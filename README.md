# Gene Expression Explorer

Analyzes gene expression data from NCBI's GEO repository and provides a web interface to explore results.

# Architecture:

![image](https://github.com/user-attachments/assets/027af4ab-5124-4d44-98b8-29fb5735f707)


for frontend refer https://github.com/VarshithPawarHR/Gene-Expression-Explorer-Dashboard

# Note: This is microservice for the above repository

# Note: The one service hosted is currently on free trial if you try to load a large dataset it will crash please load it in local system by cloning this repo!! Thank you


## Project Branches
*   **`main` branch**: Contains the **Flask backend server**.
    *   Handles data fetching from GEO, analysis (Pandas, SciPy), and API endpoints.
*   **`master` branch**: Contains the **Streamlit frontend UI**.
    *   Visualizes data and allows users to query genes via the Flask API.

## Tech Stack
*   **Backend (`main`)**: Python, Flask, Pandas, SciPy
*   **Frontend (`master`)**: Python, Streamlit

## Quick Start

### 1. Clone the Repository

```
git clone <your-repository-url>
cd <your-repository-name>
```


### 3. Setup & Run Frontend (Streamlit - `master` branch)
**(Open a new terminal)**



## Usage
1.  Ensure the Flask backend (`main`) is running.
2.  Ensure the Streamlit frontend (`master`) is running.
3.  Open the Streamlit URL (e.g., `http://localhost:8501`) in your browser to explore.

---
*Make sure you have a `requirements.txt` in both the `main` and `master` branches!*
*Generate with: `pip freeze > requirements.txt` in each activated virtual environment.*




