from keras.models import load_model

def load():
    # Load the trained model
    model = load_model("models/model.keras")
    return model
