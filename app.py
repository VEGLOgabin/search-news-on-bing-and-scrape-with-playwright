import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv

async def scrape_bing_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True if you do not need to see the browser
        page = await browser.new_page()

        # Go to the Bing News search page
        await page.goto('https://www.bing.com/news/search?q=%22google%22+%22cloud%22')

        # Scroll to the bottom of the page to load more content
        previous_height = await page.evaluate('document.body.scrollHeight')
        print("Here is the previous height of the   search page : ")
        print(previous_height)
        while True:
            # Scroll down
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            # Wait for new content to load
            await page.wait_for_timeout(2000)  # Here is a timeout  for the new content to load

            # Get the new height and check if the page has stopped loading
            new_height = await page.evaluate('document.body.scrollHeight')
            if new_height == previous_height:
                break
            previous_height = new_height

        # Extract content
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.find_all('div', class_='news-card-body')

        # Prepare data for CSV
        data = []
        for article in articles:
            title_tag = article.find('a', class_='title')
            link_tag = article.find('a', class_='title')
            image_tag = article.find('img')
            source_tag = article.find('div', class_='source')
            snippet_tag = article.find('div', class_='snippet')

            title = title_tag.text.strip() if title_tag else 'No Title'
            link = link_tag['href'] if link_tag else 'No Link'
            image_url = image_tag['src'] if image_tag else 'No Image'
            source = source_tag.text.strip() if source_tag else 'No Source'
            snippet = snippet_tag.text.strip() if snippet_tag else 'No Snippet'

            data.append({
                'Title': title,
                'Link': link,
                'Image URL': image_url,
                'Source': source,
                'Snippet': snippet
            })

        # Save data to CSV
        with open('bing_news_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Link', 'Image URL', 'Source', 'Snippet']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        print(f'Scraped {len(data)} articles. Data saved to bing_news_articles.csv.')

        # Close the browser
        await browser.close()

# Run the scrape function
asyncio.run(scrape_bing_news())
