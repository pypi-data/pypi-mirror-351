from abc import ABC, abstractmethod
from typing import List, Dict, Any
import hashlib
import numpy as np


class BaseModule(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class Document:
    def __init__(self, content: str, metadata: Dict[str, Any] = None, doc_id: str = None):
        self.content = content
        self.metadata = metadata or {}
        self.doc_id = doc_id or self._generate_id(content)

    @staticmethod
    def _generate_id(content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def __repr__(self):
        return f"Document(id={self.doc_id}, content={self.content[:50]}...)"


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> List[Document]:
        pass


class BaseEvaluator(BaseModule):
    def evaluate(self, prediction: str, reference: str) -> Dict[str, float]:
        raise NotImplementedError

    def evaluate_batch(self, predictions: List[str], references: List[str], *args, **kwargs) -> Dict[str, float]:
        raise NotImplementedError

    def __call__(self, prediction: str, reference: str) -> Dict[str, float]:
        return self.evaluate(prediction, reference)


class BaseGenerator(BaseModule, ABC):
    @abstractmethod
    def generate(self, query: str, docs: List[Document]) -> str:
        raise NotImplementedError

    def __call__(self, query: str, docs: List[Document]) -> str:
        return self.generate(query, docs)


class BaseQueryRewriter(BaseModule):
    def rewrite(self, query: str) -> str:
        return query  # Default no-op

    def __call__(self, query: str) -> str:
        return self.rewrite(query)


class BaseReranker(BaseModule):
    def rerank(self, query: str, docs: List[Document]) -> List[Document]:
        return docs  # Default: no reranking

    def __call__(self, query: str, docs: List[Document]) -> List[Document]:
        return self.rerank(query, docs)


class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, docs: List[Document]):
        pass

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int) -> List[Document]:
        pass


class BaseRetriever(BaseModule, ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> List[Document]:
        raise NotImplementedError

    def __call__(self, query: str, top_k: int) -> List[Document]:
        return self.retrieve(query, top_k)


class BasePipeline(ABC):
    @abstractmethod
    def run(self, query: str) -> str:
        pass

    @abstractmethod
    def evaluate(self, dataset: List[Dict]) -> Dict[str, float]:
        pass
