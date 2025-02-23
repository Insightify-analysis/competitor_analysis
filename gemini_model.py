import os
import asyncio
import logging
import google.generativeai as genai
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class GeminiModel:
    """A wrapper class for Google's Gemini AI model with both sync and async capabilities."""

    DEFAULT_MODEL = "gemini-2.0-pro-exp-02-05"
    DEFAULT_CONFIG = {
        "temperature": 0.35,
        "top_p": 0.8,
        "top_k": 64,
        "max_output_tokens": 65536,
        "response_mime_type": "text/plain",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_MODEL,
        generation_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Gemini model.

        Args:
            api_key: Gemini API key. If None, attempts to get from environment variable.
            model_name: Name of the Gemini model to use.
            generation_config: Configuration for text generation.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided or set in GEMINI_API_KEY environment variable"
            )

        genai.configure(api_key=self.api_key)
        self.generation_config = generation_config or self.DEFAULT_CONFIG
        self.model = genai.GenerativeModel(
            model_name=model_name, generation_config=self.generation_config
        )

    async def generate(self, prompt: str, **kwargs) -> Any:
        """Generate content asynchronously with validation"""
        try:
            # Remove temperature if it exists, because generate_content_async() doesn't accept it.
            kwargs.pop("temperature", None)
            response = await self.model.generate_content_async(prompt, **kwargs)

            if not response or not hasattr(response, "text"):
                raise ValueError("Invalid response from Gemini API")

            return response

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    def generate_sync(self, prompt: str, **kwargs) -> Any:
        """
        Generate content synchronously.

        Args:
            prompt: Input text prompt
            **kwargs: Additional arguments to pass to generate_content

        Returns:
            Generated content response
        """
        kwargs.pop("temperature", None)
        return self.model.generate_content(prompt, **kwargs)

    def start_chat(self, history: Optional[List] = None) -> Any:
        """
        Start a chat session.

        Args:
            history: Optional list of previous chat messages

        Returns:
            Chat session object
        """
        return self.model.start_chat(history=history or [])

    def validate_api_key(self) -> bool:
        """Validate API key is present and valid"""
        if not self.api_key:
            raise ValueError("Missing Gemini API key")
        return True


async def main():
    """Example usage of the GeminiModel class."""
    try:
        # Initialize model
        model = GeminiModel()

        # Example of async generation
        response = await model.generate("What is the capital of France?")
        print("Async response:", response.text)

        # Example of chat session
        chat = model.start_chat()
        chat_response = chat.send_message("Tell me a fun fact about Paris.")
        print("\nChat response:", chat_response.text)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
