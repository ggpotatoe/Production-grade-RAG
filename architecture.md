# 🎓 Óbuda University Phonebook RAG POC - Project Specification

## 1\. 🎯 Projekt Célja

Létrehozni egy "Production-Grade" RAG (Retrieval-Augmented Generation) POC alkalmazást, amely az Óbudai Egyetem telefonkönyv adatait (CSV) teszi kereshetővé természetes nyelven.

  - **Elsődleges nyelv:** Magyar.
  - **Másodlagos nyelv:** Angol (UI kapcsolóval és automatikus nyelvfelismeréssel).
  - **Design:** Óbudai Egyetem arculat (Sötétkék, Narancs, Fehér).

## 2\. 🛠️ Technológiai Stack

### Backend (Python)

  - **Framework:** `FastAPI` (gyors, aszinkron, könnyű dokumentálni).
  - **LLM:** `gpt-4o-mini` (OpenAI API-n keresztül). Ez a legköltséghatékonyabb és leggyorsabb modell erre a célra.
  - **Embedding:** `intfloat/multilingual-e5-large`. Mivel ez egy nagyobb modell, a `FastEmbed` vagy `SentenceTransformers` könyvtárat használjuk a lokális futtatáshoz (CPU-n is hatékony), így nem kell fizetni külső embedding API-ért.
  - **Vector Database:** `Qdrant` (Dockerben vagy in-memory/disk módban). Kiváló a "Hybrid Search" (kulcsszavas + szemantikus) támogatásban, ami kritikus telefonkönyv adatoknál.
  - **Data Handling:** `Pandas` a CSV tisztítására és betöltésére.

### Frontend (Vanilla)

  - **Tech:** HTML5, CSS3, Vanilla JavaScript (ES6+).
  - **Styling:** CSS változók az ÓE színekhez, Flexbox/Grid a layout-hoz. Nem használunk build rendszert (Vite/Webpack/React) a POC egyszerűsége és hordozhatósága érdekében, de a kód tiszta és moduláris marad.

## 3\. 🎨 Design & UI (Óbudai Egyetem Arculat)

  - **Primary Blue:** `#003E7E` (Mélykék) - Fejléchez, gombokhoz.
  - **Secondary Orange:** `#F28C00` (Narancs) - Kiemelésekhez, "Call to Action" elemekhez.
  - **Background:** `#FFFFFF` (Fehér) és `#F5F5F5` (Világosszürke).
  - **Text:** `#333333` (Sötétszürke).

## 4\. 📂 Projekt Struktúra

A projekt gyökérkönyvtára legyen az alábbi szerkezetű. Kérlek, generáld le a fájlokat ezen struktúra alapján.

```text
obuda-phonebook-rag/
│
├── data/
│   └── ad-users.csv           # A forrásfájl (a user által feltöltött CSV)
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI belépési pont
│   │   ├── config.py          # Környezeti változók kezelése
│   │   ├── models.py          # Pydantic modellek (Request/Response)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ingestion.py   # CSV beolvasása, tisztítása, embedding generálás
│   │       ├── vector_store.py# Qdrant kliens és keresési logika
│   │       └── llm_engine.py  # OpenAI hívás és prompt engineering
│   │
│   ├── requirements.txt       # Python függőségek
│   └── .env.example           # API kulcsok helye
│
├── frontend/
│   ├── index.html             # Főoldal szerkezete
│   ├── style.css              # ÓE design
│   ├── app.js                 # API hívások, chat logika, nyelvváltás
│   └── assets/                # Képek (pl. logo placeholder)
│
├── docker-compose.yml         # Qdrant adatbázis futtatásához
└── README.md                  # Dokumentáció
```

## 5\. 🧠 Implementációs Részletek (Prompt a Cursornak)

### 5.1 Adatfeldolgozás (Data Ingestion Strategy)

A táblázatos adatoknál (CSV) a sima szöveges chunkolás nem hatékony.
**Stratégia:**

1.  Minden sorból készítünk egy **szemantikus dokumentumot** az embeddinghez.
      - *Formátum:* `Név: {DisplayName}, Beosztás: {Title}, Tanszék: {Department}, Telefonszám: {TelephoneNumber}...`
2.  Az eredeti mezőket (Department, Title, OUPath) elmentjük **Payload/Metadata**-ként a Qdrantban.
3.  Ez lehetővé teszi, hogy az LLM válaszában pontosan vissza tudja adni a telefonszámot, ne hallucináljon.

### 5.2 Backend Logika (`backend/app/services`)

  - **Ingestion:** Használd a `FastEmbed` könyvtárat az `intfloat/multilingual-e5-large` modellhez. Prefixáld a query-ket: "query: " és a dokumentumokat "passage: " előtaggal (az e5 modell ezt igényli).
  - **Search:** A Qdrant-ban végezz "similarity search"-et. A találatokat (Top 5-10) add át az LLM-nek contextként.
  - **LLM Prompt:** A rendszer promptnak tartalmaznia kell:
      - Te az Óbudai Egyetem segítőkész telefonkönyv asszisztense vagy.
      - Szigorúan csak a megadott kontextusból válaszolj.
      - Ha a query angol, válaszolj angolul. Ha magyar, magyarul.

### 5.3 Frontend Logika

  - **Nyelvváltás:** Egy egyszerű gomb (HU/EN). Ez beállít egy változót, amit elküldünk a backendnek a query mellett (`language: "hu"` vagy `"en"`).
  - **Chat Interface:**
      - Input mező alul.
      - Chat buborékok (User: jobbra, Bot: balra).
      - Loading indikátor (pl. az ÓE logó pulzálása vagy narancssárga pontok).
      - A válaszban a telefonszámok és email címek legyenek kattintható linkek (`tel:`, `mailto:`).

## 6\. 📝 Generálandó Kód Részletek (Iránymutatás)

### `requirements.txt`

```text
fastapi
uvicorn
python-dotenv
pandas
qdrant-client
openai
fastembed
pydantic
```

### `backend/app/services/ingest.py` (Snippet)

```python
# Pszeudokód iránymutatás
import pandas as pd
from fastembed import TextEmbedding

def process_csv(file_path):
    df = pd.read_csv(file_path)
    # Adattisztítás: NaN értékek kezelése
    documents = []
    metadatas = []
    
    for _, row in df.iterrows():
        # Szemantikus szöveg létrehozása kereséshez
        content = f"Név: {row['DisplayName']}, Beosztás: {row['Title']}, Szervezet: {row['Department']}..."
        documents.append(content)
        metadatas.append(row.to_dict())
        
    embedding_model = TextEmbedding(model_name="intfloat/multilingual-e5-large")
    embeddings = list(embedding_model.embed(documents))
    
    return documents, embeddings, metadatas
```

### `frontend/style.css` (Snippet)

```css
:root {
    --oe-blue: #003E7E;
    --oe-orange: #F28C00;
    --bg-light: #F5F7FA;
    --chat-bg-user: #003E7E;
    --chat-text-user: #FFFFFF;
    --chat-bg-bot: #FFFFFF;
}
/* Használj modern CSS reset-et és Flexboxot a layout felépítéséhez */
```

-----

**Utasítás a Cursornak:**
Kérlek, kezdd a projektet a `requirements.txt` és a `docker-compose.yml` létrehozásával, majd építsd fel a backend logikát az adatbetöltéshez. Ha ezek megvannak, készítsd el a FastAPI végpontokat, végül a Frontend-et.

A user által biztosított CSV fájl adatai alapján a következő mezőkre figyelj kiemelten:
`DisplayName`, `Title`, `Department`, `TelephoneNumber`, `UPN` (Email).