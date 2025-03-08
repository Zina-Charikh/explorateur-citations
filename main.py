from fastapi import FastAPI, Query
import requests
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Création de l'application FastAPI
app = FastAPI()

# Configuration du middleware CORS pour permettre les requêtes de n'importe quelle origine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Autoriser toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Définition de l'URL de l'API Hugging Face et du dataset utilisé
API_URL = "https://datasets-server.huggingface.co/rows"
DATASET_NAME = "Abirate/english_quotes"

# Cache local des citations pour éviter des requêtes répétées
cached_quotes = []
# empêcher plusieurs tâches de modifier le cache en même temps
fetch_lock = asyncio.Lock()

async def fetch_quotes():
      """
    Fonction asynchrone pour récupérer les citations depuis l'API Hugging Face.
    Utilise un cache pour éviter de surcharger l'API avec des requêtes répétées.
    """
    global cached_quotes
    async with fetch_lock:
     # Si les citations sont déjà mises en cache, les retourner directement
        if cached_quotes:
            return cached_quotes

        response = requests.get(f"{API_URL}?dataset={DATASET_NAME}&config=default&split=train&length=100")
        data = response.json()
        # Extraction des citations sous forme de liste de dictionnaires
        cached_quotes = [
            {
                "quote": row["row"].get("quote", ""),
                "author": row["row"].get("author", ""),
                "tags": row["row"].get("tags", [])
            } for row in data.get("rows", [])
        ]
        return cached_quotes

@app.get("/quotes")
async def get_quotes():
       """
    Endpoint pour récupérer la liste complète des citations.
    Retourne les données mises en cache ou les récupère si nécessaire.
    """
    return await fetch_quotes()

@app.get("/quotes/by_tag")
async def get_quotes_by_tag(tag: str = Query(...)):
     """
    Endpoint pour récupérer les citations en fonction d'un tag donné.
    :param tag: Tag recherché (insensible à la casse)
    :return: Liste des citations contenant ce tag
    """
    all_quotes = await fetch_quotes()
    # Filtrer les citations contenant le tag spécifié
    return [q for q in all_quotes if tag.lower() in [t.lower() for t in q.get("tags", [])]]

@app.get("/tags")
async def get_tags():
     """
    Endpoint pour récupérer la liste des tags uniques présents dans les citations.
    :return: Liste triée des tags
    """
    all_quotes = await fetch_quotes()
    # Extraire tous les tags uniques à partir des citations
    tags = {tag for quote in all_quotes for tag in quote.get("tags", [])}
    return sorted(tags)
