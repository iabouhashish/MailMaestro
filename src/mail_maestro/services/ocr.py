import base64
from PIL import Image
import pytesseract
import io
import requests
import logging

# PEP 282 logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("mailmaestro.services")

def extract_images(email_data):
    """
    Extract all inline/attached/linked image bytes from the Gmail API email object.
    Handles inline base64, attachments, and remote URLs.
    """
    images = []
    logger.debug(f"Starting extract_images with email_data keys: {list(email_data.keys())}")

    # Inline/attached images (base64-encoded)
    if 'payload' in email_data:
        stack = [email_data['payload']]
        while stack:
            part = stack.pop()
            logger.debug(f"Processing part with mimeType: {part.get('mimeType')}")
            if part.get('mimeType', '').startswith('image/'):
                data = part.get('body', {}).get('data')
                if data:
                    try:
                        img_bytes = base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))
                        images.append(img_bytes)
                        logger.info("Decoded and appended inline/attached image.")
                    except Exception as e:
                        logger.error(f"Error decoding image: {e}")
            # Recursively traverse subparts
            stack.extend(part.get('parts', []))

    # Find remote images in HTML body (simple version)
    body_html = ""
    if "payload" in email_data:
        for part in email_data["payload"].get("parts", []):
            if part.get("mimeType") == "text/html":
                html_b64 = part.get("body", {}).get("data")
                if html_b64:
                    try:
                        body_html = base64.urlsafe_b64decode(html_b64).decode("utf-8", errors="ignore")
                        logger.debug("Decoded HTML body for remote image search.")
                    except Exception as e:
                        logger.error(f"Error decoding HTML body: {e}")
                        continue

    import re
    urls = re.findall(r'<img[^>]+src="([^"]+)"', body_html)
    logger.debug(f"Found {len(urls)} image URLs in HTML body.")
    for url in urls:
        if url.startswith("http"):
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    images.append(resp.content)
                    logger.info(f"Downloaded remote image from {url}")
                else:
                    logger.warning(f"Failed to download image from {url}, status code: {resp.status_code}")
            except Exception as e:
                logger.error(f"Error downloading remote image from {url}: {e}")
    logger.info(f"Total images extracted: {len(images)}")
    return images

def ocr_images(image_bytes_list):
    """
    Runs OCR on a list of image byte blobs, returns joined text.
    """
    ocr_texts = []
    logger.info(f"Starting OCR on {len(image_bytes_list)} images.")
    for idx, img_bytes in enumerate(image_bytes_list):
        try:
            with Image.open(io.BytesIO(img_bytes)) as img:
                logger.debug(f"Opened image {idx} for OCR. Mode: {img.mode}, Size: {img.size}")
                # Preprocess for better OCR (optional)
                if img.mode == "P" and "transparency" in img.info:
                    img = img.convert("RGBA")
                    logger.debug(f"Converted image {idx} to RGBA for transparency.")
                img = img.convert("L")
                logger.debug(f"Converted image {idx} to grayscale.")
                text = pytesseract.image_to_string(img)
                if text.strip():
                    ocr_texts.append(text.strip())
                    logger.info(f"OCR succeeded for image {idx}.")
                else:
                    logger.warning(f"OCR returned empty text for image {idx}.")
        except Exception as e:
            logger.error(f"OCR failed for image {idx}: {e}")
    logger.info(f"OCR complete. Total non-empty results: {len(ocr_texts)}")
    return "\n\n".join(ocr_texts)
