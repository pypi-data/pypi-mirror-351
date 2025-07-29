# Written by Juan Pablo Gutiérrez
# 05/01/2025
# This file handles analysis of a prompt.

from typing import Dict
from sentence_transformers import SentenceTransformer
from cerebraai.algorithms.semantic import get_semantic_based_model
from cerebraai.algorithms.sentiment import get_sentiment_emotion_model
from cerebraai.algorithms.topic import get_topic_based_model
from cerebraai.models.llm import LLM

def get_best_model(
    model: SentenceTransformer,
    prompt: str,
    llms: list,
    weights: dict = {"semantic": 0.3, "topic": 0.5, "sentiment": 0.3},
    sentiment_weights: dict = {"positive": 0.5, "negative": 0.5},
    emotion_weights: dict = {"happy": 0.5, "sad": 0.5},
) -> Dict[LLM, float]:
    
    """
    Gets the best model for the given prompt based on semantic, topic, and sentiment analyses.

    Args:
        model (SentenceTransformer): Semantic analysis model.
        prompt (str): The prompt to analyze.
        llms (list[LLM]): List of LLMs with their descriptions.
        weights (dict): Weights for semantic, topic, and sentiment analyses.

    Returns:
        str: The name of the best LLM for the given prompt.
    """
    # Perform analyses
    semantic_model = get_semantic_based_model(model, prompt, llms)
    topic_model = get_topic_based_model(model, prompt, llms)
    sentiment_model = get_sentiment_emotion_model(prompt, llms, sentiment_weights, emotion_weights)

    # Collect scores for each analysis
    results : Dict[str, Dict[str, LLM]] = {
        "semantic": semantic_model,
        "topic": topic_model,
        "sentiment": sentiment_model,
    }

    # Aggregate scores for each LLM
    aggregated_scores = {}
    for llm in llms:
        model_name = llm.model

        # Weighted sum of scores for each model
        aggregated_scores[llm] = (
            results["semantic"]["score"] * weights["semantic"] if results["semantic"]["llm"].model == llm.model else 0
            + results["topic"]["score"] * weights["topic"] if results["topic"]["llm"].model == llm.model else 0
            + results["sentiment"]["score"] * weights["sentiment"] if results["sentiment"]["llm"].model == llm.model else 0
        )

    # Select the model with the highest aggregated score
    best_model = max(aggregated_scores, key=aggregated_scores.get)

    return {
        "llm": best_model,
        "score": aggregated_scores[best_model],
    }
