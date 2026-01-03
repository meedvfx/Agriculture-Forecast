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
- [Structure du Projet](#-structure-du-projet)
- [Installation et Configuration](#-installation-et-configuration)
- [Utilisation](#-utilisation)
- [Auteur](#Auteur)

---

## 📖 Aperçu

L'objectif de ce projet est de fournir aux analystes, agriculteurs et décideurs un outil simple pour visualiser l'évolution des récoltes et anticiper les productions futures jusqu'en **2040**. L'application traite des données historiques, calcule des statistiques clés et génère des prévisions fiables grâce à des modèles de machine learning pré-entraînés.

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
- Design responsive, épuré et moderne.

---

## ⚙️ Technologies Utilisées
- **Langage** : Python 3.9+
- **Interface Web** : Streamlit
- **Analyse de Données** : Pandas, NumPy
- **Visualisation** : Matplotlib, Seaborn, Plotly Express
- **Machine Learning** : Facebook Prophet, Scikit-learn, XGBoost

---

## 📂 Structure du Projet

L'architecture du projet est modulaire pour assurer maintenabilité et évolutivité :

```
Project/
├── app.py                # Point d'entrée de l'application Streamlit
├── utils/                # Bibliothèque de fonctions utilitaires
│   ├── data_loader.py    # Logique de chargement et de nettoyage des données
│   └── plots.py          # Génération des graphiques et visualisations
├── data/                 # Stockage des jeux de données
│   ├── data.csv          # Données historiques de production
│   └── prevision_2040.csv # Données prévisionnelles générées
├── modele/               # Développement et expérimentation des modèles
│   └── model.ipynb       # Notebook Jupyter contenant l'entraînement des modèles
└── requirements.txt      # Liste des dépendances et bibliothèques
```

---

## 🚀 Installation et Configuration

Suivez ces étapes pour lancer le projet en local :

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/meedvfx/Agriculture-Forecast.git
   cd Agriculture-Forecast
   ```

2. **Installer les dépendances** :
   Assurez-vous d'avoir Python installé, puis exécutez :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application** :
   ```bash
   streamlit run app.py
   ```

---

## 🖥️ Utilisation

Une fois l'application lancée, votre navigateur s'ouvrira sur le tableau de bord local.

1. **Barre Latérale** : Utilisez le menu pour naviguer entre "Accueil", "Historique" et "Prévisions".
2. **Historique** : Sélectionnez un produit pour voir sa courbe de production passée.
3. **Prévisions** : Consultez les projections futures et comparez-les aux dernières données connues.

---

## 👨‍💻 Auteur

Ce projet a été développé par **Mohamed ZAHZOUH**.

- 🌍 **LinkedIn** : [Mohamed ZAHZOUH](https://www.linkedin.com/in/mohamed-zahzouh-1402a7318/)
- 📧 **Contact** : [mohamedzahzouh2006@gmail.com](mailto:mohamedzahzouh2006@gmail.com)

---

<center>
  <sub>Réalisé avec ❤️ et Python.</sub>
</center>

