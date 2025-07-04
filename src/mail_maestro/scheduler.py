from apscheduler.schedulers.background import BackgroundScheduler
from threading import Event
from datetime import datetime, timedelta
import logging

from mail_maestro.services.notion_client import NotionService

log = logging.getLogger("mailmaestro.core")

class Scheduler:
    def __init__(self):
        log.info("Initializing Scheduler.")
        self._sched = BackgroundScheduler()
        self._sched.start()
        # keep the process alive if you run in "serve" mode
        self._stop_event = Event()
        log.debug("Scheduler started and stop event created.")

    def schedule(self, concert: dict):
        """
        Schedule a one-off job at datetime dt to log or send the message.
        You can replace the job_func with any action you like.
         "concert": {
                    "event_name": str,         # Event Name
                    "summary": str,            # Concert Summary
                    "date_time": str,          # Date & Time
                    "venue_address": str,      # Venue & Address
                    "presale_info": str,       # Presale Information
                    "ticket_link": str,        # Ticket Purchase Link
                    "additional_notes": str    # Additional Notes
                }
        """
        def job_func():
            notion = NotionService.get_instance()
            notion.insert_concert(concert, '220c4a082ac980d5b6a9cc8e0f46a3b3')
        log.info(f"Scheduling job '{concert['event_name']}' at {concert['date_time']} with message: {concert['additional_notes']}")
        # try:
        #     run_time = datetime.now() + timedelta(minutes=1)
        #     self._sched.add_job(
        #         job_func,
        #         trigger="date",
        #         run_date=run_time,
        #         id=concert["event_name"],
        #         replace_existing=False
        #     )
        #     log.debug(f"Job '{concert['event_name']}' scheduled successfully.")
        # except Exception as e:
        #     log.error(f"Failed to schedule job '{concert['event_name']}': {e}")
        #     raise
        try:
            job_func()
            log.debug(f"Job '{concert['event_name']}' ran immediately.")
        except Exception as e:
            log.error(f"Job '{concert['event_name']}' failed: {e}")


    def shutdown(self):
        log.info("Shutting down Scheduler.")
        self._sched.shutdown()
        self._stop_event.set()
        log.debug("Scheduler shutdown complete and stop event set.")

    def wait_forever(self):
        log.info("Scheduler entering wait_forever mode (container will stay alive).")
        # call this if you want your container to stay alive
        self._stop_event.wait()
        log.info("Scheduler wait_forever event released.")
