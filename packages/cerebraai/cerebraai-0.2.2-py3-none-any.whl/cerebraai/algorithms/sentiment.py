# Written by Juan Pablo Gutiérrez
# 06/01/2025
# This file handles sentiment analysis of a prompt.

from nltk.sentiment import SentimentIntensityAnalyzer
import text2emotion as te
from typing import Dict
from cerebraai.models.llm import LLM

def _get_sentiment_analysis(prompt: str) -> Dict[str, float]:
    """
    Gets the sentiment analysis of the given prompt.

    Args:
        prompt (str): The prompt to analyze.

    Returns:
        dict: The sentiment scores of the prompt.
    """
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(prompt)

def _get_emotion_analysis(prompt: str) -> Dict[str, float]:
    """
    Gets the emotion analysis of the given prompt.

    Args:
        prompt (str): The prompt to analyze.

    Returns:
        dict: The emotion scores of the prompt.
    """
    return te.get_emotion(prompt)

def _normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalizes a dictionary of scores to sum to 1.

    Args:
        scores (dict): Scores to normalize.

    Returns:
        dict: Normalized scores.
    """
    total = sum(scores.values())
    return {key: value / total if total > 0 else 0 for key, value in scores.items()}

def _analyze_prompt(prompt: str) -> Dict[str, Dict[str, float]]:
    """
    Analyzes the prompt for sentiment and emotion.

    Args:
        prompt (str): The prompt to analyze.

    Returns:
        dict: Combined sentiment and emotion analysis results.
    """
    sentiment = _get_sentiment_analysis(prompt)
    emotion = _get_emotion_analysis(prompt)

    return {
        "sentiment": sentiment,
        "emotion": emotion
    }

def get_sentiment_emotion_model(
    prompt: str,
    llms: list[LLM],
    sentiment_weights: Dict[str, float],
    emotion_weights: Dict[str, float]
) -> LLM:
    """
    Selects the best LLM based on sentiment and emotion analysis.

    Args:
        prompt (str): The prompt to analyze.
        llms (list): List of LLMs with their descriptions.
        sentiment_weights (dict): Weights for sentiment analysis.
        emotion_weights (dict): Weights for emotion analysis.

    Returns:
        dict: The selected LLM and its score.
    """

    prompt_analysis = _analyze_prompt(prompt)
    prompt_sentiment = _normalize_scores(prompt_analysis["sentiment"])
    prompt_emotion = _normalize_scores(prompt_analysis["emotion"])

    llm_analysis = {llm.model: _analyze_prompt(llm.conditions.to_description()) for llm in llms}
    llm_sentiment = {
        model: _normalize_scores(analysis["sentiment"])
        for model, analysis in llm_analysis.items()
    }
    llm_emotion = {
        model: _normalize_scores(analysis["emotion"])
        for model, analysis in llm_analysis.items()
    }

    # Compare with prompt and calculate weighted scores
    scores = {}
    for llm in llms:
        model = llm.model

        # Calculate sentiment similarity
        sentiment_similarity = sum(
            prompt_sentiment[sentiment] * llm_sentiment[model].get(sentiment, 0) * sentiment_weights.get(sentiment, 1)
            for sentiment in prompt_sentiment
        )

        # Calculate emotion similarity
        emotion_similarity = sum(
            prompt_emotion[emotion] * llm_emotion[model].get(emotion, 0) * emotion_weights.get(emotion, 1)
            for emotion in prompt_emotion
        )

        # Final score for the LLM
        scores[llm] = sentiment_similarity + emotion_similarity

    # Select the best model
    best_model, best_score = max(scores.items(), key=lambda x: x[1])

    return {
        "llm": best_model,
        "score": best_score
    }

def _analyze_prompt(prompt: str) -> dict:
    """
    Analyzes the prompt for sentiment and emotion.

    Args:
        prompt (str): The prompt to analyze.

    Returns:
        dict: Combined sentiment and emotion analysis results.
    """
    # Example implementation using existing methods
    sentiment = _get_sentiment_analysis(prompt)
    emotion = _get_emotion_analysis(prompt)
    return {"sentiment": sentiment, "emotion": emotion}

def _normalize_scores(scores: dict) -> dict:
    """
    Normalizes the scores to sum up to 1 for comparison.

    Args:
        scores (dict): Scores to normalize.

    Returns:
        dict: Normalized scores.
    """
    total = sum(scores.values())
    return {key: value / total if total > 0 else 0 for key, value in scores.items()}
