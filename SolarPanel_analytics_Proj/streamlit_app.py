import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image
from sklearn.metrics import precision_score, recall_score, f1_score

# Updated preprocess function
def preprocess_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB").resize((128, 128))
    img = np.array(img) / 255.0
    return np.expand_dims(img, axis=0)

st.title("SolarGuard: Solar Panel Defect Detection")

# Load model
model = tf.keras.models.load_model("mobilenetv2_solar_F.keras")
class_names = ["Bird-drop", "Clean", "Dusty", "Electrical-damage", "Physical-Damage", "Snow-covered"]

# Upload image
uploaded_file = st.file_uploader("Upload a solar panel image", type=["jpg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    img = preprocess_image(uploaded_file)
    prediction = model.predict(img)
    predicted_class = class_names[np.argmax(prediction)]
    st.success(f"Prediction: **{predicted_class}**")