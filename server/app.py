# Minimal FastAPI example
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import uuid, datetime


app = FastAPI()


class GeminiResult(BaseModel):
    classification: str
    sentiment: str
    confidence_score: float
    entities: dict


@app.post('/enrich')
def enrich(data: GeminiResult):
    dept_map = {'invoice': 'Finance', 'contract': 'Legal', 'report': 'Management'}
    return {
        'document_id': str(uuid.uuid4()),
        'department': dept_map.get(data.classification, 'General'),
        'sensitivity': 'confidential' if 'amount' in str(data.entities) else 'internal',
        'routing_tag': 'needs-review' if data.confidence_score < 0.7 else 'auto-approved',
        'processed_at': datetime.datetime.utcnow().isoformat()
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)