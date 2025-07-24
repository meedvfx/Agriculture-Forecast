import streamlit as st
import pandas as pd
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
st.write("Cette application utilise un modèle de Machine Learning avancé pour prédire la **quantité produite (en tonnes)** selon la **filière**, le **produit** et l’**année** sélectionnée.")
st.divider()

# =============================================================================
# Chargement du modèle et des données
# =============================================================================

# Utiliser le cache pour ne charger le modèle qu'une seule fois
@st.cache_resource
def load_model():
    """Charge le pipeline de modèle sauvegardé."""
    try:
        with open("modele/modelagr.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("Le fichier du modèle 'modele/modelagr.pkl' n'a pas été trouvé. Assurez-vous d'avoir exécuté le notebook d'entraînement.")
        return None

# Utiliser le cache pour ne charger les données qu'une seule fois
@st.cache_data
def load_data(path):
    """Charge et prépare les données depuis un fichier CSV."""
    try:
        data = pd.read_csv(path)
        # --- Nettoyage robuste de la colonne 'year' (CORRIGÉ) ---
        # La colonne 'year' contient des dates complètes (ex: '2011-01-01').
        # On la convertit en format datetime, puis on extrait l'année.
        data['year'] = pd.to_datetime(data['year'], errors='coerce')
        # Supprime les lignes où la date est invalide
        data.dropna(subset=['year'], inplace=True)
        # On garde uniquement l'année (ex: 2011) et on la convertit en entier
        data['year'] = data['year'].dt.year.astype(int)
        return data
    except FileNotFoundError:
        st.error(f"Le fichier de données '{path}' est introuvable.")
        return None

# Correction du chemin d'accès au fichier de données
model = load_model()
df = load_data("dataagr.csv")

# Si le chargement a échoué, on arrête l'application
if model is None or df is None or df.empty:
    st.error("Le chargement des données a échoué ou le fichier est vide après nettoyage. L'application ne peut pas continuer.")
    st.stop()

# =============================================================================
# Calcul de l'année minimale pour le 'time_index'
# =============================================================================
# Cette valeur est cruciale car elle doit être la même que celle utilisée pendant l'entraînement.
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
    st.warning("Veuillez d'abord sélectionner une filière.")
    produit = None

# On arrête si aucun produit n'est sélectionné
if not produit:
    st.stop()


# 3. Sélection de l'année
current_year = datetime.now().year
selected_year = st.number_input(
    "3. Sélectionnez l'année de prédiction :",
    min_value=int(min_year),
    max_value=current_year + 20, # Permet de prédire 20 ans dans le futur
    value=current_year
)

# =============================================================================
# Prédiction
# =============================================================================

if st.button("🚀 Lancer la prédiction", type="primary"):
    # Création du DataFrame pour la prédiction avec les bonnes caractéristiques
    # Le modèle attend 'time_index' ET 'time_index_sq'
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
        # Le modèle attend un DataFrame avec les colonnes correspondantes
        prediction = model.predict(input_df)[0]

        st.success(f"### Production prédite pour **{produit}** en **{selected_year}** :")
        # Formatage du nombre pour une meilleure lisibilité
        st.metric(label="Résultat", value=f"{prediction:,.0f} Tonnes".replace(',', ' '))

    except Exception as e:
        st.error("Une erreur est survenue lors de la prédiction.")
        st.error(f"Détails de l'erreur : {e}")
