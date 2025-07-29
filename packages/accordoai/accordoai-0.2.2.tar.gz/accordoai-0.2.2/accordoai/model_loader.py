from importlib.resources import files
from keras.models import load_model



def load():
    model_path = files("accordoai.models").joinpath("model.keras")
    model = load_model(str(model_path))
    return model
