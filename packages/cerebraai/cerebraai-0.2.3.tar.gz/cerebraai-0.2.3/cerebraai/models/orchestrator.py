# Written by Juan Pablo Gutiérrez
# 03/01/2025

from sentence_transformers import SentenceTransformer
from cerebraai.algorithms.analysis import get_best_model
from cerebraai.models.llm import LLM, LLMResponse, LLMConditions
from typing import Callable

class Orchestrator:

    llms: list[LLM]
    analysis_weights: dict
    sentiment_weights: dict
    emotion_weights: dict

    """
    A class that represents an AI Orchestrator. It will balance prompting to different LLMs based on the user's prompt.
    """

    def __init__(self, llms: list[LLM], text_model: SentenceTransformer, analysis_weights: dict = {"semantic": 0.3, "topic": 0.5, "sentiment": 0.3}, sentiment_weights: dict = {"positive": 0.5, "negative": 0.5}, emotion_weights: dict = {"happy": 0.5, "sad": 0.5}):
        self.llms = llms
        self.text_model = text_model
        self.analysis_weights = analysis_weights
        self.sentiment_weights = sentiment_weights
        self.emotion_weights = emotion_weights

    def execute(self, prompt: str) -> LLMResponse:
        llm = get_best_model(self.text_model, prompt, self.llms, self.analysis_weights, self.sentiment_weights, self.emotion_weights)["llm"]
        return llm.execute(prompt)

    def update_weights(self, analysis_weights: dict = None, sentiment_weights: dict = None, emotion_weights: dict = None):
        self.analysis_weights = analysis_weights
        self.sentiment_weights = sentiment_weights
        self.emotion_weights = emotion_weights

    def update_llms(self, llms: list[dict], execute : {str: Callable}):
        new_llms = []
        for llm in llms:
            new_llms.append(LLM(
                model=llm["model"],
                conditions=LLMConditions(domain=llm["conditions"]["domain"], sentiment=llm["conditions"]["sentiment"], topic=llm["conditions"]["topic"], description=llm["conditions"]["description"]),
                executor=execute[llm["model"]]
            ))

        self.llms = new_llms

    def add_llm(self, llm: LLM):
        self.llms.append(llm)
