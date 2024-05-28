import uvicorn
from messages import create_app

app = create_app("development")

if __name__ == "__main__":
    uvicorn.run("run:app", host="127.0.0.1", port=8000, reload=True)