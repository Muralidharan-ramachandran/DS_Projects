import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlalchemy as sa
from sklearn.metrics import classification_report
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#Initialize sessions state
if "predict_state" not in st.session_state:
    st.session_state.predict_state = False
if "classify_state" not in st.session_state:
    st.session_state.classify_state = False
if "recommend_state" not in st.session_state:
    st.session_state.recommend_state = False

# Load pickled models and data
@st.cache_data(show_spinner="Loading ML models...")
def load_models():
    return (
        joblib.load('Rate_model_reg.pkl'),
        joblib.load('model_clf.pkl'),
        
    )

Ratemodel, rclass = load_models()

if "predict_clicked" not in st.session_state:
    st.session_state.predict_clicked = False

if "classify_clicked" not in st.session_state:
    st.session_state.classify_clicked = False

if "recommend_clicked" not in st.session_state:
    st.session_state.recommend_clicked = False



Tourism_df = pd.read_excel(r"C:\Users\Admin\Downloads\tourism\Final_table2.xlsx")
selected_features = [
    "VisitYear",        
    "VisitMonth",       
    "VisitMode",    
    "AttractionId",           
    "AttractionTypeId",  
    "CountryId",        
    "RegionId"          
]

vst_mode_dic={1 : "Business",
              2 : "Couples",
              3 : "Family",
              4 : "Friends",
              5 : "Solo"}

df = Tourism_df[selected_features + ["Rating"]].copy()

if selected_features not in st.session_state:
    st.session_state.visit_year = int(df["VisitYear"].min())
    st.session_state.visit_month = int(df["VisitMonth"].min())
    st.session_state.visit_mode = int(df["VisitMode"].min())
    st.session_state.AttractionId = int(df["AttractionId"].min())
    st.session_state.attraction_type_id = int(df["AttractionTypeId"].min())
    st.session_state.country_id  = int(df["CountryId"].min())
    st.session_state.Region = int(df["RegionId"].min())
    

# Recommendation System Functions

@st.cache_resource

def recommend_attractions_content_based(attraction_id, df, n=5):
    
    attraction_features = df[df["AttractionId"] == attraction_id][["AttractionTypeId", "UserId"]].values
    
    # Ensure the array is not empty
    if attraction_features.size == 0:
        return ["No recommendations found. Attraction ID might be incorrect or missing."]
    
    #attraction_features = attraction_features.reshape(-1, 1)  # Reshape if needed
    knn = NearestNeighbors(n_neighbors=n, metric="cosine")
    knn.fit(df[["AttractionTypeId", "UserId"]])

    distances, indices = knn.kneighbors(attraction_features)
    recommendations = df.iloc[indices[0]]["Attraction"].tolist()
    recommendations = list(set(recommendations))

    return recommendations


@st.cache_resource
# Collaborative Filtering using KNN


def recommend_attractions_collaborative(user_id, df, n=5):
    user_item_matrix = df.pivot_table(index="UserId", columns="AttractionId", values="Rating", aggfunc="mean")
    user_sparse_matrix = csr_matrix(user_item_matrix.fillna(0))
    knn = NearestNeighbors(metric="cosine", algorithm="brute")
    knn.fit(user_sparse_matrix)
    user_index = user_item_matrix.index.get_loc(user_id)
    distances, indices = knn.kneighbors(user_sparse_matrix[user_index], n_neighbors=n + 1)
    similar_users = indices.flatten()[1:]
    recommendations = []
    for sim_user in similar_users:
        top_attractions = user_item_matrix.iloc[sim_user].sort_values(ascending=False).index[:n]
        recommendations.extend(top_attractions)
    return list(set(recommendations))[:n]

# Streamlit App
st.title("Tourism Experience Analytics")
st.sidebar.title("🌍 Travel Experience Dashboard")
option = st.sidebar.selectbox("Choose an analysis", ["Prediction", "Classification", "Recommendation"])

if option == "Prediction":
    st.subheader("🤖 Rating Prediction")
    
    with st.form(key="prediction_form"):
      visit_year = st.number_input("Visit Year", min_value=int(df["VisitYear"].min()), max_value=int(df["VisitYear"].max()))
      visit_month = st.number_input("Visit Month", min_value=int(df["VisitMonth"].min()), max_value=int(df["VisitMonth"].max()))
      visit_mode = st.number_input("Visit Mode", min_value=int(df["VisitMode"].min()), max_value=int(df["VisitMode"].max()))
      AttractionId = st.selectbox("Select Attraction ID", df["AttractionId"].unique())
      attraction_type_id = st.selectbox("Select Attraction Type ID", df["AttractionTypeId"].unique())
      country_id = st.selectbox("Select Country ID", df["CountryId"].unique())
      Region = st.selectbox("Select Region ID", df["RegionId"].unique())
      # Submit button inside form
      predict_button = st.form_submit_button("Predict Rating")


   
    if  predict_button:
        st.session_state.predict_clicked = True
        pred_rating = Ratemodel.predict([[visit_year, visit_month,visit_mode,AttractionId,attraction_type_id,country_id,Region]])[0]
        st.write(f"Predicted Rating: {pred_rating}")

    

    
        
        

elif option == "Classification":
    st.subheader("📊 Visit Mode Classification")

    with st.form(key="prediction_form"):
      visit_year = st.number_input("Visit Year", min_value=int(df["VisitYear"].min()), max_value=int(df["VisitYear"].max()))
      visit_month = st.number_input("Visit Month", min_value=int(df["VisitMonth"].min()), max_value=int(df["VisitMonth"].max()))
      AttractionId = st.selectbox("Select Attraction ID", df["AttractionId"].unique())
      attraction_type_id = st.selectbox("Select Attraction Type ID", df["AttractionTypeId"].unique())
      country_id = st.selectbox("Select Country ID", df["CountryId"].unique())
      Region = st.selectbox("Select Region ID", df["RegionId"].unique())

      classify_button = st.form_submit_button("Predict Visit Mode")
    if classify_button:
        st.session_state.classify_clicked = True
        pred_visit_mode = rclass.predict([[visit_year, visit_month, AttractionId, attraction_type_id, country_id, Region]])[0]
        
        if pred_visit_mode in vst_mode_dic:
           visit_mode_label = vst_mode_dic[pred_visit_mode]
           st.write(f"Predicted Visit Mode: {pred_visit_mode} - {visit_mode_label}")
        else:
           st.write(f"Predicted Visit Mode: {pred_visit_mode} - No matching mode found")

        

    


        
if option != "Recommendation":
    st.session_state.recommend_clicked = False

elif option == "Recommendation":
    st.subheader("🎯 Recommendations")
    recommendation_type = st.sidebar.radio("Choose Recommendation Type", ["Content-Based", "Collaborative Filtering"])

    if recommendation_type == "Content-Based":
        attraction_ids = Tourism_df["AttractionId"].unique()
        attraction_input = st.selectbox("Select Attraction ID:", attraction_ids)

        if st.button("Get Recommendations"):
            st.session_state.recommend_clicked = True
        if st.session_state.recommend_clicked:
            st.write(f"Recommended suggestion for attractions: {recommend_attractions_content_based(attraction_input, Tourism_df)}")

    elif recommendation_type == "Collaborative Filtering":
        user_ids = Tourism_df["UserId"].unique()
        user_input = st.selectbox("Select User ID:", user_ids)
        if st.button("Get Recommendations"):
            st.session_state.recommend_clicked = True
        if st.session_state.recommend_clicked:
            recommended_attractions = recommend_attractions_collaborative(user_input, Tourism_df)
            filtered_recommendations = Tourism_df[Tourism_df["AttractionId"].isin(recommended_attractions)][["AttractionId", "Attraction"]]
            filtered_recommendations_id = filtered_recommendations["AttractionId"].unique()
            filtered_recommendations_at = filtered_recommendations["Attraction"].unique()
            st.write(f"Recommended attraction_ids for User ID {user_input}:")
            for i in range(len(filtered_recommendations_id)):
                st.write(filtered_recommendations_id[i])
                st.write(filtered_recommendations_at[i])


