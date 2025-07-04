import re
import unicodedata
from bs4 import BeautifulSoup
from dateparser import parse
from datetime import datetime

def parse_datetime(text: str) -> datetime:
    return parse(text)


class EmailParser:
    def __init__(self):
        # You can hook in BeautifulSoup or other libs here
        pass

    def parse(self, raw_body: str) -> str:
        # Use BeautifulSoup to convert HTML to plain text
        soup = BeautifulSoup(raw_body, 'html.parser')
        text = soup.get_text(separator=' ')

        # Normalize unicode (NFKC = Compatibility Decomposition, then Composition)
        text = unicodedata.normalize('NFKC', text)

        # Remove control/non-printable characters (except basic whitespace)
        text = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF]+', '', text)

        # Optionally replace specific unicode whitespace (like non-breaking space)
        text = text.replace('\u00A0', ' ')  # Non-breaking space -> regular space

        # Collapse any extra whitespace
        text = ' '.join(text.split())
        return text