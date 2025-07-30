from fastapi import FastAPI
import torch, numpy as np

app = FastAPI()
model = torch.load("model.pt", map_location="cpu")
model.eval()

@app.post("/infer")
def infer(payload: dict):
    x = torch.tensor([payload["input"]], dtype=torch.float32)
    with torch.no_grad():
        y = model(x).item()
    return {"score": y, "prediction": int(np.argmax(y))}

@app.get("/report")
def report():
    return {"message": "Production report: OK"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=51000)
