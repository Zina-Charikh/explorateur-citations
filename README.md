# explorateur-citations
Projet interface web pour le TAL 

# Citations et Quiz 
Cette application interactive permet d’afficher des citations  et propose un quiz ludique où il faut deviner l’auteur d’une citation.

## Installation et Lancement
### Cloner le projet
```bash
git clone https://github.com/ton-repo/citations-quiz.git
cd citations-quiz
```

### Installer les dépendances  
```bash
pip install fastapi uvicorn requests
```

### Lancer l’API FastAPI 
```bash
uvicorn main:app --reload
```
L’API tourne maintenant sur **http://127.0.0.1:8000/**

### Ouvrir l’interface Web
Ouvrir **`interface.html`** dans un navigateur web.
