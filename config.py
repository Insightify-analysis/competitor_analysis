import os
from pathlib import Path
from dotenv import load_dotenv as _load_dotenv
import json


def load_env() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        _load_dotenv(dotenv_path=env_path)
    # else, silently continue


def get_context_folder() -> Path:
    # Try env variable first
    context_path = os.getenv("CONTEXT_FOLDER")
    if context_path:
        p = Path(context_path)
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        return p

    current_dir = Path(__file__).parent
    possible_paths = [
        current_dir / "context_data",
        current_dir.parent / "context_data",
        Path("context_data"),
    ]
    for path in possible_paths:
        if path.exists():
            return path
    # Create default if not found.
    default_path = current_dir / "context_data"
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path


def get_config() -> dict:
    current_dir = Path(__file__).parent
    categories_file = current_dir / "categories.json"
    # Create a default categories file if not present
    if not categories_file.exists():
        default_categories = {"byType": {}}
        categories_file.write_text(json.dumps(default_categories, indent=2))
    return {
        "categories_file": str(categories_file),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "use_ai": os.getenv("USE_AI", "true").lower() == "true",
        "context_folder": str(get_context_folder()),
    }
