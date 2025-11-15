from apscheduler.schedulers.blocking import BlockingScheduler
from worker import run_sync_once
import time

def job():
    print(f"[RUN] Checking at {time.ctime()}")
    run_sync_once()

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, "interval", minutes=5)
    print("🚀 Auto Meeting Scheduler started.")
    job()
    scheduler.start()
