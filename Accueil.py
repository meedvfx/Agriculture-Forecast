# -*- coding: utf-8 -*-
"""

@author: meedvfx
"""

import streamlit as st
#####################################################################################################

#les variables#########

image = 'data/logo.jpg'

############################################################################

st.set_page_config(page_title='i Soft Network', page_icon="data:image/svg+xml,%3csvg stroke-width='1.75' id='Layer_1' data-name='Layer 1' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3e%3cdefs%3e%3cstyle%3e.cls-daxkepcpz6c2pmq4n5s20h-1%7bfill:none%3bstroke:%23FC0F0F%3bstroke-miterlimit:10%3b%3b%7d%3c/style%3e%3c/defs%3e%3cpolyline class='cls-daxkepcpz6c2pmq4n5s20h-1' points='1 12 12 2.83 23 12'/%3e%3cpolyline class='cls-daxkepcpz6c2pmq4n5s20h-1' points='19.33 9.25 19.33 21.17 14.75 21.17 14.75 13.83 9.25 13.83 9.25 21.17 4.67 21.17 4.67 9.25'/%3e%3c/svg%3e", layout="centered",initial_sidebar_state="auto", menu_items=None)

st.image(image, caption="Logo De L'entreprise", width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto", use_container_width=False)
 
st.link_button("Site De L'entreprise", "https://i-softnetwork.com/", help=None, type="primary", icon=None, disabled=False, use_container_width=False)


st.title("🏢 Bienvenue chez **i‑Soft Network**")
st.subheader("📍 Kénitra, Maroc")

st.write("""
**i‑Soft Network** est une entreprise spécialisée dans le développement de solutions informatiques, le conseil, l’audit et la vente de matériel.  
Notre mission : accompagner les entreprises marocaines dans leur transformation numérique et leur gestion de systèmes d’information.

---

## 🎯 Objectifs Globaux

Cette application permet de :

- Centraliser l'information économique et agricole pour une analyse unifiée.
- Fournir des outils de prédiction fiables pour la prise de décision stratégique.
- Favoriser la veille économique territoriale par indicateurs régionaux et nationaux.
- Soutenir la digitalisation du secteur agricole et la gestion intelligente des données.
""")


# ▶️ Bénéfices du projet (double module)
st.write("## 🛠️ Bénéfices du projet pour i‑Soft Network")

data_benefices = {
    "Axe stratégique": [
        "Audit & Conseil",
        "Amélioration de la prise de décision",
        "Veille économique avancée",
        "Digitalisation"
    ],
    "Apport du projet": [
        "Analyses économiques basées sur les prix et la production agricole pour un conseil stratégique approfondi",
        "Accès à des indicateurs fiables : production par produit/année/ville et évolution des prix",
        "Observation croisée de l’offre agricole et des tendances de consommation",
        "Application intelligente unifiant données de production et prix pour une gestion optimisée"
    ]
}

st.dataframe(data_benefices)

# ▶️ Fonctionnalités principales des deux modules
st.write("## 📊 Fonctionnalités principales des applications")

data_fonctionnalites = {
    "Fonctionnalité": [
        "Prédiction du prix par produit, ville et date",
        "Visualisation des tendances de prix annuelles",
        "Analyse comparative des prix entre deux villes",
        "Classement des produits les plus chers",
        "Exploration de la distribution des prix",
        "Visualisation de la production agricole par région",
        "Analyse de l’évolution de la production par année",
        "Comparaison de production entre plusieurs produits ou régions"
    ],
    "Description": [
        "Estimation du prix futur grâce à un modèle prédictif (IA)",
        "Graphiques montrant l'évolution des prix dans le temps",
        "Comparer les prix moyens entre deux villes sélectionnées",
        "Identifier les 10 produits les plus chers par an ou par ville",
        "Analyse statistique de la répartition des prix alimentaires",
        "Afficher les quantités produites selon produit/région/année",
        "Observer les variations interannuelles de production",
        "Comparer visuellement la production entre plusieurs zones"
    ]
}

st.dataframe(data_fonctionnalites)
