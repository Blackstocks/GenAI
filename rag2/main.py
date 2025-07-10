# main.py

import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
import uvicorn
from .server import app
from . import index
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def start_rq_worker():
    print("🔧 Starting RQ worker with scheduler...")

    # Load environment variables from .env

    # Launch RQ worker in the background
    subprocess.Popen(
        ["rq", "worker", "--with-scheduler", "--url", "redis://valkey:6379"]
    )
    print("✅ RQ worker running in background.")


def main():
    # Load environment
    load_dotenv()

    # 1. Start background worker
    start_rq_worker()

    # 3. Launch FastAPI server
    print("🚀 Starting FastAPI server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
