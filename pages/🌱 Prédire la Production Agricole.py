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
st.write("Cette application permet de prédire la **quantité produite (en tonnes)** selon la **filière**, le **produit** et l’**année** sélectionnée, en utilisant un modèle de Machine Learning.")
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
    """Charge les données depuis un fichier CSV."""
    try:
        data = pd.read_csv(path)
        return data
    except FileNotFoundError:
        st.error(f"Le fichier de données '{path}' est introuvable.")
        return None

model = load_model()
df = load_data("data/dataagr.csv")

# Si le chargement a échoué, on arrête l'application
if model is None or df is None:
    st.stop()

# =============================================================================
# Section de Débogage des Données
# =============================================================================
with st.expander("🔍 Informations de débogage des données (Étape 1)"):
    st.write("### Après le chargement initial du CSV :")
    st.write("**Colonnes détectées :**", df.columns.tolist())
    st.write("**Premières 5 lignes du DataFrame :**")
    st.dataframe(df.head())
    st.write(f"**Nombre total de lignes :** {len(df)}")

# =============================================================================
# Nettoyage et préparation des données - ÉTAPE CRUCIALE
# =============================================================================
rows_before_cleaning = len(df)
# S'assurer que la colonne 'year' est de type numérique et sans erreurs.
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df.dropna(subset=['year'], inplace=True)
df['year'] = df['year'].astype(int)
rows_after_cleaning = len(df)

# =============================================================================
# Section de Débogage (Après Nettoyage)
# =============================================================================
with st.expander("🔍 Informations de débogage des données (Étape 2)"):
    st.write("### Après le nettoyage de la colonne 'year' :")
    st.write(f"**Lignes avant nettoyage :** {rows_before_cleaning}")
    st.write(f"**Lignes après nettoyage :** {rows_after_cleaning}")
    st.write("**Premières 5 lignes du DataFrame après nettoyage :**")
    st.dataframe(df.head())
st.divider()

# Le modèle a été entraîné avec 'time_index' (year - min_year).
# Nous devons reproduire ce calcul pour la prédiction.
if df.empty:
    st.error("Le DataFrame est vide après le nettoyage. Impossible de continuer. Veuillez vérifier la colonne 'year' de votre fichier CSV.")
    st.stop()
    
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
        st.stop()
    produit = st.selectbox("2. Sélectionnez le produit :", produits_filtres)
else:
    st.warning("Veuillez d'abord sélectionner une filière.")
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
    # Création du DataFrame pour la prédiction avec les bonnes colonnes
    time_index_value = selected_year - min_year

    input_data = {
        'Filière': [filiere],
        'Produit': [produit],
        'time_index': [time_index_value] # Utiliser 'time_index'
    }
    input_df = pd.DataFrame(input_data)

    st.write("---")
    st.write("Données envoyées au modèle pour prédiction :")
    st.dataframe(input_df)

    try:
        # Le modèle attend un DataFrame avec les colonnes 'Filière', 'Produit', 'time_index'
        prediction = model.predict(input_df)[0]

        st.success(f"### Production prédite pour **{produit}** en **{selected_year}** :")
        st.metric(label="Résultat", value=f"{prediction:,.0f} Tonnes".replace(',', ' '))

    except Exception as e:
        st.error("Une erreur est survenue lors de la prédiction.")
        st.error(f"Détails de l'erreur : {e}")
