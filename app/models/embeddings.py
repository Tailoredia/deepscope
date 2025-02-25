import torch
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

class EmbeddingModelRegistry:
    """Registry to manage multiple embedding models"""

    def __init__(self):
        self._models: Dict[str, BaseEmbeddingModel] = {}

    def register_model(self, model_id: str, model: 'BaseEmbeddingModel'):
        """Register a new embedding model"""
        self._models[model_id] = model

    def get_model(self, model_id: str) -> 'BaseEmbeddingModel':
        """Get a registered model by ID"""
        if model_id not in self._models:
            raise KeyError(f"Model {model_id} not registered")
        return self._models[model_id]

    def list_models(self) -> List[str]:
        """List all registered model IDs"""
        return list(self._models.keys())

class BaseEmbeddingModel:
    """Base class for embedding models"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.cache = {}

    def get_embeddings(self, texts: List[str], batch_size: int) -> np.ndarray:
        """Get embeddings for a list of texts"""
        raise NotImplementedError

    def _process_batch(self, batch: List[str]) -> np.ndarray:
        """Process a single batch of texts"""
        raise NotImplementedError

class SentenceTransformerModel(BaseEmbeddingModel):
    """Wrapper for SentenceTransformer models"""

    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.model = SentenceTransformer(model_name)
        if torch.cuda.is_available():
            self.model = self.model.to(torch.device('cuda'))

    def get_embeddings(self, texts: List[str], batch_size: int) -> np.ndarray:
        cached_embeddings = []
        texts_to_encode = []
        text_positions = []

        for i, text in enumerate(texts):
            if text in self.cache:
                cached_embeddings.append(self.cache[text])
            else:
                texts_to_encode.append(text)
                text_positions.append(i)

        if texts_to_encode:
            new_embeddings = self.model.encode(
                texts_to_encode,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )

            for text, embedding in zip(texts_to_encode, new_embeddings):
                self.cache[text] = embedding

            all_embeddings = np.zeros(
                (len(texts), new_embeddings.shape[1]),
                dtype=np.float32
            )

            cached_positions = [i for i in range(len(texts)) if i not in text_positions]
            for pos, emb in zip(cached_positions, cached_embeddings):
                all_embeddings[pos] = emb

            for pos, emb in zip(text_positions, new_embeddings):
                all_embeddings[pos] = emb

            return all_embeddings

        return np.stack(cached_embeddings)

class HuggingFaceModel(BaseEmbeddingModel):
    """Wrapper for HuggingFace models"""

    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        if torch.cuda.is_available():
            self.model = self.model.to(torch.device('cuda'))

    def get_embeddings(self, texts: List[str], batch_size: int) -> np.ndarray:
        cached_embeddings = []
        texts_to_encode = []
        text_positions = []

        for i, text in enumerate(texts):
            if text in self.cache:
                cached_embeddings.append(self.cache[text])
            else:
                texts_to_encode.append(text)
                text_positions.append(i)

        if texts_to_encode:
            # Process in batches
            batches = [texts_to_encode[i:i + batch_size]
                       for i in range(0, len(texts_to_encode), batch_size)]
            new_embeddings = []

            for batch in batches:
                batch_embeddings = self._process_batch(batch)
                new_embeddings.extend(batch_embeddings)

            new_embeddings = np.array(new_embeddings)

            for text, embedding in zip(texts_to_encode, new_embeddings):
                self.cache[text] = embedding

            all_embeddings = np.zeros(
                (len(texts), new_embeddings.shape[1]),
                dtype=np.float32
            )

            cached_positions = [i for i in range(len(texts)) if i not in text_positions]
            for pos, emb in zip(cached_positions, cached_embeddings):
                all_embeddings[pos] = emb

            for pos, emb in zip(text_positions, new_embeddings):
                all_embeddings[pos] = emb

            return all_embeddings

        return np.stack(cached_embeddings)

    def _process_batch(self, batch: List[str]) -> np.ndarray:
        # Tokenize and get model outputs
        inputs = self.tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        )

        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Use mean pooling of last hidden states
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        return embeddings.cpu().numpy()

# Initialize the model registry
model_registry = EmbeddingModelRegistry()

# Register default models
# model_registry.register_model(
#     "mpnet",
#     SentenceTransformerModel("sentence-transformers/all-mpnet-base-v2")
# )

model_registry.register_model(
    "minilm",
    SentenceTransformerModel("sentence-transformers/all-MiniLM-L6-v2")
)

# model_registry.register_model(
#     "bert",
#     HuggingFaceModel("bert-base-uncased")
# )

def get_model(model_id: Optional[str] = None) -> BaseEmbeddingModel:
    """Get an embedding model by ID, using default if none specified"""
    if model_id is None:
        model_id = "mpnet"  # Default model
    return model_registry.get_model(model_id)