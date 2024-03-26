from googlesearch import search
import requests
from bs4 import BeautifulSoup

def google_search(query:str) -> str:
    """
    Perform a Google search for the given query and return the search results.

    Args:
        query (str): The search query.

    Returns:
        str: The search results as a string, including URLs and text content of the given search query.

    """
    urls = []
    for i in search(query, num_results=1):
        urls.append(i)
    
    information = ''
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        text_content = ''
        paraghraphs = soup.find_all('p')
        for paragraph in paraghraphs:
            text_content += paragraph.text

        information += f"{url}\n{text_content}\n\n"

    if len(information) >= 2048:
        information = information[:2048]
    
    return information
