# Written by Juan Pablo Gutiérrez
# 06/01/2025
# This file handles utils for the algorithms.

from sentence_transformers import SentenceTransformer, util

def similarity_score(model: SentenceTransformer, desc1: str, desc2: str) -> float:
    """
    Calculates the similarity score between two descriptions.

    Args:
        model (SentenceTransformer): The semantic model to use.
        desc1 (str): The first description.
        desc2 (str): The second description.

    Returns:
        float: The similarity score between the two descriptions.
    """
    embedding1 = model.encode(desc1)
    embedding2 = model.encode(desc2)
    return util.pytorch_cos_sim(embedding1, embedding2).item()

