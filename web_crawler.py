import requests
from bs4 import BeautifulSoup


def get_all_links(url):
    """Function returns list of all links found in the url"""
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    # List comprehension for retrieving only href content (no tags)
    return [i.get('href') for i in soup.find_all('a')]


def get_site_title(url):
    """Funtion returns title of site at passed url"""
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    return soup.title.text
