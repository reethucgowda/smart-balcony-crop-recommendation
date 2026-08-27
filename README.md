# 🌱 Smart Balcony Crop Recommendation System

A Streamlit-based application that recommends suitable crops for balcony gardening based on environmental and balcony conditions.

## ✨ Features

* 🌱 Smart crop recommendations
* ☀️ Sunlight analysis
* 🌡️ Temperature & humidity analysis
* 💧 Water requirement analysis
* 🪴 Balcony space & pot size consideration
* 📊 Crop suitability scores
* 📋 Crop growing guidance

## 🧠 Algorithm

**Weighted Rule-Based Scoring Algorithm**

The system calculates a suitability score for each crop using:

* Sunlight — 25%
* Temperature — 20%
* Pot Size — 15%
* Space — 10%
* Water — 10%
* Season — 10%
* Wind — 5%
* Experience — 5%

The crops are ranked according to their final suitability score.

## 🛠️ Technologies

Python • Streamlit • Pandas • CSV

## ▶️ Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Live Demo

https://smart-balcony-crop-recommendation.streamlit.app

## 🎯 Goal

To help balcony gardeners choose suitable crops using data-driven recommendations.

## 👩‍💻 Author

**Reethu C Gowda**
