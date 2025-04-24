import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error,root_mean_squared_error,r2_score
import joblib

df=pd.read_csv("D:\\Projects\\Crop_Production\\Cleaned_Crop_data.csv")
df1=pd.read_csv("D:\\Projects\\Crop_Production\\Cleaned_Crop_data.csv")

#label encoder
label_encoder = LabelEncoder()

categorical_columns = ['Area', 'Item']

for col in categorical_columns:
    df[col] = label_encoder.fit_transform(df[col])
df = df.fillna(0)

X = df.iloc[:, [0, 1, 2, 3, 9]]
y=df['Production']

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
r=RandomForestRegressor(n_estimators=100)
r.fit(X_train,y_train)
y_pred=r.predict(X_test)
mae=mean_absolute_error(y_test,y_pred)
rmse=root_mean_squared_error(y_test,y_pred)
r2=r2_score(y_test,y_pred)

def main():    
    st.title("🌾 Crop Production Prediction App")
    st.write("This app predicts crop production based on area harvested, yield, and year.")

    area_encoder = joblib.load("area_label_encoder.pkl")  # Encoder for 'Area'
    item_encoder = joblib.load("item_label_encoder.pkl")  # Encoder for 'Item'
    
    st.sidebar.header("User Input")
    area = st.sidebar.selectbox("Select Region", df1['Area'].unique())
    crop = st.sidebar.selectbox("Select Crop", df1['Item'].unique())
    year = st.sidebar.slider("Select Year", int(df['Year'].min()), int(df['Year'].max()), step=1)
    area_harvested = st.sidebar.number_input("Enter Area Harvested (ha)", min_value=0.0, value=1000.0, step=100.0)
    yield_per_ha = st.sidebar.number_input("Enter Yield (kg/ha)", min_value=0.0, value=1500.0, step=100.0)

    if area and crop:
     area_encoded = area_encoder.transform([area])[0]
     item_encoded = item_encoder.transform([crop])[0]

    
    if st.sidebar.button("Predict Production"):
        input_data = np.array([[area_encoded,item_encoded,year,area_harvested, yield_per_ha]])
        prediction = r.predict(input_data)
        st.sidebar.success(f"🌟 Predicted Production: {prediction[0]:,.2f} tons")
        if prediction[0] > 5000:
            st.sidebar.write("✅ This region is predicted to have a high crop production. Consider focusing on maximizing yield!")
        elif prediction[0] < 500:
            st.sidebar.write("⚠️ This region is predicted to have low crop production. It may require intervention, such as improved farming techniques or crop diversification.")
        else:
            st.sidebar.write("📈 This region has moderate crop production. Monitoring and resource optimization can improve outcomes.")
    
    st.subheader("📊 Model Performance")
    st.write(f"**Mean Absolute Error (MAE):** {mae:,.2f}")
    st.write(f"**Root Mean Squared Error (MSE):** {rmse:,.2f}")
    st.write(f"**R² Score:** {r2:.4f}")
    
    st.subheader("📈 Crop Production Trends")
    filtered_data = df1[(df1['Item'] == crop) & (df1['Area'] == area)]
    fig = px.line(filtered_data, x='Year', y='Production', title=f"Crop Production of {crop} in {area}")
    st.plotly_chart(fig)
    
    st.subheader("🌍 Yearly Trends Across All Crops")
    fig2 = px.line(df, x='Year', y='Production', color='Item', title="Yearly Trends of Crop Production")
    st.plotly_chart(fig2)

if __name__ == "__main__":
    main()
