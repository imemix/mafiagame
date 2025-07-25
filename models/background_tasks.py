import threading
import time
from flask import current_app
from models.utils import release_expired_jail
from models.drug import DrugDealer
from datetime import datetime, timedelta
from flask_login import current_user
import random
from models.character import Character
from extensions import db
from apscheduler.schedulers.background import BackgroundScheduler

def jail_release_background_task(app):
    with app.app_context():
        while True:
            release_expired_jail()
            time.sleep(20)  # Check every 20 seconds

def start_jail_release_thread(app):
    t = threading.Thread(target=jail_release_background_task, args=(app,), daemon=True)
    t.start()

def start_scheduler(app):
    from models.stock import update_all_stock_prices
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: app.app_context().push() or update_all_stock_prices(),
        trigger="interval",
        # Random interval between 1 minute and 1 hours
        seconds=30,
        id="update_stock_prices"
    )
    scheduler.start()

def get_online_users():
    cutoff = datetime.utcnow() - timedelta(seconds=1)
    # Real users online
    real_online = current_user.name.query.filter(current_user.last_seen >= cutoff).all()
    # NPCs: Characters with master_id=0 (or whatever you use)
    npcs = Character.query.filter_by(master_id=0, is_alive=True).all()
    # Optionally, create a fake User object for each NPC if your template expects User
    return real_online, npcs
