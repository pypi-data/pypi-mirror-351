from .bases import *
from collections import Counter, defaultdict
import random



class ToyGenerator(BaseGenerator):
    """用于流程测试"""

    def generate(self, query: str, docs: List[Document]) -> str:
        return f"Answer to: {query} (based on {len(docs)} docs)"


class ToyVectorStore(BaseVectorStore):
    """随机生成向量作为embedding，用于RAG流程测试"""

    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add(self, docs: List[Document]):
        self.documents.extend(docs)
        # Generate dummy embeddings (in real implementation use sentence-transformers)
        self.embeddings.extend([np.random.rand(768) for _ in docs])

    def search(self, query_vector: np.ndarray, top_k: int) -> List[Document]:
        if not self.embeddings:
            return []

        # Calculate cosine similarity
        embeddings = np.array(self.embeddings)
        query_norm = np.linalg.norm(query_vector)
        embeddings_norm = np.linalg.norm(embeddings, axis=1)

        # Avoid division by zero
        if query_norm == 0 or np.any(embeddings_norm == 0):
            scores = np.zeros(len(embeddings))
        else:
            scores = np.dot(embeddings, query_vector) / (embeddings_norm * query_norm)

        # Get top_k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [self.documents[i] for i in top_indices]


class ToyDenseRetriever(BaseRetriever):
    def __init__(self, vectorstore: BaseVectorStore):
        self.vectorstore = vectorstore

    def encode(self, query: str) -> np.ndarray:
        # In real implementation, use sentence-transformers model
        return np.random.rand(768)

    def retrieve(self, query: str, top_k: int) -> List[Document]:
        query_vector = self.encode(query)
        return self.vectorstore.search(query_vector, top_k)


class SynonymQueryRewriter(BaseQueryRewriter):
    def __init__(self, synonym_dict: dict = None):
        self.synonym_dict = synonym_dict or {
            "how": ["what", "method"],
            "why": ["reason", "cause"],
            "best": ["top", "greatest"],
            "define": ["explain", "describe"]
        }

    def rewrite(self, query: str) -> str:
        words = query.split()
        for word in words:
            if word in self.synonym_dict:
                word = random.choice(self.synonym_dict[word])
        return " ".join(words)


class RAGEvaluator(BaseEvaluator):
    def __init__(self, metrics: List[str] = ["rouge", "exact_match"]):
        self.metrics = metrics

    def evaluate(self, prediction: str, reference: str) -> Dict[str, float]:
        results = {}

        if "rouge" in self.metrics:
            rouge_scores = self._rouge_score(prediction, reference)
            results.update(rouge_scores)

        if "exact_match" in self.metrics:
            results["exact_match"] = float(prediction.strip().lower() == reference.strip().lower())

        return results

    def evaluate_batch(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        results = defaultdict(list)

        for pred, ref in zip(predictions, references):
            score = self.evaluate(pred, ref)
            for metric, value in score.items():
                results[metric].append(value)

        # Calculate average for each metric
        return {metric: np.mean(values) for metric, values in results.items()}

    def _rouge_score(self, candidate: str, reference: str) -> Dict[str, float]:
        # Simplified ROUGE calculation
        c_words = candidate.split()
        r_words = reference.split()

        # Unigram overlap
        c_count = Counter(c_words)
        r_count = Counter(r_words)

        overlap = sum(min(c_count[word], r_count[word]) for word in set(c_words) & set(r_words))

        precision = overlap / len(c_words) if c_words else 0.0
        recall = overlap / len(r_words) if r_words else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "rouge1_precision": precision,
            "rouge1_recall": recall,
            "rouge1_f1": f1
        }



class ToyRAGPipeline(BasePipeline):
    def __init__(
        self,
        retriever: BaseRetriever,
        generator: BaseGenerator,
        rewriter: BaseQueryRewriter = None,
        reranker: BaseReranker = None,
        evaluator: BaseEvaluator = None
    ):
        self.retriever = retriever
        self.generator = generator
        self.rewriter = rewriter if reranker is not None else BaseQueryRewriter()
        self.reranker = reranker if reranker is not None else BaseReranker()
        self.evaluator = evaluator

    def run(self, query: str) -> str:
        query_ = self.rewriter.rewrite(query)
        docs = self.retriever.retrieve(query_, top_k=10)
        reranked_docs = self.reranker.rerank(query_, docs)
        answer = self.generator.generate(query_, reranked_docs)
        return answer

    def evaluate(self, dataset: List[Dict]) -> Dict[str, float]:
        assert self.evaluate is not None, "`evaluator` of `StandardRAGPipeline` is None!"
        predictions = []
        references = []

        for item in dataset:
            query = item["query"]
            reference = item["answer"]

            prediction = self.run(query)
            predictions.append(prediction)
            references.append(reference)

        return self.evaluator.evaluate_batch(predictions, references)


def run_toyrag():
    # Create vector store with sample documents
    vectorstore = ToyVectorStore()
    documents = [
        Document("Ragxis is a modular RAG framework for research."),
        Document("Retrieval-Augmented Generation combines retrieval and generation."),
        Document("Self-RAG is an adaptive RAG approach that critiques its own retrievals."),
        Document("RePlug uses multiple retrieval passes for better context."),
        Document("Vector stores are used for efficient similarity search.")
    ]
    vectorstore.add(documents)

    # Initialize pipeline components
    retriever = ToyDenseRetriever(vectorstore)
    generator = ToyGenerator()
    rewriter = SynonymQueryRewriter()
    reranker = BaseReranker()
    evaluator = RAGEvaluator()

    # Create pipeline
    pipeline = ToyRAGPipeline(retriever, generator, rewriter, reranker, evaluator)

    # Run query
    query = "What is Ragxis?"
    result = pipeline.run(query)
    print(f"Query: {query}")
    print(f"Result: {result}")

    # Evaluate on sample QA dataset
    qa_data = [
        {"query": "What is Ragxis?", "answer": "a modular RAG framework for research"},
        {"query": "What does RAG stand for?", "answer": "Retrieval-Augmented Generation"}
    ]
    metrics = pipeline.evaluate(qa_data)
    print("\nEvaluation Metrics:")
    for metric, score in metrics.items():
        print(f"{metric}: {score:.4f}")
