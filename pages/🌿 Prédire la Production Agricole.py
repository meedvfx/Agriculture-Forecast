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
# Chargement du modèle et des données
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
def load_data(path):
    """Charge et prépare les données depuis un fichier CSV de manière robuste."""
    try:
        data = pd.read_csv(path)
        # --- Nettoyage robuste de la colonne 'year' (CORRECTION FINALE) ---
        # Cette méthode est la plus sûre pour gérer les formats de date variés.
        # 1. Tente de convertir la colonne en format date. Les erreurs deviendront NaT (Not a Time).
        data['year'] = pd.to_datetime(data['year'], errors='coerce')
        
        # 2. Supprime les lignes où la conversion a échoué (valeur NaT).
        data.dropna(subset=['year'], inplace=True)
        
        # 3. Extrait l'année de la date et la convertit en entier.
        data['year'] = data['year'].dt.year.astype(int)
        return data
    except FileNotFoundError:
        st.error(f"Le fichier de données '{path}' est introuvable. Vérifiez que le fichier se trouve bien dans un dossier nommé 'data'.")
        return None
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la lecture des données : {e}")
        return None

# Correction du chemin d'accès pour correspondre à la structure de votre projet
model = load_model()
df = load_data("data/dataagr.csv")

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
    max_value=current_year + 20,
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
        # 1. Prédire la valeur transformée (logarithmique)
        log_prediction = model.predict(input_df)[0]
        
        # 2. Appliquer la transformation inverse pour obtenir la valeur réelle
        final_prediction = np.expm1(log_prediction)
        
        # 3. S'assurer que le résultat n'est pas négatif
        final_prediction = max(0, final_prediction)

        st.success(f"### Production prédite pour **{produit}** en **{selected_year}** :")
        st.metric(label="Résultat", value=f"{final_prediction:,.0f} Tonnes".replace(',', ' '))

    except Exception as e:
        st.error("Une erreur est survenue lors de la prédiction.")
        st.error(f"Détails de l'erreur : {e}")
