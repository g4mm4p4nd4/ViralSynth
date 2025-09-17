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

    class DummyCv2:
        COLOR_BGR2GRAY = 0
        CAP_PROP_POS_MSEC = 0

        @staticmethod
        def VideoCapture(path):
            return DummyCap()

        @staticmethod
        def cvtColor(frame, _code):
            return frame[:, :, 0]

    class DummyTesseract:
        @staticmethod
        def image_to_string(_frame):
            return "hello"

    monkeypatch.setattr(video_analysis, "_load_cv2", lambda: DummyCv2())
    monkeypatch.setattr(video_analysis, "_load_pytesseract", lambda: DummyTesseract())

    pacing, brightness, contrast, text, shots = video_analysis.analyse_video("video.mp4")

    assert pacing == 1.0
    assert text.strip() == "hello"
    assert len(shots) == 1
