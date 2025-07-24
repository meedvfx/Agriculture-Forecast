import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
from datetime import date

st.set_page_config(
    page_title="Prédiction de la Production Agricole",
    layout="centered",
    page_icon="data:image/svg+xml,%3csvg stroke-width='1.75' id='Layer_1' data-name='Layer 1' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3e%3cdefs%3e%3cstyle%3e.cls-n1wrucdvdcsstajotcwn1-1%7bfill:none%3bstroke:%23FC0F0F%3bstroke-miterlimit:10%3b%3b%7d%3c/style%3e%3c/defs%3e%3cpolyline class='cls-n1wrucdvdcsstajotcwn1-1' points='7.23 6.27 1.5 12 7.23 17.73'/%3e%3cpolyline class='cls-n1wrucdvdcsstajotcwn1-1' points='16.77 17.73 22.5 12 16.77 6.27'/%3e%3cline class='cls-n1wrucdvdcsstajotcwn1-1' x1='11.05' y1='12' x2='12.95' y2='12'/%3e%3cline class='cls-n1wrucdvdcsstajotcwn1-1' x1='15.82' y1='12' x2='17.73' y2='12'/%3e%3cline class='cls-n1wrucdvdcsstajotcwn1-1' x1='6.27' y1='12' x2='8.18' y2='12'/%3e%3c/svg%3e"
)

st.title("🌿 Prédiction de la Production Agricole (en Tonnes)")
st.write("Cette application permet de prédire la **quantité produite (en tonnes)** selon la **filière**, le **produit** et l’**année** sélectionnée.")

@st.cache_resource
def load_model():
    with open("modele/modelagr.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data("data/dataagr.csv")

filieres = df['Filière'].dropna().unique().tolist()
filiere = st.selectbox("🌱 Sélectionnez la filière :", filieres)

produits_filtres = df[df['Filière'] == filiere]['Produit'].dropna().unique().tolist()

if not produits_filtres:
    st.warning("Aucun produit disponible pour cette filière")
    st.stop()

produit = st.selectbox("🍊 Sélectionnez le produit :", produits_filtres)

selected_date = st.date_input(
    "📅 Sélectionnez une date (année seulement utilisée) :",
    value=pd.to_datetime("2020-01-01"),
    min_value=pd.to_datetime("2010-01-01"),
    max_value=pd.to_datetime("2050-12-31")
)

year = selected_date.year

if st.button("Prédire la production"):
    input_df = pd.DataFrame({
        "Filière": [filiere],
        "Produit": [produit],
        "year": [year]
    })


    prediction = model.predict(input_df)[0]


    st.success(f"🌾 La production estimée de **{produit}** en **{year}** est de : **{prediction:,.2f} tonnes**")
