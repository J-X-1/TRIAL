"""
TRIAL - Texas Regulatory Insurance Analysis Layer
Phase 1: Selenium Scraper for Texas Insurance Code Title 7 (v2)

Uses Selenium with headless Chrome. Waits for the Angular app's
doc-viewer component to load actual statute content before saving.

URL pattern: https://statutes.capitol.texas.gov/Docs/IN/htm/IN.{chapter}.htm

Title 7 chapters: 1101-1117, 1131-1133, 1138, 1151-1154

Prerequisites:
  pip install selenium webdriver-manager
"""

import os
import time
import json
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
BASE_URL = "https://statutes.capitol.texas.gov/Docs/IN/htm/IN.{chapter}.htm"

# Only attempt chapters that actually exist in Title 7
# (based on our first Selenium run: these are the ones that had content markers)
# We'll try the full range but expect gaps
CHAPTER_START = 1101
CHAPTER_END = 1154

OUTPUT_DIR = "raw_html"
DELAY_SECONDS = 3  # slightly longer delay to be polite with Selenium
PAGE_LOAD_TIMEOUT = 30  # give Angular more time to load content


def setup_driver():
    """Create a headless Chrome browser instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def wait_for_statute_content(driver, timeout=PAGE_LOAD_TIMEOUT):
    """
    Wait for the doc-viewer to populate with statute text.
    
    The Angular app loads in stages:
    1. SPA shell loads (navigation, dropdowns, tree view)
    2. doc-viewer component makes an internal call to load statute HTML
    3. Content appears inside <app-doc-viewer>
    
    We wait for stage 3 by looking for statute-specific elements
    inside the doc-viewer, or by checking for substantial text content.
    """
    try:
        # Strategy 1: Wait for a section element with statute content
        # Real statute pages have elements like "Sec. 1101.001"
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "app-doc-viewer *")) > 5
            or "SUBCHAPTER" in d.find_element(By.CSS_SELECTOR, "app-doc-viewer").text
        )
        
        # Give a tiny bit more time for full content to render
        time.sleep(1)
        return True
    except Exception:
        pass
    
    try:
        # Strategy 2: Check if doc-viewer has any meaningful text at all
        doc_viewer = driver.find_element(By.CSS_SELECTOR, "app-doc-viewer")
        text = doc_viewer.text.strip()
        if len(text) > 100:
            return True
    except Exception:
        pass
    
    return False


def extract_statute_content(driver):
    """
    Extract just the statute content from the doc-viewer,
    plus save the full page source as backup.
    Returns (full_page_source, doc_viewer_text, doc_viewer_html)
    """
    full_source = driver.page_source
    
    try:
        doc_viewer = driver.find_element(By.CSS_SELECTOR, "app-doc-viewer")
        viewer_text = doc_viewer.text.strip()
        viewer_html = doc_viewer.get_attribute("innerHTML")
    except Exception:
        viewer_text = ""
        viewer_html = ""
    
    return full_source, viewer_text, viewer_html


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log = {
        "scrape_start": datetime.now().isoformat(),
        "source": "selenium v2 - waits for doc-viewer",
        "chapters_attempted": 0,
        "chapters_downloaded": 0,
        "chapters_not_found": 0,
        "chapters_failed": 0,
        "files": []
    }

    print("TRIAL Selenium Scraper v2")
    print(f"Downloading chapters {CHAPTER_START}-{CHAPTER_END}")
    print(f"Output directory: {OUTPUT_DIR}/")
    print(f"Timeout per page: {PAGE_LOAD_TIMEOUT}s")
    print("-" * 50)
    print("Starting headless Chrome...", flush=True)

    driver = setup_driver()
    print("Browser ready.\n")

    try:
        for chapter_num in range(CHAPTER_START, CHAPTER_END + 1):
            url = BASE_URL.format(chapter=chapter_num)
            log["chapters_attempted"] += 1

            print(f"  Ch. {chapter_num}: loading... ", end="", flush=True)

            try:
                driver.get(url)
                content_loaded = wait_for_statute_content(driver)

                full_source, viewer_text, viewer_html = extract_statute_content(driver)

                # Validate we got real statute content
                has_sections = "Sec." in viewer_text and "Added by Acts" in viewer_text
                has_chapter_header = "CHAPTER" in viewer_text or "SUBCHAPTER" in viewer_text
                text_length = len(viewer_text)

                if content_loaded and (has_sections or has_chapter_header) and text_length > 200:
                    # Save the full page
                    full_path = os.path.join(OUTPUT_DIR, f"IN_{chapter_num}.htm")
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(full_source)

                    # Also save just the doc-viewer content for easier parsing
                    content_path = os.path.join(OUTPUT_DIR, f"IN_{chapter_num}_content.htm")
                    with open(content_path, "w", encoding="utf-8") as f:
                        f.write(viewer_html)

                    # Save plain text version too
                    text_path = os.path.join(OUTPUT_DIR, f"IN_{chapter_num}.txt")
                    with open(text_path, "w", encoding="utf-8") as f:
                        f.write(viewer_text)

                    full_size = len(full_source.encode("utf-8"))
                    content_size = len(viewer_html.encode("utf-8"))
                    text_size = len(viewer_text.encode("utf-8"))

                    print(f"OK (text: {text_size:,} bytes, html: {content_size:,} bytes)")
                    log["chapters_downloaded"] += 1
                    log["files"].append({
                        "chapter": chapter_num,
                        "status": "downloaded",
                        "files": {
                            "full_page": f"IN_{chapter_num}.htm",
                            "content_html": f"IN_{chapter_num}_content.htm",
                            "plain_text": f"IN_{chapter_num}.txt"
                        },
                        "sizes": {
                            "full_page": full_size,
                            "content_html": content_size,
                            "plain_text": text_size
                        },
                        "url": url
                    })
                else:
                    reason = f"text_len={text_length}, sections={has_sections}, header={has_chapter_header}"
                    print(f"no statute content ({reason})")
                    log["chapters_not_found"] += 1
                    log["files"].append({
                        "chapter": chapter_num,
                        "status": "no_content",
                        "reason": reason,
                        "viewer_text_preview": viewer_text[:200] if viewer_text else "(empty)",
                        "url": url
                    })

            except Exception as e:
                print(f"ERROR: {e}")
                log["chapters_failed"] += 1
                log["files"].append({
                    "chapter": chapter_num,
                    "status": "error",
                    "error": str(e),
                    "url": url
                })

            time.sleep(DELAY_SECONDS)

    finally:
        driver.quit()
        print("\nBrowser closed.")

    # Save log
    log["scrape_end"] = datetime.now().isoformat()
    log_path = os.path.join(OUTPUT_DIR, "download_log.json")
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    # Summary
    print("-" * 50)
    print("Done!")
    print(f"  Attempted:    {log['chapters_attempted']}")
    print(f"  Downloaded:   {log['chapters_downloaded']}")
    print(f"  Not found:    {log['chapters_not_found']}")
    print(f"  Failed:       {log['chapters_failed']}")
    print(f"  Log saved:    {log_path}")


if __name__ == "__main__":
    main()
