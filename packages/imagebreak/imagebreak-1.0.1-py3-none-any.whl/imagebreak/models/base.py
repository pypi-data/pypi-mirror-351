"""Base model interface for ImageBreak framework."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from PIL import Image

from ..types import ModelResponse, ModelType, ResponseStatus


class BaseModel(ABC):
    """Abstract base class for all model implementations."""
    
    def __init__(self, model_name: str = "unknown", model_type: ModelType = ModelType.TEXT_GENERATION):
        """
        Initialize the base model.
        
        Args:
            model_name: Name of the model
            model_type: Type of model (text, image, multimodal)
        """
        self.model_name = model_name
        self.model_type = model_type
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> ModelResponse:
        """
        Generate text response from a prompt.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional model-specific parameters
            
        Returns:
            ModelResponse containing the generated text and metadata
        """
        pass
    
    def generate_image(self, prompt: str, **kwargs) -> ModelResponse:
        """
        Generate image from a prompt.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional model-specific parameters
            
        Returns:
            ModelResponse containing image URL/path and metadata
        """
        return ModelResponse(
            status=ResponseStatus.ERROR,
            error_message="Image generation not supported by this model"
        )
    
    def analyze_image(
        self,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        image_pil: Optional[Image.Image] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Analyze an image and provide description/analysis.
        
        Args:
            image_path: Path to local image file
            image_url: URL of image to analyze
            image_pil: PIL Image object
            **kwargs: Additional model-specific parameters
            
        Returns:
            ModelResponse containing image analysis and metadata
        """
        return ModelResponse(
            status=ResponseStatus.ERROR,
            error_message="Image analysis not supported by this model"
        )
    
    def supports_image_generation(self) -> bool:
        """Check if the model supports image generation."""
        return self.model_type in [ModelType.IMAGE_GENERATION, ModelType.MULTIMODAL]
    
    def supports_text_generation(self) -> bool:
        """Check if the model supports text generation."""
        return self.model_type in [ModelType.TEXT_GENERATION, ModelType.MULTIMODAL]
    
    def supports_image_analysis(self) -> bool:
        """Check if the model supports image analysis."""
        return False  # Override in subclasses that support it
    
    def validate_prompt(self, prompt: str, max_length: int = 4000) -> bool:
        """
        Validate a prompt for basic safety and length constraints.
        
        Args:
            prompt: The prompt to validate
            max_length: Maximum allowed prompt length
            
        Returns:
            True if prompt is valid, False otherwise
        """
        if not prompt or not prompt.strip():
            self.logger.warning("Empty prompt provided")
            return False
            
        if len(prompt) > max_length:
            self.logger.warning(f"Prompt too long: {len(prompt)} > {max_length}")
            return False
            
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "supports_text": self.supports_text_generation(),
            "supports_image": self.supports_image_generation(),
            "supports_analysis": self.supports_image_analysis(),
        }
    
    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}(model_name='{self.model_name}', type='{self.model_type.value}')"
    
    def __repr__(self) -> str:
        """Detailed representation of the model."""
        return self.__str__() 