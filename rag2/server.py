# flake8: noqa

from fastapi import FastAPI, Query, Path
from .queue.connection import queue  # ✅ import the queue, not the connection
from .queue.worker import process_query

app = FastAPI()


@app.get("/")
def root():
    return {"status": "Server is up and running"}


@app.post("/chat")
def chat(query: str = Query(..., description="chat messages")):
    job = queue.enqueue(process_query, query)
    return {"status": "queued", "job_id": job.id}


@app.get("/result/{job_id}")
def get_result(job_id: str = Path(..., description="Job_ID")):
    job = queue.fetch_job(job_id=job_id)

    if job is None:
        return {"status": "not found"}
    if job.is_finished:
        return {"status": "finished", "result": job.result}
    elif job.is_failed:
        return {"status": "failed"}
    else:
        return {"status": "in progress"}
