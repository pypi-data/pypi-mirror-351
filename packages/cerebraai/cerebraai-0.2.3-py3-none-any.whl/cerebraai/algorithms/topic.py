# Written by Juan Pablo Gutiérrez
# 06/01/2025
# This file handles topic based selection of a LLM model.

from sentence_transformers import SentenceTransformer, util
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from cerebraai.algorithms.utils import similarity_score
from cerebraai.models.llm import LLM

import nltk
import numpy as np

vectorizer = CountVectorizer()

def get_topic_based_model(model: SentenceTransformer, prompt: str, llms: list[LLM]) -> dict:
    """
    Gets the best topic based model for the given prompt.

    Args:
        model (SentenceTransformer): The semantic model to use.
        prompt (str): The prompt to analyze.
        llms (list[LLM]): The LLM models to decide on.

    Returns:
        str: The best topic based model.
    """
    tokens = nltk.word_tokenize(prompt.lower())

    X = vectorizer.fit_transform([' '.join(tokens)])

    lda = LatentDirichletAllocation(n_components=3, random_state=42)
    topic_distributions = lda.fit_transform(X)

    topic_based_models = {}

    # Main part: Loop through each descriptions to calculate similarities with the LLM models
    for topic_idx, topic_distribution in enumerate(lda.components_):
        topic_desc = generate_topic_description(topic_distribution)
        # Calculate similarity scores for each LLM model
        similarities = {llm.model: similarity_score(model, topic_desc, llm.conditions.to_description()) for llm in llms}
        best_match, best_score = max(similarities.items(), key=lambda x: x[1])
        topic_based_models[topic_idx] = {
            "llm": best_match,
            "similarity": best_score
        }

    best_topic = np.argmax(topic_distributions)
    result = topic_based_models[best_topic]

    return {
        "llm": next(llm for llm in llms if llm.model == result['llm']),
        "score": result['similarity']
    }

def generate_topic_description(topic_distribution, top_n_words=10):
    """
    Extracts the topic description from the topic distribution.
    """
    words = vectorizer.get_feature_names_out()
    top_words_idx = np.argsort(topic_distribution)[-top_n_words:]
    top_words = [words[i] for i in top_words_idx]
    return ' '.join(top_words)
