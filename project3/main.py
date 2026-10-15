import numpy as np
import streamlit as st
from PIL import Image

try:
    from tensorflow.keras.applications.mobilenet_v2 import (
        MobileNetV2,
        preprocess_input,
        decode_predictions,
    )
except ImportError:
    MobileNetV2 = None
    preprocess_input = None
    decode_predictions = None


@st.cache_resource
def load_model():
    if MobileNetV2 is None:
        raise ImportError("TensorFlow/Keras is required to use MobileNetV2.")
    return MobileNetV2(weights="imagenet")


def preprocess_image(image):
    image = image.resize((224, 224))
    image_array = np.array(image.convert("RGB"))
    image_array = np.expand_dims(image_array, axis=0)
    if preprocess_input is None:
        raise ImportError("preprocess_input is unavailable. Please install TensorFlow.")
    image_array = preprocess_input(image_array)
    return image_array


def classify_image(image, model):
    preprocessed_image = preprocess_image(image)
    predictions = model.predict(preprocessed_image, verbose=0)
    if decode_predictions is None:
        raise ImportError("decode_predictions is unavailable. Please install TensorFlow.")
    decoded_predictions = decode_predictions(predictions, top=3)[0]
    return decoded_predictions


def main():
    st.set_page_config(page_title="Image Classification with MobileNetV2", layout="wide")
    st.title("Image Classification with MobileNetV2")
    st.write("Upload an image to classify it using the MobileNetV2 model.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image.", use_container_width=True)
            st.write("Classifying...")

            model = load_model()
            predictions = classify_image(image, model)

            if predictions:
                st.write("Top Predictions:")
                for i, (_, label, score) in enumerate(predictions, start=1):
                    st.write(f"{i}. {label}: {score:.4f}")
            else:
                st.write("No predictions available.")
        except Exception as e:
            st.error(f"Error occurred while processing the image: {e}")


if __name__ == "__main__":
    main()