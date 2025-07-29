from pathlib import Path
from starlette.templating import Jinja2Templates
from datetime import datetime
from backend.config.i18n import SUPPORTED_LANGUAGES

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "backend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["supported_languages"] = SUPPORTED_LANGUAGES
templates.env.globals['now'] = datetime.now 