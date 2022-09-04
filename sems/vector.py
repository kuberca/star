#!/usr/bin/env python

"""
vector.py - generate semantic vectors for log templates
            compute semantic similarity between vectors
"""
import fasttext
import os

from scipy import spatial



class Vector:
    def __init__(self, model_file: str) -> None:
        if os.path.exists(model_file):
            print("loading model file for Vector: ", model_file)
            self.model = fasttext.load_model(model_file)
        else:
            raise Exception("Model file does not exist")

    def generate(self, log_template: str):
        """
        Generate semantic vector for log template
        """
        return self.model.get_sentence_vector(log_template)

    def similarity(self, vec1, vec2: list) -> float:
        """
        Compute semantic similarity between two vectors
        """
        cos = spatial.distance.cosine(vec1, vec2)
        cosine_similarity = 1 - cos

        return cosine_similarity
