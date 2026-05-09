from fastapi import FastAPI

app = FastAPI(title="Movie AI Agent")


@app.get("/")
def root():
    return {"message": "Movie AI Agent API"}
