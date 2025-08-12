import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# =========================
# CONFIGURATION
# =========================
st.set_page_config(page_title="Prévisions & Historique", layout="wide")

st.title("📊 Analyse Historique & Prévisions")

# =========================
# CHARGEMENT DES DONNÉES
# =========================
@st.cache_data
def load_data():
    historique = pd.read_csv("data/dataclean.csv")
    futur = pd.read_csv("data/prediction_2040.csv")

    # Conversion en datetime
    historique['date'] = pd.to_datetime(historique['date'])
    futur['date'] = pd.to_datetime(futur['date'])

    return historique, futur

historique_df, futur_df = load_data()

# =========================
# SIDEBAR - OPTIONS
# =========================
st.sidebar.header("⚙️ Options")

# Choix de la colonne à visualiser
colonnes_dispo = [col for col in historique_df.columns if col != "date"]
colonne_choisie = st.sidebar.selectbox("Choisir la colonne :", colonnes_dispo)

# Lissage (Moyenne Mobile)
lissage = st.sidebar.checkbox("Activer le lissage")
if lissage:
    fenetre = st.sidebar.slider("Fenêtre de lissage (jours) :", 2, 30, 7)

# Sélecteur mode clair/sombre
theme = st.sidebar.radio("Thème graphique :", ["Clair", "Sombre"])

if theme == "Sombre":
    plt.style.use("dark_background")
else:
    plt.style.use("default")

# =========================
# FONCTION GRAPHIQUE
# =========================
def afficher_graphique(df, titre, couleur, nom_fichier):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['date'], df[colonne_choisie], color=couleur, label=colonne_choisie)
    ax.set_title(titre)
    ax.set_xlabel("Date")
    ax.set_ylabel(colonne_choisie)
    ax.legend()
    st.pyplot(fig)

    # Téléchargement PNG
    buf_img = io.BytesIO()
    fig.savefig(buf_img, format="png")
    buf_img.seek(0)
    st.download_button(
        label=f"📥 Télécharger {nom_fichier}.png",
        data=buf_img,
        file_name=f"{nom_fichier}.png",
        mime="image/png"
    )

    # Téléchargement CSV
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Télécharger {nom_fichier}.csv",
        data=csv_data,
        file_name=f"{nom_fichier}.csv",
        mime="text/csv"
    )

# =========================
# SECTION : HISTORIQUE
# =========================
st.subheader("📈 Données Historiques")
min_date_hist = historique_df['date'].min()
max_date_hist = historique_df['date'].max()

date_range_hist = st.slider(
    "Période historique :",
    min_value=min_date_hist,
    max_value=max_date_hist,
    value=(min_date_hist, max_date_hist)
)

historique_filtered = historique_df[
    (historique_df['date'] >= date_range_hist[0]) &
    (historique_df['date'] <= date_range_hist[1])
].copy()

# Lissage
if lissage:
    historique_filtered[colonne_choisie] = historique_filtered[colonne_choisie].rolling(fenetre).mean()

afficher_graphique(historique_filtered, "Données Historiques", "blue", "historique")

# =========================
# SECTION : FUTUR
# =========================
st.subheader("🔮 Prévisions Futures")
min_date_futur = futur_df['date'].min()
max_date_futur = futur_df['date'].max()

date_range_futur = st.slider(
    "Période future :",
    min_value=min_date_futur,
    max_value=max_date_futur,
    value=(min_date_futur, max_date_futur)
)

futur_filtered = futur_df[
    (futur_df['date'] >= date_range_futur[0]) &
    (futur_df['date'] <= date_range_futur[1])
].copy()

# Lissage
if lissage:
    futur_filtered[colonne_choisie] = futur_filtered[colonne_choisie].rolling(fenetre).mean()

afficher_graphique(futur_filtered, "Prévisions Futures", "orange", "futur")
