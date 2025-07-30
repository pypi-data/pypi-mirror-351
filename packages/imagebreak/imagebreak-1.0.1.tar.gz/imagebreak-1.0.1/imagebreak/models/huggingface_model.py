"""HuggingFace model implementation for image analysis."""

import logging
import json
from typing import Optional, Dict, Any
from PIL import Image

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from transformers import pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .base import BaseModel
from ..types import ModelResponse, ResponseStatus


class HuggingFaceImageAnalyzer(BaseModel):
    """HuggingFace model for image analysis using vision-language models."""
    
    def __init__(
        self,
        model_name: str = "Salesforce/blip2-opt-2.7b",
        device: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize HuggingFace image analyzer.
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to run model on ('cpu', 'cuda', etc.)
            **kwargs: Additional model parameters
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers library is required. Install with: pip install transformers torch")
            
        super().__init__(model_name=model_name, **kwargs)
        
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None
        self.vision_pipeline = None
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the vision-language model."""
        try:
            self.logger.info(f"Loading HuggingFace model: {self.model_name}")
            
            if "blip" in self.model_name.lower():
                # Use BLIP for image captioning
                self.processor = BlipProcessor.from_pretrained(self.model_name)
                self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
                self.model.to(self.device)
                
            else:
                # Try using a generic vision pipeline
                self.vision_pipeline = pipeline(
                    "image-to-text",
                    model=self.model_name,
                    device=0 if self.device == "cuda" else -1
                )
                
            self.logger.info(f"Model loaded successfully on device: {self.device}")
            
        except Exception as e:
            self.logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def supports_image_generation(self) -> bool:
        """Check if model supports image generation."""
        return False
    
    def supports_text_generation(self) -> bool:
        """Check if model supports text generation."""
        return True
    
    def supports_image_analysis(self) -> bool:
        """Check if model supports image analysis."""
        return True
    
    def analyze_image(
        self,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        image_pil: Optional[Image.Image] = None,
        prompt: str = "Describe this image in detail, including any concerning or inappropriate content:",
        **kwargs
    ) -> ModelResponse:
        """
        Analyze an image and provide detailed description.
        
        Args:
            image_path: Path to local image file
            image_url: URL of image to analyze
            image_pil: PIL Image object
            prompt: Analysis prompt
            **kwargs: Additional parameters
            
        Returns:
            ModelResponse with image analysis
        """
        try:
            # Load image
            if image_pil:
                image = image_pil
            elif image_path:
                image = Image.open(image_path).convert('RGB')
            elif image_url:
                import requests
                from io import BytesIO
                response = requests.get(image_url)
                image = Image.open(BytesIO(response.content)).convert('RGB')
            else:
                return ModelResponse(
                    status=ResponseStatus.ERROR,
                    error_message="No image provided for analysis"
                )
            
            # Analyze image
            if self.processor and self.model:
                # Use BLIP model
                inputs = self.processor(image, prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    out = self.model.generate(
                        **inputs,
                        max_length=kwargs.get('max_length', 200),
                        num_beams=kwargs.get('num_beams', 5),
                        temperature=kwargs.get('temperature', 0.7)
                    )
                
                description = self.processor.decode(out[0], skip_special_tokens=True)
                
            elif self.vision_pipeline:
                # Use generic pipeline
                result = self.vision_pipeline(image)
                description = result[0]['generated_text'] if result else "Unable to analyze image"
                
            else:
                return ModelResponse(
                    status=ResponseStatus.ERROR,
                    error_message="No model available for image analysis"
                )
            
            # Analyze content and assign quality score
            quality_score = self._assess_image_quality(description, kwargs.get('original_prompt', ''))
            
            analysis_result = {
                "description": description,
                "quality_score": quality_score,
                "analysis_prompt": prompt,
                "model_used": self.model_name,
                "device": self.device
            }
            
            return ModelResponse(
                status=ResponseStatus.SUCCESS,
                content=analysis_result,
                metadata={
                    "analysis_type": "huggingface_vision",
                    "quality_score": quality_score
                }
            )
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            return ModelResponse(
                status=ResponseStatus.ERROR,
                error_message=str(e)
            )
    
    def _assess_image_quality(self, description: str, original_prompt: str = "") -> float:
        """
        Assess image quality based on description and original prompt.
        
        Args:
            description: Generated image description
            original_prompt: Original prompt used for generation
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            # Simple heuristic-based quality assessment
            quality_indicators = {
                "detailed": 0.2,
                "clear": 0.15,
                "realistic": 0.15,
                "accurate": 0.15,
                "high-quality": 0.1,
                "professional": 0.1,
                "vivid": 0.05,
                "sharp": 0.05,
                "well-lit": 0.05
            }
            
            negative_indicators = {
                "blurry": -0.2,
                "unclear": -0.15,
                "distorted": -0.15,
                "low-quality": -0.1,
                "pixelated": -0.1,
                "dark": -0.05,
                "grainy": -0.05
            }
            
            description_lower = description.lower()
            score = 0.5  # Base score
            
            # Add points for quality indicators
            for indicator, weight in quality_indicators.items():
                if indicator in description_lower:
                    score += weight
            
            # Subtract points for negative indicators
            for indicator, weight in negative_indicators.items():
                if indicator in description_lower:
                    score += weight  # weight is negative
            
            # Bonus for length (more detailed descriptions)
            if len(description) > 100:
                score += 0.1
            elif len(description) > 200:
                score += 0.2
            
            # Bonus for matching original prompt keywords (if available)
            if original_prompt:
                prompt_words = set(original_prompt.lower().split())
                desc_words = set(description.lower().split())
                overlap = len(prompt_words.intersection(desc_words)) / len(prompt_words) if prompt_words else 0
                score += overlap * 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return 0.5  # Default middle score
    
    def generate_text(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate text response (not supported by this model)."""
        return ModelResponse(
            status=ResponseStatus.ERROR,
            error_message="Text generation not supported by image analysis model"
        )
    
    def generate_image(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate image (not supported by this model)."""
        return ModelResponse(
            status=ResponseStatus.ERROR,
            error_message="Image generation not supported by image analysis model"
        ) 