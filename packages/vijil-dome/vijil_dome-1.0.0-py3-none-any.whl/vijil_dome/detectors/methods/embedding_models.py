from vijil_dome.detectors.utils.embeddings_base import BaseEmbeddingsDetector
from vijil_dome.detectors import (
    register_method,
    DetectionCategory,
    DetectionResult,
    SECURITY_EMBEDDINGS,
)
import os


@register_method(DetectionCategory.Security, SECURITY_EMBEDDINGS)
class JailbreakEmbeddingsDetector(BaseEmbeddingsDetector):
    def __init__(
        self,
        engine: str = "SentenceTransformers",
        model: str = "all-MiniLM-L6-v2",
        threshold: float = 0.7,
        in_mem: bool = True,
    ):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        jb_file = os.path.join(
            module_dir,
            "configs",
            "embedding_files",
            "jailbreak",
            "garak_inthewild_jailbreak.raw.txt",
        )
        super().__init__(SECURITY_EMBEDDINGS, jb_file, engine, model, threshold, in_mem)

    async def detect(self, query_string: str) -> DetectionResult:
        result = await super().detect(query_string)
        return result
