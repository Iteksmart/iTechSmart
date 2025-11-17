"""
Vision Analysis Service for iTechSmart Ninja
Provides image understanding, OCR, and visual Q&A capabilities
"""

import base64
import io
from typing import Dict, Any, List, Optional, Union
from PIL import Image
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class VisionTask(Enum):
    """Types of vision tasks"""

    GENERAL_ANALYSIS = "general_analysis"
    OCR = "ocr"
    OBJECT_DETECTION = "object_detection"
    SCENE_UNDERSTANDING = "scene_understanding"
    TEXT_EXTRACTION = "text_extraction"
    CODE_DETECTION = "code_detection"
    DIAGRAM_ANALYSIS = "diagram_analysis"
    UI_ANALYSIS = "ui_analysis"
    VISUAL_QA = "visual_qa"


class VisionProvider(Enum):
    """Vision AI providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class VisionService:
    """
    Vision analysis service with multiple AI providers

    Features:
    - Image understanding and description
    - OCR (Optical Character Recognition)
    - Object detection
    - Scene understanding
    - Visual Q&A
    - Code detection in images
    - Diagram analysis
    - UI/UX analysis
    """

    def __init__(self):
        self.providers = {
            VisionProvider.OPENAI: self._analyze_with_openai,
            VisionProvider.ANTHROPIC: self._analyze_with_anthropic,
            VisionProvider.GOOGLE: self._analyze_with_google,
        }

    async def analyze_image(
        self,
        image: Union[str, bytes, Image.Image],
        task: VisionTask = VisionTask.GENERAL_ANALYSIS,
        prompt: Optional[str] = None,
        provider: VisionProvider = VisionProvider.OPENAI,
        detail_level: str = "high",
    ) -> Dict[str, Any]:
        """
        Analyze an image

        Args:
            image: Image (path, bytes, or PIL Image)
            task: Type of analysis
            prompt: Custom prompt
            provider: AI provider to use
            detail_level: Detail level (low, medium, high)

        Returns:
            Analysis results
        """
        try:
            # Prepare image
            image_data = await self._prepare_image(image)

            # Get task-specific prompt
            if not prompt:
                prompt = self._get_task_prompt(task)

            # Analyze with provider
            if provider in self.providers:
                result = await self.providers[provider](
                    image_data, prompt, detail_level
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            return {
                "success": True,
                "task": task.value,
                "provider": provider.value,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Vision analysis error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def extract_text(
        self,
        image: Union[str, bytes, Image.Image],
        provider: VisionProvider = VisionProvider.OPENAI,
    ) -> Dict[str, Any]:
        """
        Extract text from image (OCR)

        Args:
            image: Image to analyze
            provider: AI provider

        Returns:
            Extracted text
        """
        return await self.analyze_image(
            image,
            task=VisionTask.OCR,
            prompt="Extract all text from this image. Preserve formatting and structure.",
            provider=provider,
        )

    async def detect_code(
        self,
        image: Union[str, bytes, Image.Image],
        provider: VisionProvider = VisionProvider.OPENAI,
    ) -> Dict[str, Any]:
        """
        Detect and extract code from image

        Args:
            image: Image containing code
            provider: AI provider

        Returns:
            Detected code
        """
        return await self.analyze_image(
            image,
            task=VisionTask.CODE_DETECTION,
            prompt="Extract all code from this image. Identify the programming language and preserve exact formatting.",
            provider=provider,
        )

    async def analyze_diagram(
        self,
        image: Union[str, bytes, Image.Image],
        provider: VisionProvider = VisionProvider.OPENAI,
    ) -> Dict[str, Any]:
        """
        Analyze diagram or flowchart

        Args:
            image: Diagram image
            provider: AI provider

        Returns:
            Diagram analysis
        """
        return await self.analyze_image(
            image,
            task=VisionTask.DIAGRAM_ANALYSIS,
            prompt="Analyze this diagram. Describe its structure, components, relationships, and purpose.",
            provider=provider,
        )

    async def analyze_ui(
        self,
        image: Union[str, bytes, Image.Image],
        provider: VisionProvider = VisionProvider.OPENAI,
    ) -> Dict[str, Any]:
        """
        Analyze UI/UX design

        Args:
            image: UI screenshot
            provider: AI provider

        Returns:
            UI analysis
        """
        return await self.analyze_image(
            image,
            task=VisionTask.UI_ANALYSIS,
            prompt="Analyze this UI design. Describe layout, components, color scheme, typography, and provide UX feedback.",
            provider=provider,
        )

    async def visual_qa(
        self,
        image: Union[str, bytes, Image.Image],
        question: str,
        provider: VisionProvider = VisionProvider.OPENAI,
    ) -> Dict[str, Any]:
        """
        Answer questions about an image

        Args:
            image: Image to analyze
            question: Question to answer
            provider: AI provider

        Returns:
            Answer
        """
        return await self.analyze_image(
            image,
            task=VisionTask.VISUAL_QA,
            prompt=f"Answer this question about the image: {question}",
            provider=provider,
        )

    async def compare_images(
        self,
        image1: Union[str, bytes, Image.Image],
        image2: Union[str, bytes, Image.Image],
        provider: VisionProvider = VisionProvider.OPENAI,
    ) -> Dict[str, Any]:
        """
        Compare two images

        Args:
            image1: First image
            image2: Second image
            provider: AI provider

        Returns:
            Comparison results
        """
        # Analyze both images
        result1 = await self.analyze_image(image1, provider=provider)
        result2 = await self.analyze_image(image2, provider=provider)

        return {
            "success": True,
            "image1_analysis": result1,
            "image2_analysis": result2,
            "comparison": "Images analyzed separately. Use visual_qa for detailed comparison.",
        }

    async def batch_analyze(
        self,
        images: List[Union[str, bytes, Image.Image]],
        task: VisionTask = VisionTask.GENERAL_ANALYSIS,
        provider: VisionProvider = VisionProvider.OPENAI,
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple images

        Args:
            images: List of images
            task: Analysis task
            provider: AI provider

        Returns:
            List of analysis results
        """
        results = []
        for i, image in enumerate(images):
            result = await self.analyze_image(image, task=task, provider=provider)
            result["image_index"] = i
            results.append(result)

        return results

    async def _prepare_image(self, image: Union[str, bytes, Image.Image]) -> str:
        """Prepare image for analysis"""
        if isinstance(image, str):
            # File path or URL
            if image.startswith(("http://", "https://")):
                return image  # URL
            else:
                # Read file
                with open(image, "rb") as f:
                    image_bytes = f.read()
                return base64.b64encode(image_bytes).decode("utf-8")

        elif isinstance(image, bytes):
            # Raw bytes
            return base64.b64encode(image).decode("utf-8")

        elif isinstance(image, Image.Image):
            # PIL Image
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            return base64.b64encode(image_bytes).decode("utf-8")

        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

    def _get_task_prompt(self, task: VisionTask) -> str:
        """Get prompt for specific task"""
        prompts = {
            VisionTask.GENERAL_ANALYSIS: "Analyze this image in detail. Describe what you see, including objects, people, text, colors, and overall composition.",
            VisionTask.OCR: "Extract all text from this image. Preserve formatting and structure.",
            VisionTask.OBJECT_DETECTION: "Identify and list all objects in this image with their locations.",
            VisionTask.SCENE_UNDERSTANDING: "Describe the scene in this image. What is happening? What is the context?",
            VisionTask.TEXT_EXTRACTION: "Extract all text from this image, including any visible text in signs, documents, or UI elements.",
            VisionTask.CODE_DETECTION: "Extract all code from this image. Identify the programming language and preserve exact formatting.",
            VisionTask.DIAGRAM_ANALYSIS: "Analyze this diagram. Describe its structure, components, relationships, and purpose.",
            VisionTask.UI_ANALYSIS: "Analyze this UI design. Describe layout, components, color scheme, typography, and provide UX feedback.",
            VisionTask.VISUAL_QA: "Answer questions about this image based on what you see.",
        }
        return prompts.get(task, prompts[VisionTask.GENERAL_ANALYSIS])

    async def _analyze_with_openai(
        self, image_data: str, prompt: str, detail_level: str
    ) -> Dict[str, Any]:
        """Analyze with OpenAI Vision"""
        try:
            # Import OpenAI client
            from openai import AsyncOpenAI
            import os

            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Prepare message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}",
                                "detail": detail_level,
                            },
                        },
                    ],
                }
            ]

            # Call API
            response = await client.chat.completions.create(
                model="gpt-4o", messages=messages, max_tokens=1000
            )

            return {
                "description": response.choices[0].message.content,
                "model": "gpt-4o",
                "tokens_used": response.usage.total_tokens,
            }

        except Exception as e:
            logger.error(f"OpenAI vision error: {str(e)}")
            raise

    async def _analyze_with_anthropic(
        self, image_data: str, prompt: str, detail_level: str
    ) -> Dict[str, Any]:
        """Analyze with Anthropic Claude"""
        try:
            # Import Anthropic client
            from anthropic import AsyncAnthropic
            import os

            client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

            # Call API
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )

            return {
                "description": response.content[0].text,
                "model": "claude-3-5-sonnet",
                "tokens_used": response.usage.input_tokens
                + response.usage.output_tokens,
            }

        except Exception as e:
            logger.error(f"Anthropic vision error: {str(e)}")
            raise

    async def _analyze_with_google(
        self, image_data: str, prompt: str, detail_level: str
    ) -> Dict[str, Any]:
        """Analyze with Google Gemini"""
        try:
            # Import Google client
            import google.generativeai as genai
            import os

            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

            # Decode base64 image
            import base64

            image_bytes = base64.b64decode(image_data)

            # Create PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Call API
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = await model.generate_content_async([prompt, image])

            return {
                "description": response.text,
                "model": "gemini-1.5-pro",
                "tokens_used": None,  # Gemini doesn't provide token count
            }

        except Exception as e:
            logger.error(f"Google vision error: {str(e)}")
            raise


# Global vision service instance
vision_service = VisionService()
