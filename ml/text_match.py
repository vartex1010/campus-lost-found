"""
Text similarity for matching lost <-> found item descriptions.

Starts simple with TF-IDF + cosine similarity (scikit-learn) so it works
with zero extra setup. Swap in sentence-transformers later (see bottom)
for smarter, meaning-based matching instead of keyword overlap.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _combine_text(title, description, location):
    return f"{title or ''} {description or ''} {location or ''}".strip().lower()


def text_similarity(item_a, item_b):
    """
    item_a, item_b: dicts with 'title', 'description', 'location'
    Returns a float 0..1
    """
    text_a = _combine_text(item_a.get("title"), item_a.get("description"), item_a.get("location"))
    text_b = _combine_text(item_b.get("title"), item_b.get("description"), item_b.get("location"))

    if not text_a.strip() or not text_b.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform([text_a, text_b])
    except ValueError:
        # happens if both texts are only stopwords / empty after cleaning
        return 0.0

    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return float(score)


# ---------------------------------------------------------------------
# UPGRADE PATH (better accuracy, understands meaning not just keywords):
#
#   pip install sentence-transformers
#
#   from sentence_transformers import SentenceTransformer, util
#   model = SentenceTransformer('all-MiniLM-L6-v2')
#
#   def text_similarity(item_a, item_b):
#       text_a = _combine_text(item_a['title'], item_a['description'], item_a['location'])
#       text_b = _combine_text(item_b['title'], item_b['description'], item_b['location'])
#       emb = model.encode([text_a, text_b], convert_to_tensor=True)
#       return float(util.cos_sim(emb[0], emb[1]).item())
#
# This catches matches like "backpack" <-> "school bag" that TF-IDF misses
# because it understands meaning, not just shared words.
# ---------------------------------------------------------------------
