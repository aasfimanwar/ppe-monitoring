import socket
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlparse

MCAST_GROUP = "239.255.255.250"
MCAST_PORT = 3702

NAMESPACES = {
    "e": "http://www.w3.org/2003/05/soap-envelope",
    "d": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
}

PROBE_MESSAGE = """<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
            xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
            xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
  <e:Header>
    <w:MessageID>uuid:{message_id}</w:MessageID>
    <w:To e:mustUnderstand="true">urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
    <w:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
  </e:Header>
  <e:Body>
    <d:Probe>
      <d:Types>dn:NetworkVideoTransmitter</d:Types>
    </d:Probe>
  </e:Body>
</e:Envelope>"""


@dataclass
class DiscoveredDevice:
    """One ONVIF device that responded to a WS-Discovery probe. Not yet a Camera -
    no zone, no id, no video stream resolved yet."""
    xaddr: str      # the device's service address, e.g. http://192.168.1.50/onvif/device_service
    scopes: str      # raw scope string the device advertised (name/hardware hints)


def discover_devices(timeout_seconds: float = 4.0) -> List[DiscoveredDevice]:
    """Broadcast a WS-Discovery probe and collect replies for `timeout_seconds`.

    Returns an empty list if nothing responds - this is a normal, valid result
    on a network with no ONVIF devices, not an error.
    """
    message = PROBE_MESSAGE.format(message_id=uuid.uuid4())

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(timeout_seconds)

    devices: List[DiscoveredDevice] = []
    try:
        sock.sendto(message.encode("utf-8"), (MCAST_GROUP, MCAST_PORT))
        while True:
            try:
                data, _addr = sock.recvfrom(65535)
            except socket.timeout:
                break
            device = _parse_probe_match(data)
            if device:
                devices.append(device)
    finally:
        sock.close()

    return devices


def _parse_probe_match(data: bytes) -> Optional[DiscoveredDevice]:
    """Parse one ProbeMatch SOAP response into a DiscoveredDevice, or None if
    the response doesn't look like a valid ONVIF ProbeMatch."""
    try:
        root = ET.fromstring(data)
        match = root.find(".//d:ProbeMatches/d:ProbeMatch", NAMESPACES)
        if match is None:
            return None
        xaddrs_el = match.find("d:XAddrs", NAMESPACES)
        scopes_el = match.find("d:Scopes", NAMESPACES)
        if xaddrs_el is None or not xaddrs_el.text:
            return None
        first_xaddr = xaddrs_el.text.strip().split()[0]
        return DiscoveredDevice(
            xaddr=first_xaddr,
            scopes=(scopes_el.text or "").strip() if scopes_el is not None else "",
        )
    except ET.ParseError:
        return None


def resolve_stream_uri(device: DiscoveredDevice, username: str, password: str) -> str:
    """Ask a discovered device's ONVIF Media service for its RTSP stream URI.

    NOT VERIFIED - requires the onvif-zeep package and a real ONVIF camera to
    test against, neither of which is available in this development setup.
    Written to the documented ONVIF Media service pattern (GetProfiles then
    GetStreamUri) but should be treated as unproven until tested against
    actual hardware.
    """
    try:
        from onvif import ONVIFCamera
    except ImportError as exc:
        raise RuntimeError(
            "resolve_stream_uri requires the 'onvif-zeep' package "
            "(pip install onvif-zeep), which is not installed."
        ) from exc

    parsed = urlparse(device.xaddr)
    host = parsed.hostname
    port = parsed.port or 80

    camera = ONVIFCamera(host, port, username, password)
    media_service = camera.create_media_service()
    profiles = media_service.GetProfiles()
    if not profiles:
        raise RuntimeError(f"No media profiles returned by {device.xaddr}")

    stream_setup = {
        "StreamSetup": {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}},
        "ProfileToken": profiles[0].token,
    }
    response = media_service.GetStreamUri(stream_setup)
    return response.Uri