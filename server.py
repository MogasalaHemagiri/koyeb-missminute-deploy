from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Online", "agent": "Missminute1", "platform": "Koyeb"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

