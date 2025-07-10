# main.py

import os
import subprocess
from dotenv import load_dotenv
import uvicorn
from .server import app
from . import index


def start_rq_worker():
    print("🔧 Starting RQ worker with scheduler...")

    # Load environment variables from .env
    load_dotenv()

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

    # 2. Run document indexing
    print("🔄 Running document indexing...")
    index.run_indexing()

    # 3. Launch FastAPI server
    print("🚀 Starting FastAPI server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
