# Autonomous QA Agent: The "Testing Brain" 🧠

## 📋 Objective
This project implements an **Autonomous QA Agent** capable of constructing a "testing brain" from project documentation. The system ingests support documents (product specs, UI guides, APIs) and the HTML structure of a target web project to autonomously:

1.  **Generate Test Cases**: Produce comprehensive, documentation-grounded test plans.
2.  **Generate Selenium Scripts**: Convert those test cases into executable Python Selenium scripts.

The system is built with a **FastAPI** backend and a **Streamlit** frontend, ensuring a modular and user-friendly experience.

---

## 🚀 Features

### 1. Knowledge Base Ingestion
*   **Multi-format Support**: Parses Markdown (`.md`), Text (`.txt`), JSON (`.json`), HTML (`.html`), and PDF (`.pdf`).
*   **Vector Storage**: Uses **ChromaDB** to store semantic embeddings of the documents for efficient retrieval (RAG).
*   **Strict Grounding**: All generated content is strictly based on the uploaded documents, eliminating hallucinations.

### 2. Test Case Generation Agent
*   **Intelligent Planning**: Uses LLMs (Groq/Llama 3) to analyze requirements and generate positive, negative, and edge-case scenarios.
*   **Traceability**: Every test case includes a `Grounded_In` field, referencing the specific source document used.

### 3. Selenium Script Generation Agent
*   **HTML-Aware**: Analyzes the provided `checkout.html` to identify correct ID, Name, and CSS selectors.
*   **Runnable Code**: Produces clean, executable Python code using `selenium` and `webdriver_manager`.
*   **Self-Correction**: Includes assertions and error handling based on UI guidelines (e.g., verifying error message colors).

---

## 🛠️ Technology Stack

*   **Backend**: FastAPI (Python)
*   **Frontend**: Streamlit
*   **LLM Inference**: Groq API (Llama 3.3 70B)
*   **Vector Database**: ChromaDB
*   **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
*   **Automation**: Selenium WebDriver

---

## 📂 Project Structure

```
autonomous-qa-agent/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── models.py            # Pydantic data models
│   └── services/            # Core logic
│       ├── document_parser.py   # File parsing (MD, PDF, HTML)
│       ├── vector_store.py      # ChromaDB management
│       ├── rag_service.py       # RAG pipeline implementation
│       ├── test_case_agent.py   # Test case generation logic
│       └── script_agent.py      # Selenium script generation logic
├── frontend/
│   └── app.py               # Streamlit user interface
├── data/                    # Data storage (uploads, vector_db, outputs)
├── test_cases/              # Project assets (docs, html)
├── requirements             # Project dependencies
└── run.bat                  # One-click startup script
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
*   Python 3.8 or higher
*   A Groq API Key (Get one for free at [console.groq.com](https://console.groq.com/))

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd autonomous-qa-agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory and add your API key:
    ```env
    GROQ_API_KEY=gsk_your_api_key_here...
    ```

---

## ▶️ How to Run

### Option A: One-Click Script (Windows)
Simply double-click `run.bat` or run it from the terminal:
```bash
.\run.bat
```
This script will:
1.  Check for the virtual environment.
2.  Start the FastAPI backend on port `8000`.
3.  Start the Streamlit frontend on port `8501`.
4.  Open your browser automatically.

### Option B: Manual Startup
If you prefer running components separately:

**Terminal 1 (Backend):**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
streamlit run frontend/app.py
```

---

## 📖 Usage Guide

### Phase 1: Build the Knowledge Base
1.  Go to the **"Knowledge Base"** tab in the UI.
2.  **Upload Documents**: Select the support files from the `test_cases/` folder (e.g., `product_specs.md`, `ui_ux_guide.txt`).
3.  **Upload HTML**: Upload the `checkout.html` file.
4.  Click **"Build Knowledge Base"**. The system will parse files and index them in ChromaDB.

### Phase 2: Generate Test Cases
1.  Switch to the **"Test Case Agent"** tab.
2.  Enter a prompt, e.g., *"Generate test cases for the discount code feature."*
3.  Click **"Generate Test Cases"**.
4.  Review the generated plans, including scenarios, expected results, and source document references.

### Phase 3: Generate Selenium Scripts
1.  Switch to the **"Script Agent"** tab.
2.  Select a generated test case from the dropdown (e.g., `TC-001`).
3.  Click **"Generate Selenium Script"**.
4.  The agent will analyze the test case and `checkout.html` to write the code.
5.  **Download** or **Copy** the script to run it locally.

---

## 📦 Project Assets (Included)

The `test_cases/` directory contains the required assets for the demo:

1.  **`checkout.html`**: The target single-page application. Contains forms for user details, shipping, payment, and a discount code field.
2.  **`product_specs.md`**: Defines business rules (e.g., "SAVE15 gives 15% off", "Express shipping is $10").
3.  **`ui_ux_guide.txt`**: Defines visual requirements (e.g., "Error messages must be red").
4.  **`api_endpoints.json`**: Mock API definitions for backend integration context.

---

## 🧪 Evaluation Criteria Checklist

*   [x] **Functionality**: Full pipeline implemented (Ingestion -> RAG -> Code).
*   [x] **Knowledge Grounding**: RAG pipeline ensures tests are based *only* on uploaded docs.
*   [x] **Script Quality**: Scripts use explicit waits (`WebDriverWait`) and correct selectors.
*   [x] **Code Quality**: Modular architecture with Pydantic models and typed services.
*   [x] **UX**: Clean Streamlit interface with progress indicators.
*   [x] **Documentation**: This README covers all setup and usage steps.