from fastapi import FastAPI

app = FastAPI()

@app.get("/{prekol}")
def index(prekol: str):
    return {"Zdarova": prekol}