from app.data.models import Camera, SourceType
from app.pipeline import DetectionPipeline

camera = Camera(
    id="cam-yard-01", name="Yard Camera",
    source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
)

pipeline = DetectionPipeline(camera)
pipeline.run_forever()