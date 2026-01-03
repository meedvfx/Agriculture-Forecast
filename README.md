# 🌱 Agriculture Forecast — Prédiction de Production Agricole

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agriculture-forecast.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Prophet-orange)

Bienvenue sur **Agriculture Forecast**, une application interactive de tableau de bord conçue pour analyser les productions agricoles historiques et prédire les tendances futures grâce à l'intelligence artificielle.

Ce projet utilise **Facebook Prophet** pour les modèles de séries temporelles et **Streamlit** pour une interface utilisateur fluide et réactive.

---

## 📑 Table des Matières

- [Aperçu](#-aperçu)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Démo et Aperçu](#-démo-et-aperçu)
- [Technologies Utilisées](#-technologies-utilisées)
- [Installation et Configuration](#-installation-et-configuration)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [Auteur](#-auteur)

---

## 📖 Aperçu

L'objectif de ce projet est de fournir aux analystes, agriculteurs et décideurs un outil simple pour visualiser l'évolution des récoltes et anticiper les productions futures jusqu'en **2040**. L'application traite des données historiques, calcule des statistiques clés et génère des prévisions fiables.

---

## 🚀 Fonctionnalités Principales

### 📊 1. Analyse Historique
- **Filtrage Dynamique** : Sélectionnez un produit spécifique ou visualisez l'ensemble des données.
- **Plage Temporelle** : Ajustez la période d'analyse via un curseur interactif.
- **Indicateurs Clés** : Affichage immédiat de la moyenne, du minimum et du maximum de production.
- **Visualisation** : Graphiques clairs générés avec Matplotlib.
- **Export** : Téléchargement des graphiques en PNG et des données filtrées en CSV.

### 🔮 2. Prédictions Futures (IA)
- **Modélisation Avancée** : Utilisation de l'algorithme Prophet pour projeter les tendances jusqu'en 2040.
- **Comparaison** : Analyse comparative automatique entre les dernières données réelles et les premières prévisions.
- **Export de Prévisions** : Récupérez les données prédictives pour vos propres rapports.

### 🖥️ 3. Interface Intuitive
- Navigation fluide via une barre latérale.
- Design responsive et épuré.

---

## 🛠 Technologies Utilisées

Ce projet repose sur une stack Python robuste orientée Data Science :

- **Streamlit** : Framework pour créer l'application web interactive.
- **Pandas** : Manipulation et nettoyage des données.
- **Prophet** : Moteur de prévision de séries temporelles.
- **Matplotlib** : Génération des graphiques statistiques.
- **NumPy** : Calculs scientifiques performants.

---

## 📥 Installation et Configuration

Pour exécuter ce projet localement, suivez ces étapes :

### 1. Cloner le dépôt
```bash
git clone https://github.com/meedvfx/Agriculture-Forecast.git
cd Agriculture-Forecast
```

### 2. Créer un environnement virtuel (Recommandé)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

---

## ▶️ Utilisation

Une fois l'installation terminée, lancez l'application avec la commande suivante :

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut (généralement à l'adresse `http://localhost:8501`).

---

## 📂 Structure du Projet

```plaintext
Agriculture-Forecast/
├── data/
│   ├── data.csv                 # Données historiques brutes
│   └── prevision_2040.csv       # Données prédites par le modèle
├── .git/                        # Gestion de version
├── app.py                       # Point d'entrée de l'application Streamlit
├── requirements.txt             # Liste des dépendances Python
└── README.md                    # Documentation du projet
```

---

## 👨‍💻 Auteur

Ce projet a été développé par **Mohamed ZAHZOUH**.

- 🌍 **LinkedIn** : [Mohamed ZAHZOUH](https://www.linkedin.com/in/mohamed-zahzouh-1402a7318/)
- 📧 **Contact** : [mohamedzahzouh2006@gmail.com](mailto:mohamedzahzouh2006@gmail.com)

---

<center>
  <sub>Réalisé avec ❤️ et Python.</sub>
</center>
