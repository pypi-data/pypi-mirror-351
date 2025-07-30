from sentence_transformers import SentenceTransformer, models
from sentence_transformers.util import cos_sim
from keybert import KeyBERT
from .config import DEFAULT_PATHS

DEFAULT_KEYBERT_PATH = DEFAULT_PATHS["keybert"]


def load_sentence_bert_model(model_path: str = None) -> SentenceTransformer:
    path = model_path or DEFAULT_KEYBERT_PATH
    word_embedding_model = models.Transformer(
        model_name_or_path=path,
        max_seq_length=256,
        do_lower_case=False
    )
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode='mean'
    )
    normalize_model = models.Normalize()
    return SentenceTransformer(modules=[word_embedding_model, pooling_model, normalize_model])

KEYBERT_MODEL = load_sentence_bert_model()

def encode_sentences(model: SentenceTransformer = None, sentences=None):
    m = model or KEYBERT_MODEL
    return m.encode(
        sentences,
        convert_to_tensor=True,
        show_progress_bar=True,
        normalize_embeddings=True
    )

def compute_cosine_similarity(embeddings=None):
    return cos_sim(embeddings, embeddings)

def extract_keywords(
    text=None,
    top_n: int = 5,
    diversity: float = 0.7,
    use_mmr: bool = True,
    stop_words='english',
    keyphrase_ngram_range=(1, 2),
    model: SentenceTransformer = None
):
    if text is None or (isinstance(text, list) and not text):
        raise ValueError("No content provided for keyword extraction.")
    kw_model = model or KEYBERT_MODEL
    docs = text if isinstance(text, list) else [text]
    kw = KeyBERT(kw_model)
    return kw.extract_keywords(
        docs,
        keyphrase_ngram_range=keyphrase_ngram_range,
        stop_words=stop_words,
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=diversity
    )