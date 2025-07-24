import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import xgboost as xgb # Nécessaire pour que pickle puisse charger le modèle

# =============================================================================
# Configuration de la page
# =============================================================================
st.set_page_config(
    page_title="Prédiction de la Production Agricole",
    layout="centered",
    page_icon="🌿"
)

st.title("🌿 Prédiction de la Production Agricole (en Tonnes)")
st.write("Cette application utilise un modèle de Machine Learning avancé pour prédire la **quantité produite (en tonnes)** selon la **filière**, le **produit** et l’**année** sélectionnée.")
st.divider()

# =============================================================================
# Chargement du modèle et des données (VERSION FINALE ROBUSTE)
# =============================================================================

@st.cache_resource
def load_model():
    """Charge le pipeline de modèle sauvegardé."""
    try:
        with open("modele/modelagr.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("Le fichier du modèle 'modele/modelagr.pkl' n'a pas été trouvé. Assurez-vous d'avoir exécuté le notebook d'entraînement final.")
        return None
    except Exception as e:
        st.error(f"Une erreur est survenue lors du chargement du modèle : {e}")
        return None

@st.cache_data
def load_data():
    """
    Charge et prépare les données depuis un fichier CSV de manière très robuste.
    Tente de trouver le fichier de données à plusieurs emplacements.
    """
    paths_to_try = ["dataagr.csv", "data/dataagr.csv"]
    data = None
    loaded_path = None

    for path in paths_to_try:
        try:
            data = pd.read_csv(path)
            loaded_path = path
            break 
        except FileNotFoundError:
            continue

    if data is None:
        st.error(f"Fichier de données introuvable. Assurez-vous que 'dataagr.csv' se trouve dans le dossier principal ou dans un sous-dossier 'data'.")
        return None
    
    st.success(f"Fichier de données chargé avec succès depuis : '{loaded_path}'")

    try:
        # --- Nettoyage robuste de la colonne 'year' (identique au notebook) ---
        data['year'] = pd.to_datetime(data['year'], errors='coerce')
        data.dropna(subset=['year'], inplace=True)
        data['year'] = data['year'].dt.year.astype(int)
        return data
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la préparation des données : {e}")
        return None

# Chargement des données et du modèle
model = load_model()
df = load_data()

if model is None or df is None or df.empty:
    st.error("Le chargement des données ou du modèle a échoué. L'application ne peut pas continuer.")
    st.stop()

# =============================================================================
# Calcul de l'année minimale pour le 'time_index'
# =============================================================================
min_year = df['year'].min()

# =============================================================================
# Interface utilisateur
# =============================================================================

st.subheader("Veuillez faire vos sélections :")

filieres = sorted(df['Filière'].dropna().unique().tolist())
filiere = st.selectbox("1. Sélectionnez la filière :", filieres)

if filiere:
    produits_filtres = sorted(df[df['Filière'] == filiere]['Produit'].dropna().unique().tolist())
    if not produits_filtres:
        st.warning("Aucun produit disponible pour cette filière.")
        produit = None
    else:
        produit = st.selectbox("2. Sélectionnez le produit :", produits_filtres)
else:
    produit = None

if not produit:
    st.stop()

current_year = datetime.now().year
selected_year = st.number_input(
    "3. Sélectionnez l'année de prédiction :",
    min_value=int(min_year),
    max_value=current_year + 30, # Augmentation de la portée
    value=current_year
)

# =============================================================================
# Prédiction
# =============================================================================

if st.button("🚀 Lancer la prédiction", type="primary"):
    time_index_value = selected_year - min_year
    time_index_sq_value = time_index_value ** 2

    input_data = {
        'Filière': [filiere],
        'Produit': [produit],
        'time_index': [time_index_value],
        'time_index_sq': [time_index_sq_value]
    }
    input_df = pd.DataFrame(input_data)

    st.write("---")
    st.write("Données envoyées au modèle pour prédiction :")
    st.dataframe(input_df)

    try:
        # Le modèle a été entraîné sur le log de la production
        # Il faut donc appliquer la transformation inverse (exponentielle)
        log_prediction = model.predict(input_df)[0]
        final_prediction = np.expm1(log_prediction)
        final_prediction = max(0, final_prediction) # S'assurer de ne pas avoir de résultat négatif

        st.success(f"### Production prédite pour **{produit}** en **{selected_year}** :")
        st.metric(label="Résultat", value=f"{final_prediction:,.0f} Tonnes".replace(',', ' '))

    except Exception as e:
        st.error("Une erreur est survenue lors de la prédiction.")
        st.error(f"Détails de l'erreur : {e}")
