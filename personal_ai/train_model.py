import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv("intents.csv")
X = df["text"]
y = df["intent"]

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2))),
    ("clf", LogisticRegression(max_iter=1000))
])

model.fit(X, y)
joblib.dump(model, "intent_model.pkl")

print("✅ Model trained and saved as intent_model.pkl")
