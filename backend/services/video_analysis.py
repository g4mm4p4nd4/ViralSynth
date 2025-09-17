import os
from typing import List, Tuple

"""Utilities for analysing video content and persisting shot metadata."""

import os

from ..models import VideoShot
from .supabase import get_supabase_client


def _load_cv2():
    import cv2  # type: ignore

    return cv2


def _load_numpy():
    import numpy as np  # type: ignore

    return np


def _load_pytesseract():
    import pytesseract  # type: ignore

    pytesseract.pytesseract.tesseract_cmd = os.environ.get(
        "PYTESSERACT_PATH", "tesseract"
    )
    return pytesseract


def _load_scene_tools():
    from scenedetect import SceneManager, VideoManager  # type: ignore
    from scenedetect.detectors import ContentDetector  # type: ignore

    return VideoManager, SceneManager, ContentDetector

def detect_shots(video_path: str) -> list[tuple[float, float]]:
    """Return a list of (start, end) times for detected shots."""
    VideoManager, SceneManager, ContentDetector = _load_scene_tools()
    try:
        vm = VideoManager([video_path])
        sm = SceneManager()
        sm.add_detector(ContentDetector())
        vm.set_downscale_factor()
        vm.start()
        sm.detect_scenes(frame_source=vm)
        scenes = sm.get_scene_list()
        vm.release()
        return [(start.get_seconds(), end.get_seconds()) for start, end in scenes]
    except Exception:
        return []


def _frame_brightness_contrast(frame) -> tuple[float, float]:
    cv2 = _load_cv2()
    np = _load_numpy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    return brightness, contrast


def analyse_video(video_path: str):
    """Analyse a video for pacing, brightness/contrast and OCR text."""
    cv2 = _load_cv2()
    np = _load_numpy()
    pytesseract = _load_pytesseract()
    shots: list[VideoShot] = []
    try:
        shot_times = detect_shots(video_path)
        if not shot_times:
            return 0.0, 0.0, 0.0, "", shots
        cap = cv2.VideoCapture(video_path)
        texts: list[str] = []
        brightness_vals = []
        contrast_vals = []
        for start, end in shot_times:
            mid = (start + end) / 2.0
            cap.set(cv2.CAP_PROP_POS_MSEC, mid * 1000)
            ret, frame = cap.read()
            if not ret:
                continue
            brightness, contrast = _frame_brightness_contrast(frame)
            text = pytesseract.image_to_string(frame).strip()
            shots.append(
                VideoShot(
                    start_time=start,
                    end_time=end,
                    brightness=brightness,
                    contrast=contrast,
                    text=text,
                )
            )
            brightness_vals.append(brightness)
            contrast_vals.append(contrast)
            if text:
                texts.append(text)
        cap.release()
        pacing = float(np.mean([end - start for start, end in shot_times]))
        avg_brightness = float(np.mean(brightness_vals)) if brightness_vals else 0.0
        avg_contrast = float(np.mean(contrast_vals)) if contrast_vals else 0.0
        onscreen_text = " ".join(texts).strip()
        return pacing, avg_brightness, avg_contrast, onscreen_text, shots
    except Exception:
        return 0.0, 0.0, 0.0, "", []


def save_video_shots(video_id: int, shots: list[VideoShot]) -> None:
    """Persist shot metadata to Supabase."""
    supabase = get_supabase_client()
    if not supabase or not shots or video_id is None:
        return
    rows = [
        {
            "video_id": video_id,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "brightness": s.brightness,
            "contrast": s.contrast,
            "text": s.text,
        }
        for s in shots
    ]
    try:
        supabase.table("video_shots").insert(rows).execute()
    except Exception:
        pass
