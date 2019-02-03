import requests
from bs4 import BeautifulSoup
from url_normalize import url_normalize


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


def validate_links(links, url):
    """
    Function returns validated set of links
    Validation can be extended
    """
    valid_links = []
    # Iterate through list and validate each link
    for link in links:
        # Put here any needed validation
        if link is not None and 'mailto:' not in link:
            if link == url:
                valid_links.append(link)
            elif url == link[:len(url)]:
                # Normalize link if it leads to subsite
                valid_link = url_normalize(link)
                valid_links.append(link)
            else:
                try:
                    # Section mainly for relative links
                    # Try block prevents from getting errors from request.get()
                    if link[0] != '/':
                        link = f'/{link}'
                    if (
                        'http' not in link[:5]
                        and requests.get(url + link).status_code == 200
                    ):
                        if url[-1] == '/' and link[0] == '/':
                            valid_link = f'{url[:-1]}{link}'
                            valid_links.append(url_normalize(valid_link))
                        else:
                            valid_link = f'{url}{link}'
                            valid_links.append(url_normalize(valid_link))
                except requests.exceptions.ConnectionError as errorc:
                    print(f"Connection error: {errorc}")
    # Return set of links to avoid duplicates
    return(set(valid_links))


def iterate_dictionary(dictio, base_url):
    """Recursive function that add data to the dictionary"""
    if {} in dictio.values():
        for key in dictio:
            if dictio[key] == {}:
                title = get_site_title(key)
                links = get_all_links(key)
                valid_links = validate_links(links, base_url)
                dictio[key] = {
                    'title': title,
                    'links': valid_links
                }
                # Add new objects to the dictionary
                for link in valid_links:
                    if link not in dictio:
                        dictio[link] = {}
                # Break loop after adding keys to avoid errors
                break
        iterate_dictionary(dictio, base_url)
    return dictio


def save_to_file(source):
    """optional function for saving result in a file"""
    with open('output.txt', 'w') as fn:
        fn.write(str(source))


def site_map(url):
    """Fuction returns site map for given url"""
    # Create base dictionary with initial object
    dictio = {url: {}}
    output = iterate_dictionary(dictio, url)
    save_to_file(output)
    return output


def main():
    url = input('Write full url to map. Example "http://0.0.0.0:8000"')
    return site_map(url)


if __name__ == '__main__':
    main()