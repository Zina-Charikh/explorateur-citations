from fastapi import FastAPI, Query
import requests
from fastapi.middleware.cors import CORSMiddleware
import re
import asyncio

app = FastAPI()

# ✅ Activer CORS pour autoriser les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 URL de l'API Hugging Face
API_URL = "https://datasets-server.huggingface.co/rows"
DATASET_NAME = "Abirate/english_quotes"

# ✅ Cache global pour éviter de refaire des requêtes inutiles
cached_quotes = []
fetch_lock = asyncio.Lock()  # ✅ Verrou pour éviter le double chargement

async def fetch_quotes():
    global cached_quotes
    async with fetch_lock:  # ✅ Empêche les requêtes simultanées
        if cached_quotes:  # ✅ Vérifie si le cache est déjà rempli
            print(f"✅ Cache déjà chargé ({len(cached_quotes)} citations). Pas de nouvelle récupération.")
            return cached_quotes  

        print("📌 Chargement des citations depuis l'API (par lots de 100)...")
        total_quotes = []
        offset = 0
        batch_size = 100  # L'API limite length à 100
        max_quotes = 5000  # Nombre total de citations à récupérer

        while len(total_quotes) < max_quotes and offset < 5000:
            params = {
                "dataset": DATASET_NAME,
                "config": "default",
                "split": "train",
                "offset": offset,
                "length": batch_size
            }

            response = requests.get(API_URL, params=params)
            if response.status_code != 200:
                print(f"⚠️ Erreur API: {response.status_code}")
                break
            
            data = response.json()
            if "rows" in data and data["rows"]:
                new_quotes = [
                    {"quote": row["row"].get("quote", "No quote available"), 
                     "author": row["row"].get("author", "Unknown")}
                    for row in data["rows"]
                ]
                total_quotes.extend(new_quotes)
                offset += batch_size
                print(f"✅ {len(new_quotes)} citations récupérées, total : {len(total_quotes)}")
            else:
                print(f"⚠️ L'API a retourné 0 résultats à offset={offset}. Arrêt.")
                break

        cached_quotes = total_quotes  # ✅ Stocke les citations récupérées
        print(f"✅ {len(cached_quotes)} citations mises en cache !")
        return cached_quotes  

@app.get("/quotes")
async def get_quotes():
    return await fetch_quotes()

# ✅ Fonction de normalisation du texte
def normalize_text(text):
    return re.sub(r"\s+", " ", text.strip().lower())

@app.get("/quotes/search")
async def search_quotes(query: str = Query(..., min_length=2)):
    all_quotes = await fetch_quotes()
    print(f"✅ {len(all_quotes)} citations chargées pour la recherche.")
    query_norm = normalize_text(query)

    print(f"🔎 Recherche pour '{query_norm}' dans {len(all_quotes)} citations...")
    result = []
    seen_texts = set()

    for q in all_quotes:
        quote_norm = normalize_text(q["quote"])
        author_norm = normalize_text(q["author"])

        if query_norm in quote_norm or query_norm in author_norm:
            if q["quote"] not in seen_texts:
                seen_texts.add(q["quote"])
                result.append(q)
        
        author_reversed = " ".join(reversed(author_norm.split(", ")))
        if query_norm in author_reversed:
            if q["quote"] not in seen_texts:
                seen_texts.add(q["quote"])
                result.append(q)

    print(f"✅ {len(result)} résultats trouvés pour '{query_norm}'")
    return result
