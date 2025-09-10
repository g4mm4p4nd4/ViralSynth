import numpy as np
from backend.services import video_analysis


def test_analyse_video(monkeypatch):
    # Mock shot detection
    monkeypatch.setattr(video_analysis, "detect_shots", lambda path: [(0.0, 1.0)])

    # Mock VideoCapture to return a simple black frame
    class DummyCap:
        def set(self, *args, **kwargs):
            pass

        def read(self):
            frame = np.zeros((10, 10, 3), dtype=np.uint8)
            return True, frame

        def release(self):
            pass

    monkeypatch.setattr(video_analysis.cv2, "VideoCapture", lambda path: DummyCap())
    monkeypatch.setattr(video_analysis.pytesseract, "image_to_string", lambda frame: "hello")

    pacing, brightness, contrast, text, shots = video_analysis.analyse_video("video.mp4")

    assert pacing == 1.0
    assert text.strip() == "hello"
    assert len(shots) == 1
