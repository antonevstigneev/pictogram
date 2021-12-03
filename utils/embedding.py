import torch
import clip
import streamlit as st


device = "cpu"

@st.cache(show_spinner=True, allow_output_mutation=True)
def load_model():
   return clip.load("ViT-B/32", device=device, jit=False)


class Embedding:
  def __init__(self):
    self._model, self._preprocess = load_model()

  def getTextEmbedding(self, text):
    tokenized_text = clip.tokenize(f"{text}").to(device)
    with torch.no_grad():
      self.text_embedding = self._model.encode_text(tokenized_text)
      self.text_embedding /= self.text_embedding.norm(dim=-1, keepdim=True)

  def getImageEmbedding(self, image):
    image_input = self._preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
      image_embedding = self._model.encode_image(image_input)
      image_embedding /= image_embedding.norm(dim=-1, keepdim=True)

    return image_embedding