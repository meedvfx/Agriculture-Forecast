import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
from datetime import date

# 🔧 Configuration Streamlit
st.set_page_config(
    page_title="Prédiction de la Production Agricole",
    layout="centered",
    page_icon="🌾"
)

st.title("🌿 Prédiction de la Production Agricole (en Tonnes)")
st.write("Cette application permet de prédire la **quantité produite (en tonnes)** selon la **filière**, le **produit** et l’**année** sélectionnée.")

# 🔁 Chargement du modèle
@st.cache_resource
def load_model():
    with open("modele/modelagr.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

# 🔁 Chargement des données
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data("data/dataagr.csv")

# ✅ Préparation des sélections utilisateur
filieres = df['Filière'].dropna().unique().tolist()
produits = df['Produit'].dropna().unique().tolist()
annees = sorted(df['year'].dropna().unique())

# 🎛️ Interface utilisateur
filiere = st.selectbox("🌱 Sélectionnez la filière :", filieres)
produit = st.selectbox("🍊 Sélectionnez le produit :", produits)
annee = st.selectbox("📅 Sélectionnez l'année :", annees)

# 📌 Prédiction
if st.button("Prédire la production"):
    input_df = pd.DataFrame({
        "Filière": [filiere],
        "Produit": [produit],
        "year": [annee]
    })

    # 🔮 Prédiction
    prediction = model.predict(input_df)[0]

    # ✅ Affichage
    st.success(f"🌾 La production estimée de **{produit}** en **{annee}** est de : **{prediction:,.2f} tonnes**")
