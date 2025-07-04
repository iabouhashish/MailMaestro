# src/services/notion_service.py

import os
from notion_client import Client
from typing import Optional, TypedDict
from datetime import datetime as date_time
import threading
import logging

logger = logging.getLogger("mailmaestro.services")


class Concert(TypedDict):
    event_name: str
    date_time: date_time
    venue_address: str
    presale_info: str
    additional_notes: str
    summary: str
    ticket_link: str


class NotionService:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, api_key: str):
        if hasattr(self, "_initialized") and self._initialized:
            return  # Prevent reinitialization

        self._client = Client(auth=api_key)
        self._initialized = True
        logger.info("NotionService singleton instance created.")

    @classmethod
    def get_instance(cls, api_key: Optional[str] = None) -> "NotionService":
        """
        Get the singleton instance, initializing it if necessary.
        `api_key` is only used during first-time initialization.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if not api_key:
                        api_key = os.getenv("NOTION_API_KEY")
                        if not api_key:
                            raise ValueError("api_key required to initialize NotionService")
                    cls._instance = cls(api_key)
        return cls._instance

    def insert_concert(self, concert: Concert, database_id: str) -> None:
        """
        Inserts a concert into the specified Notion database.
        """
        properties = self._format_concert_properties(concert)

        try:
            self._client.pages.create(parent={"database_id": database_id}, properties=properties)
            logger.info(f"Inserted concert '{concert['event_name']}' into Notion (DB: {database_id}).")
        except Exception as e:
            logger.error(f"Failed to insert concert into Notion: {e}")
            raise

    def _format_concert_properties(self, concert: Concert) -> dict:
        """
        Formats the concert dictionary into Notion property format.
        Handles missing or malformed fields gracefully, logging warnings and using empty strings or None as appropriate.
        Accepts 'date_time' as either a datetime object or a string (ISO format preferred).
        """
        logger.debug(f"Formatting concert properties for: {concert.get('event_name', '[Unknown Event]')}")
        props = {}
        def safe_get(key, default=""):
            value = concert.get(key, default)
            if value == "" or value is None:
                logger.warning(f"Concert property '{key}' missing or empty; using default: '{default}'")
            return value

        # Concert title
        props["Concert"] = {"title": [{"text": {"content": safe_get("event_name")}}]}

        # Concert Date
        date_val = concert.get("date_time")
        date_str = None
        if date_val:
            try:
                if isinstance(date_val, str):
                    logger.debug(f"Attempting to parse 'date_time' as ISO format: '{date_val}'")
                    try:
                        dt = date_time.fromisoformat(date_val)
                        date_str = dt.date().isoformat()
                        logger.info(f"Parsed 'date_time' as ISO: '{date_val}' -> '{date_str}'")
                    except Exception as e:
                        logger.warning(f"Could not parse 'date_time' string '{date_val}' as ISO: {e}; trying fallback format.")
                        # Try fallback format like 'Sat 7/19'
                        import re
                        import datetime as dtmod
                        match = re.match(r"(?:[A-Za-z]{3,}\s*)?(\d{1,2})/(\d{1,2})", date_val)
                        if match:
                            month, day = int(match.group(1)), int(match.group(2))
                            year = dtmod.datetime.now().year
                            logger.debug(f"Attempting fallback parse for 'date_time': month={month}, day={day}, year={year}")
                            try:
                                dt2 = dtmod.datetime(year, month, day)
                                date_str = dt2.date().isoformat()
                                logger.info(f"Parsed 'date_time' fallback: '{date_val}' -> '{date_str}'")
                            except Exception as e2:
                                logger.error(f"Could not parse fallback 'date_time' string '{date_val}': {e2}; using empty date.")
                        else:
                            logger.error(f"Unrecognized 'date_time' string format: '{date_val}'; using empty date.")
                else:
                    logger.debug(f"'date_time' is a datetime object: {date_val}")
                    date_str = date_val.date().isoformat()
                    logger.info(f"Parsed 'date_time' from datetime object: '{date_str}'")
            except Exception as e:
                logger.error(f"Malformed 'date_time' in concert: {date_val} ({e}); using empty date.")
        else:
            logger.warning("Concert property 'date_time' missing; using empty date.")
        logger.info(f"Final 'Concert Date' value: {date_str}")
        props["Concert Date"] = {"date": {"start": date_str or None}}

        # Venue Name
        props["Venue Name"] = {"rich_text": [{"text": {"content": safe_get("venue_address")}}]}
        # Presale Information
        props["Presale Information"] = {"rich_text": [{"text": {"content": safe_get("presale_info")}}]}
        # Description
        props["Description"] = {"rich_text": [{"text": {"content": safe_get("summary")}}]}
        # Ticket Link
        ticket_link = concert.get("ticket_link", "")
        if not ticket_link:
            logger.warning("Concert property 'ticket_link' missing or empty; using empty string.")
        props["Ticket Link"] = {"url": ticket_link}
        # Additional Notes
        props["Additional Notes"] = {"rich_text": [{"text": {"content": safe_get("additional_notes")}}]}
        logger.debug(f"Formatted concert properties: {props}")
        return props
