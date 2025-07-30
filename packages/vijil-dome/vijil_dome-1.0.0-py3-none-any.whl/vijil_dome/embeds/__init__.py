from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from vijil_dome.types import Sentences, Embeddings


@dataclass
class EmbeddingsItem:
    text: str
    embeddings: Optional[Embeddings] = None
    meta: Dict = field(default_factory=dict)


class AbstractEmbedder(ABC):
    @abstractmethod
    async def embeddings(self, sentences: Sentences) -> List[Embeddings]:
        pass
