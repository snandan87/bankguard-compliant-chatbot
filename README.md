# BankGuard: Banking Compliance Policy Assistant with Chroma Vector DB

### 🛠️ PyCharm IDE Setup
1. Open `bankguard` folder in PyCharm.
2. Create Python 3.11/3.12 Virtual Environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (or `.\venv\Scripts\Activate.ps1`)
4. Install: `pip install -r requirements.txt`
5. Run: `streamlit run ui/app.py --server.port 8501`

### 📄 Compliance Policy Ingestion
- Upload PDF policy manuals via the Streamlit interface.
- Documents are chunked and stored in Chroma Vector DB.
- Queries perform vector similarity search to ground responses.