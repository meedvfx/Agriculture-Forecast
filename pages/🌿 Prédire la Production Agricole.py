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
st.write("Cette application utilise un modèle de Machine Learning avancé pour prédire la **quantité produite (en tonnes)**.")
st.divider()

# =============================================================================
# Fonctions de chargement (VERSION LA PLUS ROBUSTE)
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
    """Charge et nettoie les données de manière très sûre."""
    # Tente de trouver le fichier à plusieurs emplacements communs
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
    
    try:
        # --- Nettoyage final et garanti de la colonne 'year' ---
        # 1. Convertit en format date, les erreurs deviennent invalides (NaT)
        data['year'] = pd.to_datetime(data['year'], errors='coerce')
        # 2. Supprime les lignes avec des dates invalides
        data.dropna(subset=['year'], inplace=True)
        # 3. Extrait l'année et la convertit en entier (maintenant sans risque)
        data['year'] = data['year'].dt.year.astype(int)
        return data
    except Exception as e:
        st.error(f"ERREUR lors de la préparation des données : {e}")
        return None

# Chargement
model = load_model()
df = load_data()

# Arrêt de l'application si le chargement échoue
if model is None or df is None or df.empty:
    st.error("L'application ne peut pas démarrer en raison d'une erreur de chargement.")
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
    min_value=int(min_year),
    max_value=current_year + 30,
    value=current_year
)

# =============================================================================
# Prédiction
# =============================================================================

if st.button("🚀 Lancer la prédiction", type="primary"):
    # Préparation des données pour le modèle
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
    st.write("Données envoyées au modèle :")
    st.dataframe(input_df)

    try:
        # 1. Le modèle prédit la valeur logarithmique
        log_prediction = model.predict(input_df)[0]
        # 2. On applique la transformation inverse (exponentielle)
        final_prediction = np.expm1(log_prediction)
        # 3. On s'assure que le résultat est positif
        final_prediction = max(0, final_prediction)

        st.success(f"### Production prédite pour **{produit}** en **{selected_year}** :")
        st.metric(label="Résultat", value=f"{final_prediction:,.0f} Tonnes".replace(',', ' '))

    except Exception as e:
        st.error(f"Une erreur est survenue lors de la prédiction : {e}")
