import multiprocessing
import signal
import sys

from app.data.models import Camera, SourceType


def run_api():
    from app.api.app import create_app
    app = create_app()
    app.run(port=5000, use_reloader=False)


def run_pipeline():
    from app.pipeline import DetectionPipeline

    camera = Camera(
        id="cam-yard-01", name="Yard Camera",
        source_type=SourceType.WEBCAM, source_uri="0", zone="yard",
    )
    pipeline = DetectionPipeline(camera)
    pipeline.run_forever()


def main():
    api_process = multiprocessing.Process(target=run_api, name="api")
    pipeline_process = multiprocessing.Process(target=run_pipeline, name="pipeline")

    api_process.start()
    pipeline_process.start()

    print("SneakySafety running - API on http://127.0.0.1:5000 - Ctrl+C to stop everything")

    def handle_shutdown(signum, frame):
        print("\nStopping...")
        pipeline_process.terminate()
        api_process.terminate()
        pipeline_process.join()
        api_process.join()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)

    api_process.join()
    pipeline_process.join()


if __name__ == "__main__":
    main()