from typing import List, Optional
from vijil_dome.types import Embeddings
from vijil_dome.types import Sentences
from vijil_dome.embeds import AbstractEmbedder
from vijil_dome.embeds.models import init_embedding_model


class Embedder(AbstractEmbedder):
    embedding_engine = None
    embedding_model = None

    _model = None

    def __init__(
        self,
        embedding_model: Optional[str] = None,
        embedding_engine: Optional[str] = None,
    ):
        self.embedding_engine = embedding_engine or "FastEmbed"
        self.embedding_model = embedding_model or "all-MiniLM-L6-v2"

    def _init_model(self):
        """Initialize the model used for computing the embeddings."""
        self._model = init_embedding_model(
            embedding_model=self.embedding_model, embedding_engine=self.embedding_engine
        )

    async def embeddings(self, sentences: Sentences) -> List[Embeddings]:
        """Compute embeddings for a list of texts.

        Args:
            texts (List[str]): The list of texts to compute embeddings for.

        Returns:
            List[List[float]]: The computed embeddings.
        """
        if self._model is None:
            self._init_model()
        if self._model is None:
            raise ValueError(
                "Model not found. Please provide a model to compute embeddings."
            )

        return await self._model.encode_async(sentences)
