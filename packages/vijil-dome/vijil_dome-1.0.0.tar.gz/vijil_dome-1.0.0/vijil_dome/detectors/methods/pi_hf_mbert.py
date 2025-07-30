import logging
import torch
from vijil_dome.detectors import (
    PI_MBERT,
    register_method,
    DetectionCategory,
    DetectionResult,
)
from transformers import pipeline
from vijil_dome.detectors.utils.hf_model import HFBaseModel

logger = logging.getLogger("vijil.dome")


@register_method(DetectionCategory.Security, PI_MBERT)
class MBertPromptInjectionModel(HFBaseModel):
    """
    Vijil Finetuned MBERT model
    """

    def __init__(self, truncation: bool = True, max_length: int = 512):
        try:
            super().__init__(
                model_name="vijil/mbert-prompt-injection",
                tokenizer_name="answerdotai/ModernBERT-base",
            )

            self.classifier = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                truncation=truncation,
                max_length=max_length,
                device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            )
            self.response_string = f"Method:{PI_MBERT}"
            self.run_in_executor = True
            logger.info("Initialized Vijil Mbert model..")
        except Exception as e:
            logger.error(f"Failed to initialize MBert model: {str(e)}")
            raise

    def sync_detect(self, query_string: str) -> DetectionResult:
        pred = self.classifier(query_string)
        flagged = bool(pred[0]["label"])  # Returns 1 if prompt injection, 0 otherwise
        return flagged, {
            "type": type(self),
            "predictions": pred,
            "response_string": self.response_string if flagged else query_string,
        }

    async def detect(self, query_string: str) -> DetectionResult:
        logger.info(f"Detecting using {self.__class__.__name__}...")
        return self.sync_detect(query_string)
