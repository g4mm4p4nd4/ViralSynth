import sys
from pathlib import Path
import types

# Ensure the repository root and backend package are on the path
ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
for p in (ROOT, BACKEND):
    if str(p) not in sys.path:
        sys.path.append(str(p))

# Provide lightweight stubs for optional heavy dependencies
sys.modules.setdefault("playwright", types.ModuleType("playwright"))
playwright_async = types.ModuleType("playwright.async_api")
playwright_async.async_playwright = None
sys.modules.setdefault("playwright.async_api", playwright_async)
sys.modules.setdefault("pyppeteer", types.SimpleNamespace(launch=lambda *a, **k: None))
sys.modules.setdefault("supabase", types.SimpleNamespace(create_client=lambda *a, **k: None, Client=object))
sys.modules.setdefault("openai", types.SimpleNamespace(AsyncOpenAI=object))
pytess = types.SimpleNamespace(tesseract_cmd="tesseract", image_to_string=lambda *a, **k: "")
pytess.pytesseract = pytess
sys.modules.setdefault("pytesseract", pytess)
