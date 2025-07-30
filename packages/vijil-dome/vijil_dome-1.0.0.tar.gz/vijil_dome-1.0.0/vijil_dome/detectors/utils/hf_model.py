import logging
from abc import ABC, abstractmethod
from typing import Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from vijil_dome.detectors import DetectionMethod, DetectionResult

logger = logging.getLogger("vijil.dome")


class HFBaseModel(DetectionMethod, ABC):
    """
    Abstract base class for detection models using Hugging Face transformers.
    """

    def __init__(
        self,
        model_name: str,
        tokenizer_name: Optional[str] = None,
        local_files_only: bool = False,
        trust_remote_code: bool = False,
    ):
        logger.info(f"Initializing Hugging Face model: {model_name}...")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            local_files_only=local_files_only,
            trust_remote_code=trust_remote_code,
        )
        model_tokenizer_name = tokenizer_name or model_name
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_tokenizer_name,
            local_files_only=local_files_only,
            trust_remote_code=trust_remote_code,
        )

    @abstractmethod
    async def detect(self, query_string: str) -> DetectionResult:
        """
        Abstract method to be implemented by subclasses to execute the detection logic.

        Args:
            input (str): The input text to be analyzed by the detector.

        Returns:
            DetectionResult: A tuple containing a boolean indicating whether the input was flagged,
                             and a dictionary with additional details about the detection.
        """
        pass


class HFBaseModelWithContext(HFBaseModel):
    """
    Abstract base class for context-dependent detection models using Hugging Face transformers
    """

    def __init__(
        self,
        model_name: str,
        tokenizer_name: Optional[str] = None,
        context: Optional[str] = None,
        local_files_only: bool = False,
        trust_remote_code: bool = False,
    ):
        super().__init__(
            model_name=model_name,
            tokenizer_name=tokenizer_name,
            local_files_only=local_files_only,
            trust_remote_code=trust_remote_code,
        )
        self.context = context

    # Replace the existing context with new context
    def update_context(self, new_context: str) -> None:
        self.context = new_context

    # Add additional context to the existing context
    # If no context is present, update it instead
    def add_context(self, addition_context: str) -> None:
        if self.context is None:
            self.update_context(addition_context)
        else:
            self.context += addition_context
