# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 14:49:53 2025

@author: meedz
"""

import streamlit as st
#####################################################################################################

#les variables#########

image = 'C:/Users/meedz/Desktop/Stage/site/data/logo.jpg'

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

## 🎯 Objectif du projet d’analyse & prédiction des prix

Cette application permet de :

- Visualiser l'évolution des prix des produits alimentaires par ville et par année.
- Prédire les prix futurs avec un modèle d’intelligence artificielle.
- Comparer les prix entre différentes villes.
- Mettre à disposition un outil interactif et simple d’utilisation pour les équipes d’analyse ou de gestion.

---

## 🛠️ Bénéfices du projet pour i‑Soft Network

""")


# Premier tableau : Bénéfices
data_benefices = {
    "Axe stratégique": [
        "Audit & Conseil",
        "Amélioration de la prise de décision",
        "Veille économique avancée",
        "Digitalisation"
    ],
    "Apport du projet": [
        "Analyses de données économiques pour le conseil stratégique",
        "Permettre aux équipes internes ou aux partenaires d'accéder à des indicateurs fiables et automatisés",
        "Offrir aux clients des analyses précises de l'évolution des prix par région et par année",
        "Outil intelligent facilitant la prise de décision basée sur la data"
    ]
}

st.dataframe(data_benefices)


# Deuxième tableau : Fonctionnalités principales
st.write("## 📊 Fonctionnalités principales de l’application")

data_fonctionnalites = {
    "Fonctionnalité": [
        "Prédiction du prix par produit, ville et date",
        "Visualisation des tendances annuelles",
        "Analyse comparative entre deux villes",
        "Identification des produits les plus chers",
        "Exploration de la distribution des prix"
    ],
    "Description": [
        "Estimation du prix futur grâce à un modèle prédictif",
        "Graphiques montrant l'évolution du prix par année",
        "Comparer les prix moyens entre deux villes sélectionnées",
        "Classement des 10 produits les plus chers",
        "Analyse statistique de la répartition des prix"
    ]
}

st.dataframe(data_fonctionnalites)















