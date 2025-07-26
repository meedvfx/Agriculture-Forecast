import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime

# =============================================================================
# Configuration de la page
# =============================================================================
st.set_page_config(
    page_title="Prédiction de la Production Agricole",
    layout="centered",
    page_icon="🌿"
)

st.title("🌿 Prédiction de la Production Agricole (en Tonnes)")
st.write("Cette application prédit la quantité produite (en tonnes) selon la filière, le produit et l’année.")
st.divider()

# =============================================================================
# Fonctions de chargement (VERSION STABLE)
# =============================================================================

@st.cache_resource
def load_model():
    """Charge le modèle sauvegardé."""
    try:
        with open("modele/modelagr.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("ERREUR : Le fichier du modèle 'modele/modelagr.pkl' est introuvable.")
        return None
    except Exception as e:
        st.error(f"ERREUR lors du chargement du modèle : {e}")
        return None

@st.cache_data
def load_data():
    """Charge et nettoie les données de manière sûre."""
    paths_to_try = ["dataagr.csv", "data/dataagr.csv"]
    data = None
    
    for path in paths_to_try:
        try:
            data = pd.read_csv(path)
            st.success(f"Fichier de données '{path}' chargé avec succès.")
            break
        except FileNotFoundError:
            continue

    if data is None:
        st.error("ERREUR : Fichier de données 'dataagr.csv' introuvable.")
        return None
    
    # La conversion de type pour la colonne 'year' a été retirée
    # On suppose que le fichier CSV est propre, comme dans le notebook.
    return data

# Chargement
model = load_model()
df = load_data()

if model is None or df is None or df.empty:
    st.error("L'application ne peut pas démarrer.")
    st.stop()

# =============================================================================
# Interface Utilisateur
# =============================================================================
min_year = df['year'].min()

st.subheader("Veuillez faire vos sélections :")

filieres = sorted(df['Filière'].dropna().unique().tolist())
filiere = st.selectbox("1. Sélectionnez la filière :", filieres)

if filiere:
    produits_filtres = sorted(df[df['Filière'] == filiere]['Produit'].dropna().unique().tolist())
    produit = st.selectbox("2. Sélectionnez le produit :", produits_filtres)
else:
    st.stop()

current_year = datetime.now().year
selected_year = st.number_input(
    "3. Sélectionnez l'année de prédiction :",
    min_value=min_year,
    max_value=current_year + 30,
    value=current_year
)

# =============================================================================
# Prédiction
# =============================================================================

if st.button("🚀 Lancer la prédiction", type="primary"):
    # Préparation des données pour le modèle, exactement comme dans le notebook
    time_index_value = selected_year - min_year

    input_data = {
        'Filière': [filiere],
        'Produit': [produit],
        'year': [selected_year], # Le modèle a besoin de 'year'
        'time_index': [time_index_value] # Le modèle a besoin de 'time_index'
    }
    input_df = pd.DataFrame(input_data)

    st.write("---")
    st.write("Données envoyées au modèle :")
    st.dataframe(input_df)

    try:
        # Prédiction directe
        prediction = model.predict(input_df)[0]
        prediction = max(0, prediction) # S'assurer de ne pas avoir de résultat négatif

        st.success(f"### Production prédite pour **{produit}** en **{selected_year}** :")
        st.metric(label="Résultat", value=f"{prediction:,.0f} Tonnes".replace(',', ' '))

    except Exception as e:
        st.error(f"Une erreur est survenue lors de la prédiction : {e}")
