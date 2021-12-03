import pandas as pd
import numpy as np
import torch
import json


class Palette:
    def __init__(self, query_embedding):
        self.color_palettes_list = list(json.load(open('./utils/colors_palettes-1000.json')))
        self.color_palettes_embeddings = torch.from_numpy(np.load("./utils/color_palettes_embeddings.npy")).squeeze(1).float().to('cpu')
        self.query_embedding = query_embedding

    def find_best_matches(self, topN=5):
        similarities = (self.color_palettes_embeddings @ self.query_embedding.T).squeeze(1)

        # Sort the data elements by their similarity score
        best_data_element = (-similarities).argsort()

        # Return the data list name of the best matches
        return [self.color_palettes_list[i] for i in best_data_element[:topN]]