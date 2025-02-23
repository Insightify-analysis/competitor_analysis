from pathlib import Path
import json
import pandas as pd
from typing import Dict, Any


class ContextLoader:
    """Enhanced context loader with support for multiple file types"""

    @staticmethod
    def load_all_context(directory: Path) -> Dict[str, Any]:
        if not directory.is_dir():
            raise ValueError(f"Invalid context directory: {directory}")

        context = {
            "categories": {},
            "market_data": {},
            "competitors": {},
            "raw_data": {},
        }

        for file_path in directory.glob("**/*"):
            if file_path.suffix.lower() in (".json", ".xlsx", ".xls", ".csv"):
                file_context = ContextLoader.load_file(file_path)
                ContextLoader._merge_context(context, file_context)

        return context

    @staticmethod
    def _merge_context(base: Dict[str, Any], new: Dict[str, Any]) -> None:
        for key in base:
            if key in new:
                if isinstance(base[key], dict):
                    base[key].update(new[key])
                elif isinstance(base[key], list):
                    base[key].extend(new[key])

    @staticmethod
    def load_file(file_path: Path) -> Dict[str, Any]:
        suffix = file_path.suffix.lower()

        if suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        if suffix in (".xlsx", ".xls", ".csv"):
            df = (
                pd.read_csv(file_path) if suffix == ".csv" else pd.read_excel(file_path)
            )
            return ContextLoader._parse_excel(df)

        raise ValueError(f"Unsupported file type: {suffix}")

    @staticmethod
    def _parse_excel(df: pd.DataFrame) -> Dict[str, Any]:
        context = {"categories": {}, "market_data": {}, "competitors": {}}

        for col in df.columns:
            col_lower = col.lower()
            if "category" in col_lower:
                context["categories"][col] = df[col].dropna().tolist()
            elif "market" in col_lower:
                context["market_data"][col] = df[col].dropna().tolist()
            elif "competitor" in col_lower:
                context["competitors"][col] = df[col].dropna().tolist()

        return context
