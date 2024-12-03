import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager  # Firefox WebDriver manager
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Set up Firefox options
firefox_options = Options()
# If you want Firefox to run in headless mode (without opening the browser window), uncomment the following line:
# firefox_options.add_argument("--headless")

# Set up Selenium with WebDriver Manager to handle geckodriver automatically
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=firefox_options)

# Open the webpage
url = "https://kids.nationalgeographic.com/geography/countries"
driver.get(url)

# Initial number of articles (to detect if new content is loaded)
initial_article_count = len(driver.find_elements(By.CSS_SELECTOR, 'a.PromoTile__Link'))

# Scroll to the bottom of the page and trigger content loading
while True:
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait for new content to load (adjust as necessary)

    # Check if the number of articles has increased
    current_article_count = len(driver.find_elements(By.CSS_SELECTOR, 'a.PromoTile__Link'))
    if current_article_count == initial_article_count:
        break  # Exit if no new articles are found
    else:
        initial_article_count = current_article_count  # Update the count and continue scrolling

# Optional: Pause for a few seconds to manually inspect the page
print("Waiting for 10 seconds before closing the browser for inspection...")
time.sleep(10)  # Increase this time if you need more time to inspect the page

# Get the fully loaded page source
page_source = driver.page_source

# (Optional) Print part of the page source for debugging before quitting
# You can inspect the page source here by printing a snippet
print(page_source[:500])  # Print the first 500 characters of the page source

driver.quit()

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Create RSS feed
fg = FeedGenerator()
fg.title('National Geographic Countries')
fg.link(href=url, rel='self')
fg.description('Explore different countries with National Geographic Kids.')

# Find the country links in the HTML
countries = soup.find_all('a', class_='PromoTile__Link')

# Loop through each country and add it to the RSS feed
for country in countries:
    title = country.get('aria-label')  # Extract the country name from the aria-label attribute
    link = country.get('href')  # Extract the link to the country article
    # Make sure the link is fully qualified (i.e., it has the full URL)
    if not link.startswith('http'):
        link = f"https://kids.nationalgeographic.com{link}"

    # Add the entry to the RSS feed
    entry = fg.add_entry()
    entry.title(title)
    entry.link(href=link)

# Save the RSS feed to a file
fg.rss_file('natgeo_countries.xml')
print("RSS feed saved as natgeo_countries.xml")