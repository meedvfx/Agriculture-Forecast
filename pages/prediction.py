import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import xgboost as xgb # Nécessaire pour que pickle puisse charger le modèle
import plotly.express as px

# =============================================================================
# Configuration de la page
# =============================================================================
st.set_page_config(
    page_title="Prédiction Avancée de la Production",
    layout="wide",
    page_icon="🌿"
)

st.title("🌿 Prédiction Avancée de la Production Agricole")
st.write("Cette application utilise un modèle prédictif avancé pour estimer la production future en se basant sur les tendances historiques.")
st.divider()

# =============================================================================
# Fonctions de chargement (stables et mises en cache)
# =============================================================================

@st.cache_resource
def load_model():
    """Charge le modèle sauvegardé."""
    try:
        with open("modele/modelagricole.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("ERREUR : Le fichier 'modele/modelagr.pkl' est introuvable.")
        return None
    except Exception as e:
        st.error(f"ERREUR lors du chargement du modèle : {e}")
        return None

@st.cache_data
def load_data():
    """Charge et nettoie les données de manière très sûre."""
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
        data['year'] = pd.to_datetime(data['year'], errors='coerce').dt.year
        data.dropna(subset=['year'], inplace=True)
        data['year'] = data['year'].astype(int)
        data = data[data['Production_Tonnes'] > 0]
        # Tri essentiel pour les calculs temporels
        data = data.sort_values(by=['Filière', 'Produit', 'year'])
        return data
    except Exception as e:
        st.error(f"ERREUR lors de la préparation des données : {e}")
        return None

# Chargement
model = load_model()
df_original = load_data()

if model is None or df_original is None or df_original.empty:
    st.error("L'application ne peut pas démarrer.")
    st.stop()

# =============================================================================
# Interface Utilisateur
# =============================================================================
min_year_in_data = df_original['year'].min()

st.sidebar.header("Veuillez faire vos sélections :")

filieres = sorted(df_original['Filière'].dropna().unique().tolist())
filiere = st.sidebar.selectbox("1. Sélectionnez la filière :", filieres)

if filiere:
    produits_filtres = sorted(df_original[df_original['Filière'] == filiere]['Produit'].dropna().unique().tolist())
    produit = st.sidebar.selectbox("2. Sélectionnez le produit :", produits_filtres)
else:
    st.stop()

current_year = datetime.now().year
last_year_in_data = df_original['year'].max()

selected_year = st.sidebar.number_input(
    "3. Sélectionnez l'année de prédiction :",
    min_value=last_year_in_data + 1,
    max_value=current_year + 30,
    value=last_year_in_data + 1
)

# =============================================================================
# Logique de Prédiction Itérative
# =============================================================================

if st.sidebar.button("🚀 Lancer la prédiction", type="primary"):
    with st.spinner(f"Calcul des prédictions de {last_year_in_data + 1} à {selected_year}..."):
        # On prend une copie des données historiques pour le produit sélectionné
        history_df = df_original[(df_original['Filière'] == filiere) & (df_original['Produit'] == produit)].copy()
        
        # On crée une liste pour stocker les prédictions
        predictions = []

        # Boucle de prédiction année par année
        for year_to_predict in range(last_year_in_data + 1, selected_year + 1):
            # 1. Préparer les caractéristiques pour l'année à prédire
            time_index_value = year_to_predict - min_year_in_data
            
            # 2. Calculer le lag (production de l'année précédente)
            # On prend la dernière valeur de production connue dans notre historique
            lag_1_value = history_df['Production_Tonnes'].iloc[-1]
            
            # 3. Calculer la moyenne mobile des 3 dernières années
            rolling_mean_3_value = history_df['Production_Tonnes'].tail(3).mean()
            
            # 4. Créer le DataFrame d'entrée pour le modèle
            input_data = {
                'Filière': [filiere],
                'Produit': [produit],
                'time_index': [time_index_value],
                'production_lag_1': [lag_1_value],
                'production_rolling_mean_3': [rolling_mean_3_value]
            }
            input_df = pd.DataFrame(input_data)
            
            # 5. Faire la prédiction
            prediction = model.predict(input_df)[0]
            prediction = max(0, prediction) # Assurer une prédiction positive
            
            # 6. Ajouter la prédiction à notre historique pour la prochaine itération
            new_row = pd.DataFrame({
                'Filière': [filiere],
                'Produit': [produit],
                'year': [year_to_predict],
                'Production_Tonnes': [prediction]
            })
            history_df = pd.concat([history_df, new_row], ignore_index=True)
            
            # 7. Sauvegarder la prédiction
            predictions.append({'year': year_to_predict, 'prediction': prediction})

    # Affichage des résultats
    st.header(f"Résultats pour : {produit}")
    
    final_prediction_value = predictions[-1]['prediction']
    st.metric(
        label=f"Production Prédite pour {selected_year}",
        value=f"{final_prediction_value:,.0f} Tonnes".replace(',', ' ')
    )
    
    st.divider()

    # Création d'un DataFrame pour la visualisation
    history_df['Type'] = 'Historique'
    pred_df = pd.DataFrame(predictions)
    pred_df.rename(columns={'prediction': 'Production_Tonnes', 'year': 'year'}, inplace=True)
    pred_df['Type'] = 'Prédiction'
    
    full_chart_df = pd.concat([
        history_df[['year', 'Production_Tonnes', 'Type']],
        pred_df[['year', 'Production_Tonnes', 'Type']]
    ], ignore_index=True)

    # Affichage du graphique
    st.subheader("Visualisation de la Tendance et des Prédictions")
    fig = px.line(
        full_chart_df,
        x='year',
        y='Production_Tonnes',
        color='Type',
        markers=True,
        title=f'Historique et Prédiction de la Production pour {produit}'
    )
    fig.update_layout(xaxis_title="Année", yaxis_title="Production (Tonnes)")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Veuillez sélectionner vos options dans le menu de gauche et cliquer sur 'Lancer la prédiction'.")
