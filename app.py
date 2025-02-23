import json
import sys
import asyncio
import logging
from pathlib import Path
from flask import Flask, request, jsonify

from file_manager import FileManager
from config import load_env
from excel_utils import load_companies_from_file
from company_domain_categorizer import DomainCategorizer

logger = logging.getLogger(__name__)


class CompanyCategorizerApp:
    def __init__(self):
        load_env()
        self.file_manager = FileManager()

        # Define default data directory
        default_data_dir = Path("D:/Programming/Insightify/data")

        # Define search paths, including the default data directory and its categories file
        current_dir = Path(__file__).parent
        search_paths = [
            default_data_dir / "categories.json",
            default_data_dir,
            current_dir / "categories.json",
            current_dir.parent / "data" / "categories.json",
            current_dir,
        ]

        # Find or create categories file
        categories_file = self.file_manager.find_categories_file(search_paths)
        if not categories_file:
            categories_file = current_dir / "categories.json"
            logger.info(f"Creating new categories file at {categories_file}")

        self.categorizer = DomainCategorizer(categories_file=str(categories_file))

    async def handle_input(self, clean_output: bool = False):
        """Handle interactive input with improved error handling"""
        try:
            while True:
                company_name = await asyncio.to_thread(
                    input, "\nEnter company name or startup idea (or 'exit' to quit): "
                )
                company_name = company_name.strip()

                if company_name.lower() in ("exit", "quit", "q"):
                    break
                if not company_name:
                    logger.warning("Empty input received")
                    continue

                try:
                    result = await self.categorizer.categorize_company(
                        company_name, clean_output=clean_output
                    )
                    print("\nCategorization results:")
                    print(json.dumps(result, indent=2))
                except Exception as e:
                    logger.error(f"Error categorizing {company_name}: {e}")

        except KeyboardInterrupt:
            logger.info("Application terminated by user")
            raise

    async def handle_file_input(self, file_path: str, clean_output: bool = False):
        try:
            companies = load_companies_from_file(file_path)
            results = {}
            for company in companies:
                results[company] = await self.categorizer.categorize_company(
                    company, clean_output=clean_output
                )
            # Return results instead of printing
            return results
        except Exception as e:
            return {"error": f"Error processing file: {e}"}

    async def run(self, file_path: str = None, clean_output: bool = False):
        if file_path:
            results = await self.handle_file_input(file_path, clean_output=clean_output)
            # New: post results if POST_URL is set, using json_poster
            from json_poster import post_json_result

            await asyncio.to_thread(post_json_result, results)
            print(json.dumps(results, indent=2))
        else:
            await self.handle_input(clean_output=clean_output)


# Added CLI entry point (removed server-related code)
async def main_cli():
    import sys

    file_arg = (
        sys.argv[1]
        if len(sys.argv) > 1
        and sys.argv[1].lower().endswith((".xlsx", ".xls", ".csv", ".json"))
        else None
    )
    # Check for a "--clean" flag
    clean_flag = "--clean" in sys.argv
    await CompanyCategorizerApp().run(file_arg, clean_output=clean_flag)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main_cli())
