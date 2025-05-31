import uvicorn


def main():
    uvicorn.run("ws.main:app", host="0.0.0.0", port=8000)
