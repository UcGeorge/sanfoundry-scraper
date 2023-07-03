from typing import Dict
from bs4 import BeautifulSoup
from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse

scrapfly = ScrapflyClient(key='scp-live-b9f9a03b4e1c452e899a8ba57edae8a8')


def get_html(url: str) -> str:
    api_response: ScrapeApiResponse = scrapfly.resilient_scrape(
        scrape_config=ScrapeConfig(url, headers={"referer": url}))
    return api_response.scrape_result['content']


def pagescrape(url: str, path: str) -> Dict[str, str]:
    content = get_html(url)
    soup = BeautifulSoup(content, 'lxml')

    try:
        content = soup.find('div', class_='entry-content')
        sf_contents = content.findAll('div', class_='sf-section')
        filtered_sf_content = [
            item for item in sf_contents
            if item.h2 is not None and item.table is not None
        ]
        tables = [item.table for item in filtered_sf_content]
        links = {}
        for table in tables:
            hrefs = {link.text.strip().replace(
                " ", '-'): link["href"] for link in table.findAll('a') if link.has_attr('href')}
            links.update(hrefs)
        return links
    except AttributeError:
        with open(f"{path}/content.html", 'w') as f:
            f.write(str(content))
        return {}
