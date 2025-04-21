import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

# Page configuration
st.set_page_config(page_title="Web Scraper and Report Generator")
st.title("🌐 Web Scraper and Report Generator")
st.markdown("Extract basic web content (headings, paragraphs, links) from any website and generate a downloadable report.")

# User inputs with placeholder example
url = st.text_input("Enter Website URL", "", placeholder="e.g., https://example.com")
max_pages = st.number_input("Max Pages to Scrape (for paginated sites)", min_value=1, max_value=100, value=1)

# Scraper function
def scrape_general_site(base_url, max_pages):
    all_data = []
    current_page = base_url
    page_count = 0

    while current_page and page_count < max_pages:
        try:
            res = requests.get(current_page, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')

            elements = soup.find_all(['h1', 'h2', 'p', 'a'])

            for el in elements:
                tag = el.name
                text = el.get_text(strip=True)
                href = el.get("href") if tag == "a" else ""

                if text:
                    all_data.append({
                        "URL": current_page,
                        "Tag": tag,
                        "Content": text,
                        "Link": urljoin(current_page, href) if href else ""
                    })

            next_btn = soup.find("a", string=lambda s: s and "next" in s.lower())
            if next_btn:
                next_link = next_btn.get("href")
                current_page = urljoin(base_url, next_link)
                page_count += 1
                time.sleep(1)
            else:
                break

        except Exception as e:
            st.warning(f"Error scraping page {current_page}: {e}")
            break

    return pd.DataFrame(all_data)

# Start scraping
if st.button("Start Scraping"):
    if url:
        st.info("Scraping in progress...")
        start_time = time.time()
        df = scrape_general_site(url, max_pages)
        duration = round(time.time() - start_time, 2)

        if not df.empty:
            st.success(f"Scraping completed in {duration} seconds. Found {len(df)} items.")
            st.dataframe(df)
            st.download_button("📥 Download CSV Report", df.to_csv(index=False), file_name="web_scrape_report.csv", mime="text/csv")
        else:
            st.warning("No relevant content found.")
    else:
        st.error("Please enter a valid URL.")
