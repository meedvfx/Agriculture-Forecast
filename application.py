import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Chargement des données
# =========================
@st.cache_data
def load_data():
    df_hist = pd.read_csv("data/dataclean.csv")
    df_fut = pd.read_csv("data/prediction_2040.csv")

    # Conversion date
    for col in ["Date", "date", "DATE"]:
        if col in df_hist.columns:
            df_hist[col] = pd.to_datetime(df_hist[col])
            df_hist.rename(columns={col: "Date"}, inplace=True)
        if col in df_fut.columns:
            df_fut[col] = pd.to_datetime(df_fut[col])
            df_fut.rename(columns={col: "Date"}, inplace=True)

    return df_hist, df_fut


# =========================
# Graphique Matplotlib
# =========================
def plot_timeseries(df, title, y_label, color):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Date"], df["Valeur"], color=color, linewidth=2)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)


# =========================
# Sidebar Navigation
# =========================
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Aller à :", ["Historique", "Prévisions futures", "Analyse détaillée"])

# Charger data
df_hist, df_fut = load_data()

# Harmonisation colonnes
if "Produit" not in df_hist.columns:
    st.error("La colonne 'Produit' est absente du fichier historique.")
if "Production_tonnes" not in df_hist.columns:
    st.error("La colonne 'Valeur' est absente du fichier historique.")

# =========================
# PAGE 1 - Historique
# =========================
if page == "Historique":
    st.title("📈 Données Historiques")

    produits = df_hist["Produit"].unique()
    produit_select = st.selectbox("Choisir un produit :", produits)

    # Filtrer
    df_filtre = df_hist[df_hist["Produit"] == produit_select]

    # Sélection plage de dates
    min_date, max_date = df_filtre["Date"].min(), df_filtre["Date"].max()
    date_range = st.slider("Plage de dates :", min_value=min_date, max_value=max_date, value=(min_date, max_date))
    df_filtre = df_filtre[(df_filtre["Date"] >= date_range[0]) & (df_filtre["Date"] <= date_range[1])]

    # Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Nombre de points", len(df_filtre))
    col2.metric("📊 Valeur moyenne", f"{df_filtre['Valeur'].mean():.2f}")
    col3.metric("📈 Valeur max", f"{df_filtre['Valeur'].max():.2f}")

    # Graphique
    plot_timeseries(df_filtre, f"Historique - {produit_select}", "Valeur", "blue")

    # Téléchargement
    st.download_button("📥 Télécharger données filtrées", df_filtre.to_csv(index=False), file_name="historique_filtre.csv")

# =========================
# PAGE 2 - Prévisions futures
# =========================
elif page == "Prévisions futures":
    st.title("🔮 Prévisions Futures (jusqu'en 2040)")

    produits = df_fut["Produit"].unique()
    produit_select = st.selectbox("Choisir un produit :", produits)

    df_filtre = df_fut[df_fut["Produit"] == produit_select]

    # Stats
    col1, col2 = st.columns(2)
    col1.metric("📅 Nombre de prévisions", len(df_filtre))
    col2.metric("📊 Valeur moyenne prévue", f"{df_filtre['Valeur'].mean():.2f}")

    # Graphique
    plot_timeseries(df_filtre, f"Prévisions - {produit_select}", "Valeur prévue", "orange")

    # Téléchargement
    st.download_button("📥 Télécharger prévisions", df_filtre.to_csv(index=False), file_name="previsions_2040.csv")

# =========================
# PAGE 3 - Analyse détaillée
# =========================
elif page == "Analyse détaillée":
    st.title("📊 Analyse Détaillée")

    produits_communs = list(set(df_hist["Produit"].unique()) & set(df_fut["Produit"].unique()))
    produit_select = st.selectbox("Choisir un produit :", produits_communs)

    df_hist_p = df_hist[df_hist["Produit"] == produit_select]
    df_fut_p = df_fut[df_fut["Produit"] == produit_select]

    st.subheader("Historique")
    plot_timeseries(df_hist_p, f"Historique - {produit_select}", "Valeur", "blue")

    st.subheader("Prévisions futures")
    plot_timeseries(df_fut_p, f"Prévisions futures - {produit_select}", "Valeur prévue", "orange")

    # Comparaison statistiques
    st.subheader("📈 Comparaison statistiques")
    stats_df = pd.DataFrame({
        "Période": ["Historique", "Futures"],
        "Moyenne": [df_hist_p["Valeur"].mean(), df_fut_p["Valeur"].mean()],
        "Max": [df_hist_p["Valeur"].max(), df_fut_p["Valeur"].max()],
        "Min": [df_hist_p["Valeur"].min(), df_fut_p["Valeur"].min()],
    })
    st.dataframe(stats_df)

    st.download_button("📥 Télécharger comparaison", stats_df.to_csv(index=False), file_name="comparaison.csv")
