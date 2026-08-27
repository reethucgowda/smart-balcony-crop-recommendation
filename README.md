# Smart Balcony Crop Recommendation System

A local Streamlit app that ranks container-friendly crops using balcony conditions and transparent weighted scoring.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Recommendation model

The first version intentionally uses a rule-based score because a small crop-property table is not enough to train a trustworthy supervised model. Scores combine sunlight (25%), temperature (20%), pot size (15%), space (10%), water (10%), season (10%), wind (5%), and experience (5%).

Feedback is appended to `data/sample_feedback.csv` and can later become the labeled dataset for comparing models such as Random Forest, KNN, Logistic Regression, and Gradient Boosting.
