import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import xgboost as xgb # Nécessaire pour que pickle puisse charger le modèle
from sklearn.base import BaseEstimator, RegressorMixin # Nécessaire pour la classe personnalisée

# =============================================================================
# DÉFINITION DE LA CLASSE DU MODÈLE PERSONNALISÉ
# =============================================================================
# IMPORTANT : Cette classe doit être définie ici pour que pickle puisse
# charger correctement le modèle qui a été sauvegardé depuis le notebook.
# C'est la solution à l'erreur 'AttributeError'.
class LogTransformedModel(BaseEstimator, RegressorMixin):
    def __init__(self, model):
        self.model = model

    def fit(self, X, y):
        # On transforme la cible avec log1p (log(1+y)) pour gérer les zéros
        y_transformed = np.log1p(y)
        self.model.fit(X, y_transformed)
        return self

    def predict(self, X):
        # On prédit sur l'échelle log
        log_predictions = self.model.predict(X)
        # On retransforme les prédictions à l'échelle originale avec expm1 (exp(x)-1)
        predictions = np.expm1(log_predictions)
        # On s'assure qu'aucune prédiction n'est négative
        return np.maximum(0, predictions)

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

@st.cache_data
def load_data(path):
    """Charge et prépare les données depuis un fichier CSV."""
    try:
        data = pd.read_csv(path)
        data.dropna(subset=['year'], inplace=True)
        data['year'] = data['year'].astype(int)
        return data
    except FileNotFoundError:
        st.error(f"Le fichier de données '{path}' est introuvable.")
        return None

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
# Interface utilisateur (Widgets Streamlit)
# =============================================================================

st.subheader("Veuillez faire vos sélections :")

# 1. Sélection de la filière
filieres = sorted(df['Filière'].dropna().unique().tolist())
filiere = st.selectbox("1. Sélectionnez la filière :", filieres)

# 2. Sélection du produit (filtré par filière)
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

# 3. Sélection de l'année
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
    # Création du DataFrame pour la prédiction avec les bonnes caractéristiques
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
        prediction = model.predict(input_df)[0]

        st.success(f"### Production prédite pour **{produit}** en **{selected_year}** :")
        st.metric(label="Résultat", value=f"{prediction:,.0f} Tonnes".replace(',', ' '))

    except Exception as e:
        st.error("Une erreur est survenue lors de la prédiction.")
        st.error(f"Détails de l'erreur : {e}")
