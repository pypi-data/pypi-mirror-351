from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROFILES_DIR = BASE_DIR / "profiles"
TEMPLATES_DIR = BASE_DIR / "templates"
BUILD_DIR = BASE_DIR / "build"
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_TEMPLATE = "default"
DEFAULT_PROFILE = "profile_default"
TEX_FNAME = "resume.tex"
TEMPLATE_FNAME = "template.j2"