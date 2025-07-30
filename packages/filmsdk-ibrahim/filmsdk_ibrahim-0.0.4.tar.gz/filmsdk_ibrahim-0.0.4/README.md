# MovieLens SDK - `filmsdk_ibrahim`

A simple Python SDK to interact with the MovieLens REST API. It is designed for Data Analysts and Data Scientists, with native support for Pydantic, dictionaries, and Pandas DataFrames.

---

## Installation

```bash
pip install filmsdk_ibrahim
```

---

## Configuration to test on local machine

```python
from filmsdk_ibrahim import MovieClient, MovieConfig

# Configuration with your API URL (local via docker)
config = MovieConfig(movie_base_url="http://localhost:5050")
client = MovieClient(config=config)
```

---

## Test SDK

### 1. Health check

```python
client.health_check()
# Retourn : {"status": "ok"}
```

### 2. Get a film

```python
movie = client.get_movie(1)
print(movie.title)
```

### 3. List of films in DataFrame format

```python
df = client.list_movies(limit=5, output_format="pandas")
print(df.head())
```

---

## Available output modes

All listing methods (list_movies, list_ratings, etc.) can return:

Pydantic objects (default)

Dictionaries

Pandas DataFrames

Example :

```python
client.list_movies(limit=10, output_format="dict")
client.list_ratings(limit=10, output_format="pandas")
```

---

## Liens utiles

- PyPI : [https://pypi.org/project/filmsdk-ibrahim/0.0.3/](https://pypi.org/project/filmsdk-ibrahim/0.0.3/)