import json
import logging
from pathlib import Path
from typing import Union, Dict, Optional

logger = logging.getLogger(__name__)


class FileManager:
    """Handles file operations for the categorizer"""

    @staticmethod
    def find_categories_file(search_paths: list[Path]) -> Optional[Path]:
        """Search for categories file in multiple locations"""
        for path in search_paths:
            if path.is_file() and path.suffix == ".json":
                return path
            if path.is_dir():
                json_file = path / "categories.json"
                if json_file.exists():
                    return json_file
        return None

    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Dict:
        """Load and validate JSON file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("JSON file must contain an object")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except OSError as e:
            raise OSError(f"Error reading file {file_path}: {e}")

    @staticmethod
    def create_default_categories(file_path: Union[str, Path]) -> Dict:
        """Create default categories file"""
        default_categories = {
            "byType": {
                "Technology": {
                    "lists": ["Software", "Hardware", "Cloud Computing"],
                    "mainArticle": "Technology company",
                }
            }
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_categories, f, indent=2)

        return default_categories
