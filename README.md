# Multiple Disease Prediction

Streamlit app that predicts diabetes, heart disease, and Parkinson's risk from patient input using pre-trained scikit-learn models, with an optional keyword-based AI health assistant.

## Structure

* `saved model/` — trained model files (`.sav`), loaded by the app
* `multiple_disease_pred1.py` — the Streamlit app (sidebar navigation, input forms, predictions)
* `chatbot_snippet.py` — keyword-based "AI Health Assistant" chatbot, pluggable into the sidebar
* `requirements.txt` — Python dependencies

## Setup

```
pip install -r requirements.txt
```

## Run

```
streamlit run "multiple_disease_pred1.py"
```