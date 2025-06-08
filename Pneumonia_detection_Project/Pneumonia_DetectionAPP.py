import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image

# 🔧preprocess function for Pneumonia model
def preprocess_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB").resize((224, 224))  # Use 224x224 for MobileNetV2
    img = np.array(img) / 255.0
    return np.expand_dims(img, axis=0)

# 🧠 Load model
model = tf.keras.models.load_model("pneumonia_mobilenetv2.keras")

# 🏷️ Class names
class_names = ["Normal", "Pneumonia"]

# 🎨 App title and subtitle
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🩻 PneumoDetect</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #7f8c8d;'>Chest X-Ray Based Pneumonia Detection</h4>", unsafe_allow_html=True)

# 📤 Upload image
uploaded_file = st.file_uploader("Upload a chest X-ray image", type=["jpg", "png"])

if uploaded_file:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(uploaded_file, caption="Uploaded Chest X-Ray", use_column_width=True)

    with col2:
        img = preprocess_image(uploaded_file)
        with st.spinner("Analyzing X-ray..."):
            prediction = model.predict(img)
            predicted_class = class_names[int(prediction[0] > 0.5)]  # sigmoid output → 0 or 1

        st.success(f"**Prediction:** {predicted_class}")
