# Written by Juan Pablo Gutiérrez
# 06/01/2025
# This file handles semantic similarity between a prompt and a LLM model.

from sentence_transformers import SentenceTransformer
from cerebraai.algorithms.utils import similarity_score
from cerebraai.models.llm import LLM

def get_semantic_based_model(model: SentenceTransformer, prompt: str, llms: list[LLM]) -> str:
    """
    Gets the best semantic based model for the given prompt.

    Args:
        model (SentenceTransformer): The semantic model to use.
        prompt (str): The prompt to analyze.
        llms (dict): The LLM models to decide on.

    Returns:
        dict: The best semantic based model.
    """
    similarities = {llm: similarity_score(model, prompt, llm.conditions.to_description()) for llm in llms}
    best_match = max(similarities, key=similarities.get)
    best_score = similarities[best_match]

    return {
        "llm": best_match,
        "score": best_score
    }
