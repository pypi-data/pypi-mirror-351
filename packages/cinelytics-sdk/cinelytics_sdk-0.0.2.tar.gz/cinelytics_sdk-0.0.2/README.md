
# 🎬 MovieLens SDK - `cinelytics_sdk`

cinelytics-sdk est un SDK Python léger et intuitif conçu pour faciliter l’interaction avec l’API REST **MovieLens**.
Il offre une interface simple et efficace pour accéder aux données de films, notes et autres informations clés, sans avoir à gérer directement les requêtes HTTP.

Ce SDK est particulièrement adapté aux **Data Analysts**, **Data Scientists** et **développeurs Python** qui souhaitent intégrer facilement des **données cinématographiques** dans leurs analyses, projets de machine learning ou applications.

Grâce à une prise en charge native des objets **Pydantic** pour la validation et la gestion des modèles, ainsi que la possibilité d’obtenir les résultats sous forme de **dictionnaires** ou de **DataFrames Pandas**, cinelytics-sdk s’adapte parfaitement à différents **workflows**, qu’il s’agisse de prototypage rapide, de **traitement de données** ou de **visualisation avancée**.

[![PyPI version](https://badge.fury.io/py/cinelytics_sdk.svg)](https://badge.fury.io/py/cinelytics_sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

##  Installation

```bash
pip install cinelytics_sdk
```

---

## ⚙️ Configuration de base

```python
from cinelytics_sdk import MovieClient, MovieConfig

# API distante (Render)
config = MovieConfig(movie_base_url="https://cinema-insights.onrender.com")
client = MovieClient(config=config)
```

---

## ✅ Fonctionnalités du SDK

### 1. Vérification de l’état de l’API

```python
client.health_check()
# Retour attendu : {"status": "ok"}
```

### 2. Récupérer un film par ID

```python
movie = client.get_movie(1)
print(movie.title)
```

### 3. Lister les films (format DataFrame)

```python
df = client.list_movies(limit=5, output_format="pandas")
print(df.head())
```

---

## 🔄 Formats de sortie disponibles

Toutes les méthodes de liste (`list_movies`, `list_ratings`, etc.) peuvent retourner :

- des objets **Pydantic** (par défaut)
- des **dictionnaires Python**
- des **DataFrames Pandas**

```python
client.list_movies(limit=10, output_format="dict")
client.list_ratings(limit=10, output_format="pandas")
```

---

## 🧪 Tester en local avec Docker

### 🔗 Utiliser l’API locale

Vous pouvez aussi utiliser une API locale :

```python
config = MovieConfig(movie_base_url="http://localhost:8000")
client = MovieClient(config=config)
```

---

## 👥 Public cible

- Data Analysts  
- Data Scientists  
- Étudiants & passionnés de Data  
- Développeurs Python

---

## 📄 Licence

Distribué sous licence MIT.  
[En savoir plus](https://opensource.org/licenses/MIT)

---

## 🔗 Liens utiles

- 🌍 API (Render) : [https://cinema-insights.onrender.com](https://cinema-insights.onrender.com)
- 📦 PyPI : [https://pypi.org/project/cinelytics-sdk](https://pypi.org/project/cinelytics-sdk)

---

ℹ️ Note : l’API hébergée sur Render peut mettre quelques secondes à démarrer si elle est en veille.
