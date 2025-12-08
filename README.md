# 🎓 Óbudai Egyetem Telefonkönyv RAG POC

Production-Grade RAG (Retrieval-Augmented Generation) alkalmazás az Óbudai Egyetem telefonkönyv adatainak természetes nyelvű kereséséhez.

## 📋 Tartalomjegyzék

- [Funkciók](#funkciók)
- [Technológiai Stack](#technológiai-stack)
- [Telepítés](#telepítés)
- [Használat](#használat)
- [Projekt Struktúra](#projekt-struktúra)
- [API Dokumentáció](#api-dokumentáció)

## ✨ Funkciók

- 🔍 **Természetes nyelvű keresés** - Kérdezz bármit a telefonkönyvről természetes nyelven
- 🌍 **Többnyelvűség** - Magyar és angol nyelv támogatás
- 🎨 **ÓE Arculat** - Az Óbudai Egyetem hivatalos színei és designja
- ⚡ **Gyors válaszidő** - Optimalizált embedding és vektoros keresés
- 📱 **Reszponzív design** - Mobil és asztali eszközökön is tökéletesen működik

## 🛠️ Technológiai Stack

### Backend
- **FastAPI** - Modern, gyors Python web framework
- **OpenAI GPT-4o-mini** - LLM a válaszok generálásához
- **FastEmbed** - Lokális embedding generálás (intfloat/multilingual-e5-large)
- **Qdrant** - Vektoros adatbázis a hatékony kereséshez
- **Pandas** - Adatfeldolgozás

### Frontend
- **Vanilla JavaScript** - Nincs build rendszer, tiszta ES6+
- **HTML5 & CSS3** - Modern, reszponzív design
- **ÓE Brand Colors** - Hivatalos egyetemi arculat

## 🚀 Telepítés

### Előfeltételek

- Python 3.8+
- Docker és Docker Compose
- OpenAI API kulcs

### Lépések

1. **Klónozd a repository-t** (vagy navigálj a projekt mappába)

2. **Állítsd be a környezeti változókat**

   Hozz létre a `backend` mappában egy `.env` fájlt.
   Szerkeszd a `.env` fájlt és add meg az OpenAI API kulcsodat (illetve opcionálisan a provider endpointját):
   ```
   OPENAI_API_KEY=your_api_key_here
   # Optional
   # OPENIS_BASE_URL=your_deployment_endpoint
   ```
3. **Adatforrás létrehozása**

   A projekt gyökerében hozz létre egy `data` mappát, amibe az `ad users.xlsx` fájlt elhelyezed.

5. **Indítsd el a Qdrant adatbázist**

   ```bash
   docker-compose up -d
   ```

   Ez elindítja a Qdrant konténert a `localhost:6333` porton.

6. **Telepítsd a Python függőségeket**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

7. **Indítsd el a backend szervert**

   ```bash
   cd backend\app
   python main.py
   ```

   A backend elérhető lesz a `http://localhost:8000` címen.

8. **Nyisd meg a frontend-et**

   Ezután nyisd meg a böngészőben: `http://localhost:8080`

## 📖 Használat

### Frontend használat

1. Nyisd meg a frontend oldalt a böngészőben
2. Írj be egy kérdést a beviteli mezőbe, például:
   - "Ki a mérnöki intézet dékánja?"
   - "Melyik a Györök György telefonszáma?"
   - "Kik dolgoznak az Alba Regia Karon?"
3. A válasz automatikusan megjelenik a chatben
4. A telefonszámok és email címek kattintható linkek

### Nyelvváltás

Kattints a jobb felső sarokban lévő nyelvváltó gombra (HU/EN) a nyelv megváltoztatásához.

## 📂 Projekt Struktúra

```
obuda-phonebook-rag/
│
├── data/
│   └── ad users.xlsx          # Forrásadatok
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI belépési pont
│   │   ├── config.py          # Konfiguráció
│   │   ├── models.py          # Pydantic modellek
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ingestion.py   # Adatfeldolgozás
│   │       ├── vector_store.py # Qdrant műveletek
│   │       └── llm_engine.py  # OpenAI integráció
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app.js 
│   ├── index.html
│   ├── style.css
│   └── assets/
│       ├── OE_jubileumok_eve_feher.png
│       ├── UJ_Óbudai_Egyetem_LOGO_FEHER-1.png
│       └── THE_WUR_2025_NEW_Ranking_Template_Top_800_WO.png
│
├── docker-compose.yml
└── README.md
```

## 🔌 API Dokumentáció

A backend elindítása után az API dokumentáció elérhető:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Főbb végpontok

#### `GET /health`
Egészségügyi ellenőrzés - ellenőrzi a Qdrant kapcsolatot és a kollekció létezését.

#### `POST /query`
Természetes nyelvű lekérdezés feldolgozása.

**Request body:**
```json
{
  "query": "Ki a mérnöki intézet dékánja?",
  "language": "hu",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "A mérnöki intézet dékánja Györök György...",
  "sources": [...],
  "language": "hu"
}
```

#### `POST /reindex`
Újraindexelés - hasznos, ha frissítetted az adatokat.

## 🎨 Design

Az alkalmazás az Óbudai Egyetem hivatalos arculatát követi:
- **Primary Blue:** `#003E7E` - Fejlécek, gombok
- **Secondary Orange:** `#F28C00` - Kiemelések, CTA elemek
- **Background:** `#FFFFFF` és `#F5F5F5`

## 🔧 Fejlesztés

### Újraindexelés

Ha módosítottad az adatokat, újraindexelheted a vektoros adatbázist:

```bash
curl -X POST http://localhost:8000/reindex
```

### Környezeti változók

A `backend/.env` fájlban beállítható:
- `OPENAI_API_KEY` - OpenAI API kulcs (kötelező), vagy Provider api key
- `OPENAI_BASE_URL` - Provider endpoint, amennyiben nem közvetlenül OpenAI-on keresztül hívod a modellt

## 📝 Megjegyzések

- Az első indításkor a backend automatikusan betölti és indexeli az adatokat
- Az embedding modell első használatkor letöltődik (több száz MB lehet)
- A Qdrant adatok a Docker volume-ban tárolódnak (`qdrant_storage`)

## 📄 Licenc

Ez egy POC (Proof of Concept) projekt az Óbudai Egyetem számára.

## 🤝 Közreműködés

Ez egy belső POC projekt. Kérdések esetén vedd fel a kapcsolatot a projekt felelősével.

