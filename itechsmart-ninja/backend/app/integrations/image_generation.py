"""
Image Generation Client - Multi-provider AI image generation
Supports FLUX, DALL-E, Imagen, Stable Diffusion, and more
"""

from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import requests
import base64
from io import BytesIO
from PIL import Image
import logging
import os

logger = logging.getLogger(__name__)


class ImageProvider(str, Enum):
    """Supported image generation providers"""

    FLUX = "flux"
    DALLE = "dalle"
    IMAGEN = "imagen"
    STABLE_DIFFUSION = "stable_diffusion"
    REPLICATE = "replicate"


class ImageSize(str, Enum):
    """Standard image sizes"""

    SQUARE_256 = "256x256"
    SQUARE_512 = "512x512"
    SQUARE_1024 = "1024x1024"
    PORTRAIT_512_768 = "512x768"
    PORTRAIT_768_1024 = "768x1024"
    LANDSCAPE_768_512 = "768x512"
    LANDSCAPE_1024_768 = "1024x768"
    WIDE_1024_576 = "1024x576"
    TALL_576_1024 = "576x1024"


class ImageStyle(str, Enum):
    """Image generation styles"""

    NATURAL = "natural"
    VIVID = "vivid"
    ARTISTIC = "artistic"
    PHOTOREALISTIC = "photorealistic"
    ANIME = "anime"
    DIGITAL_ART = "digital_art"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    SKETCH = "sketch"
    CARTOON = "cartoon"


class ImageQuality(str, Enum):
    """Image quality levels"""

    STANDARD = "standard"
    HD = "hd"
    ULTRA = "ultra"


class ImageGenerationClient:
    """
    Unified image generation client supporting multiple providers

    Providers:
    - FLUX: High-quality image generation
    - DALL-E: OpenAI's image generation
    - Imagen: Google's image generation
    - Stable Diffusion: Open-source generation
    - Replicate: Various models via Replicate API

    Features:
    - Text-to-image generation
    - Image-to-image generation
    - Image editing (inpainting, outpainting)
    - Image variations
    - Style transfer
    - Upscaling
    - Background removal
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        replicate_api_key: Optional[str] = None,
        stability_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
    ):
        """
        Initialize image generation client

        Args:
            openai_api_key: OpenAI API key (for DALL-E)
            replicate_api_key: Replicate API key (for FLUX, Stable Diffusion)
            stability_api_key: Stability AI API key
            google_api_key: Google API key (for Imagen)
        """
        self.openai_api_key = openai_api_key
        self.replicate_api_key = replicate_api_key
        self.stability_api_key = stability_api_key
        self.google_api_key = google_api_key

        # Provider availability
        self.providers_available = {
            ImageProvider.DALLE: bool(openai_api_key),
            ImageProvider.FLUX: bool(replicate_api_key),
            ImageProvider.STABLE_DIFFUSION: bool(
                replicate_api_key or stability_api_key
            ),
            ImageProvider.IMAGEN: bool(google_api_key),
            ImageProvider.REPLICATE: bool(replicate_api_key),
        }

    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [
            provider.value
            for provider, available in self.providers_available.items()
            if available
        ]

    # ========================================================================
    # TEXT-TO-IMAGE GENERATION
    # ========================================================================

    def generate_image(
        self,
        prompt: str,
        provider: ImageProvider = ImageProvider.DALLE,
        size: ImageSize = ImageSize.SQUARE_1024,
        style: Optional[ImageStyle] = None,
        quality: ImageQuality = ImageQuality.STANDARD,
        n: int = 1,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate images from text prompt

        Args:
            prompt: Text description of desired image
            provider: Image generation provider
            size: Image size
            style: Image style
            quality: Image quality
            n: Number of images to generate
            negative_prompt: What to avoid in image
            seed: Random seed for reproducibility

        Returns:
            List of generated images with metadata
        """
        if not self.providers_available.get(provider):
            raise Exception(
                f"Provider {provider} not available. Please configure API key."
            )

        if provider == ImageProvider.DALLE:
            return self._generate_dalle(prompt, size, style, quality, n)
        elif provider == ImageProvider.FLUX:
            return self._generate_flux(prompt, size, style, n, negative_prompt, seed)
        elif provider == ImageProvider.STABLE_DIFFUSION:
            return self._generate_stable_diffusion(
                prompt, size, style, n, negative_prompt, seed
            )
        elif provider == ImageProvider.IMAGEN:
            return self._generate_imagen(prompt, size, n)
        else:
            raise Exception(f"Provider {provider} not implemented")

    def _generate_dalle(
        self,
        prompt: str,
        size: ImageSize,
        style: Optional[ImageStyle],
        quality: ImageQuality,
        n: int,
    ) -> List[Dict[str, Any]]:
        """Generate images using DALL-E"""
        try:
            import openai

            client = openai.OpenAI(api_key=self.openai_api_key)

            # Map size to DALL-E format
            dalle_size = (
                size.value
                if size.value in ["256x256", "512x512", "1024x1024"]
                else "1024x1024"
            )

            # Map style
            dalle_style = "vivid" if style == ImageStyle.VIVID else "natural"

            response = client.images.generate(
                model="dall-e-3" if quality == ImageQuality.HD else "dall-e-2",
                prompt=prompt,
                size=dalle_size,
                quality=quality.value,
                style=dalle_style,
                n=n,
            )

            results = []
            for image in response.data:
                results.append(
                    {
                        "url": image.url,
                        "revised_prompt": getattr(image, "revised_prompt", None),
                        "provider": "dalle",
                        "size": dalle_size,
                        "quality": quality.value,
                    }
                )

            return results

        except Exception as e:
            logger.error(f"DALL-E generation failed: {e}")
            raise Exception(f"DALL-E generation failed: {str(e)}")

    def _generate_flux(
        self,
        prompt: str,
        size: ImageSize,
        style: Optional[ImageStyle],
        n: int,
        negative_prompt: Optional[str],
        seed: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Generate images using FLUX via Replicate"""
        try:
            import replicate

            # Parse size
            width, height = map(int, size.value.split("x"))

            # Build input
            input_data = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": n,
                "output_format": "png",
                "output_quality": 90,
            }

            if negative_prompt:
                input_data["negative_prompt"] = negative_prompt
            if seed:
                input_data["seed"] = seed

            # Run FLUX model
            output = replicate.run("black-forest-labs/flux-schnell", input=input_data)

            results = []
            for i, image_url in enumerate(output):
                results.append(
                    {
                        "url": image_url,
                        "provider": "flux",
                        "size": size.value,
                        "seed": seed,
                        "index": i,
                    }
                )

            return results

        except Exception as e:
            logger.error(f"FLUX generation failed: {e}")
            raise Exception(f"FLUX generation failed: {str(e)}")

    def _generate_stable_diffusion(
        self,
        prompt: str,
        size: ImageSize,
        style: Optional[ImageStyle],
        n: int,
        negative_prompt: Optional[str],
        seed: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Generate images using Stable Diffusion"""
        try:
            if self.replicate_api_key:
                return self._generate_sd_replicate(
                    prompt, size, n, negative_prompt, seed
                )
            elif self.stability_api_key:
                return self._generate_sd_stability(
                    prompt, size, n, negative_prompt, seed
                )
            else:
                raise Exception("No API key available for Stable Diffusion")

        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {e}")
            raise Exception(f"Stable Diffusion generation failed: {str(e)}")

    def _generate_sd_replicate(
        self,
        prompt: str,
        size: ImageSize,
        n: int,
        negative_prompt: Optional[str],
        seed: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Generate using Stable Diffusion via Replicate"""
        import replicate

        width, height = map(int, size.value.split("x"))

        input_data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_outputs": n,
        }

        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt
        if seed:
            input_data["seed"] = seed

        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input=input_data,
        )

        results = []
        for i, image_url in enumerate(output):
            results.append(
                {
                    "url": image_url,
                    "provider": "stable_diffusion",
                    "size": size.value,
                    "seed": seed,
                    "index": i,
                }
            )

        return results

    def _generate_sd_stability(
        self,
        prompt: str,
        size: ImageSize,
        n: int,
        negative_prompt: Optional[str],
        seed: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Generate using Stability AI API"""
        width, height = map(int, size.value.split("x"))

        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": n,
            "steps": 30,
        }

        if negative_prompt:
            data["text_prompts"].append({"text": negative_prompt, "weight": -1})
        if seed:
            data["seed"] = seed

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        results = []
        for i, artifact in enumerate(response.json()["artifacts"]):
            image_data = base64.b64decode(artifact["base64"])
            results.append(
                {
                    "data": image_data,
                    "provider": "stable_diffusion",
                    "size": size.value,
                    "seed": artifact.get("seed"),
                    "index": i,
                }
            )

        return results

    def _generate_imagen(
        self, prompt: str, size: ImageSize, n: int
    ) -> List[Dict[str, Any]]:
        """Generate images using Google Imagen"""
        # Note: Imagen API implementation would go here
        # This is a placeholder as Imagen API access is limited
        raise NotImplementedError("Imagen integration coming soon")

    # ========================================================================
    # IMAGE-TO-IMAGE GENERATION
    # ========================================================================

    def image_to_image(
        self,
        image: Image.Image,
        prompt: str,
        provider: ImageProvider = ImageProvider.STABLE_DIFFUSION,
        strength: float = 0.8,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate new image based on input image and prompt

        Args:
            image: Input image
            prompt: Text description of desired changes
            provider: Image generation provider
            strength: How much to transform (0.0-1.0)
            negative_prompt: What to avoid
            seed: Random seed

        Returns:
            List of generated images
        """
        if provider == ImageProvider.STABLE_DIFFUSION:
            return self._image_to_image_sd(
                image, prompt, strength, negative_prompt, seed
            )
        else:
            raise Exception(f"Image-to-image not supported for {provider}")

    def _image_to_image_sd(
        self,
        image: Image.Image,
        prompt: str,
        strength: float,
        negative_prompt: Optional[str],
        seed: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Image-to-image using Stable Diffusion"""
        import replicate

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_data = base64.b64encode(buffered.getvalue()).decode()

        input_data = {
            "image": f"data:image/png;base64,{image_data}",
            "prompt": prompt,
            "prompt_strength": strength,
        }

        if negative_prompt:
            input_data["negative_prompt"] = negative_prompt
        if seed:
            input_data["seed"] = seed

        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input=input_data,
        )

        results = []
        for i, image_url in enumerate(output):
            results.append(
                {
                    "url": image_url,
                    "provider": "stable_diffusion",
                    "type": "image_to_image",
                    "strength": strength,
                    "index": i,
                }
            )

        return results

    # ========================================================================
    # IMAGE EDITING
    # ========================================================================

    def inpaint(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
        provider: ImageProvider = ImageProvider.DALLE,
    ) -> List[Dict[str, Any]]:
        """
        Fill masked area of image based on prompt

        Args:
            image: Original image
            mask: Mask image (white = fill, black = keep)
            prompt: Description of what to fill
            provider: Image generation provider

        Returns:
            List of edited images
        """
        if provider == ImageProvider.DALLE:
            return self._inpaint_dalle(image, mask, prompt)
        else:
            raise Exception(f"Inpainting not supported for {provider}")

    def _inpaint_dalle(
        self, image: Image.Image, mask: Image.Image, prompt: str
    ) -> List[Dict[str, Any]]:
        """Inpaint using DALL-E"""
        import openai

        client = openai.OpenAI(api_key=self.openai_api_key)

        # Convert images to bytes
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        mask_bytes = BytesIO()
        mask.save(mask_bytes, format="PNG")
        mask_bytes.seek(0)

        response = client.images.edit(
            model="dall-e-2",
            image=image_bytes,
            mask=mask_bytes,
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

        results = []
        for img in response.data:
            results.append({"url": img.url, "provider": "dalle", "type": "inpaint"})

        return results

    def create_variation(
        self,
        image: Image.Image,
        provider: ImageProvider = ImageProvider.DALLE,
        n: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Create variations of an image

        Args:
            image: Input image
            provider: Image generation provider
            n: Number of variations

        Returns:
            List of variation images
        """
        if provider == ImageProvider.DALLE:
            return self._variation_dalle(image, n)
        else:
            raise Exception(f"Variations not supported for {provider}")

    def _variation_dalle(self, image: Image.Image, n: int) -> List[Dict[str, Any]]:
        """Create variations using DALL-E"""
        import openai

        client = openai.OpenAI(api_key=self.openai_api_key)

        # Convert image to bytes
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        response = client.images.create_variation(
            model="dall-e-2", image=image_bytes, n=n, size="1024x1024"
        )

        results = []
        for i, img in enumerate(response.data):
            results.append(
                {"url": img.url, "provider": "dalle", "type": "variation", "index": i}
            )

        return results

    # ========================================================================
    # IMAGE ENHANCEMENT
    # ========================================================================

    def upscale(
        self, image: Image.Image, scale: int = 2, provider: str = "replicate"
    ) -> Dict[str, Any]:
        """
        Upscale image resolution

        Args:
            image: Input image
            scale: Upscale factor (2 or 4)
            provider: Upscaling provider

        Returns:
            Upscaled image data
        """
        if provider == "replicate":
            return self._upscale_replicate(image, scale)
        else:
            raise Exception(f"Upscaling not supported for {provider}")

    def _upscale_replicate(self, image: Image.Image, scale: int) -> Dict[str, Any]:
        """Upscale using Replicate"""
        import replicate

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_data = base64.b64encode(buffered.getvalue()).decode()

        output = replicate.run(
            "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
            input={
                "image": f"data:image/png;base64,{image_data}",
                "scale": scale,
                "face_enhance": False,
            },
        )

        return {
            "url": output,
            "provider": "replicate",
            "type": "upscale",
            "scale": scale,
        }

    def remove_background(self, image: Image.Image) -> Dict[str, Any]:
        """
        Remove background from image

        Args:
            image: Input image

        Returns:
            Image with background removed
        """
        import replicate

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_data = base64.b64encode(buffered.getvalue()).decode()

        output = replicate.run(
            "cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",
            input={"image": f"data:image/png;base64,{image_data}"},
        )

        return {"url": output, "provider": "replicate", "type": "background_removal"}

    def enhance_face(self, image: Image.Image) -> Dict[str, Any]:
        """
        Enhance/restore faces in image

        Args:
            image: Input image

        Returns:
            Image with enhanced faces
        """
        import replicate

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_data = base64.b64encode(buffered.getvalue()).decode()

        output = replicate.run(
            "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3",
            input={
                "img": f"data:image/png;base64,{image_data}",
                "version": "v1.4",
                "scale": 2,
            },
        )

        return {"url": output, "provider": "replicate", "type": "face_enhancement"}

    # ========================================================================
    # STYLE TRANSFER
    # ========================================================================

    def apply_style(
        self, image: Image.Image, style: str, strength: float = 0.8
    ) -> Dict[str, Any]:
        """
        Apply artistic style to image

        Args:
            image: Input image
            style: Style to apply
            strength: Style strength (0.0-1.0)

        Returns:
            Styled image
        """
        # This would integrate with style transfer models
        raise NotImplementedError("Style transfer coming soon")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def download_image(self, url: str) -> Image.Image:
        """Download image from URL"""
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))

    def save_image(self, image: Image.Image, path: str):
        """Save image to file"""
        image.save(path)

    def image_to_base64(self, image: Image.Image) -> str:
        """Convert image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def base64_to_image(self, base64_str: str) -> Image.Image:
        """Convert base64 string to image"""
        image_data = base64.b64decode(base64_str)
        return Image.open(BytesIO(image_data))
