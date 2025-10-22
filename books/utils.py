import requests
import json
from django.conf import settings
from rest_framework.pagination import PageNumberPagination


def search_books_by_categroy(max_results=40, category=None):

    base_url = "https://www.googleapis.com/books/v1/volumes"
    
    # Build search query with category filter
    # search_query = query
    search_query = f"subject:{category}".strip()
    
    params = {
        "q": search_query,
        "maxResults": min(max_results, 40),
        "key": settings.GOOGLE_BOOKS_API_KEY
    }
    

    
    try:
        response = requests.get(base_url, params=params)
        print("REQUEST: ", response)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("ERROR: ",category)
        return {"error": str(e)}
    
    
def search_books(query, max_results=15):
    """
    Search for books using the Google Books API.
    
    Args:
        query (str): Search query (e.g., "python programming", "isbn:9780132350884")
        max_results (int): Maximum number of results to return (default: 10, max: 40)
        api_key (str): Optional API key for higher rate limits
    
    Returns:
        dict: JSON response from the API
    """
    base_url = "https://www.googleapis.com/books/v1/volumes"
    
    params = {
        "q": query,
        "maxResults": min(max_results, 40),
        "key": settings.GOOGLE_BOOKS_API_KEY
    }
    
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def get_book_by_id(volume_id):
    """
    Get detailed information about a specific book by its volume ID.
    
    Args:
        volume_id (str): The Google Books volume ID
        api_key (str): Optional API key
    
    Returns:
        dict: JSON response with book details
    """
    url = f"https://www.googleapis.com/books/v1/volumes/{volume_id}"
    
    params = {
        "key": settings.GOOGLE_BOOKS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching book: {e}")
        return None

def display_books(books_data):
    """Display book information in a readable format."""
    if not books_data or "items" not in books_data:
        print("No books found.")
        return
    
    print(f"\nFound {books_data.get('totalItems', 0)} books\n")
    
    for i, item in enumerate(books_data["items"], 1):
        info = item.get("volumeInfo", {})
        
        title = info.get("title", "N/A")
        authors = ", ".join(info.get("authors", ["Unknown"]))
        published = info.get("publishedDate", "N/A")
        description = info.get("description", "No description available")[:150]
        
        print(f"{i}. {title}")
        print(f"   Authors: {authors}")
        print(f"   Published: {published}")
        print(f"   Description: {description}...")
        print(f"   Volume ID: {item.get('id', 'N/A')}")
        print()



def extract_books_items(response):
    """
    Extract items array from Google Books API response.
    
    Args:
        response (dict): Google Books API response
        
    Returns:
        list: List of book items, empty list if not found
    """
    if not response:
        return []
    
    returnobj = []
    for items in response:
        for obj in items['items']:
            returnobj.append(obj)
 
    return returnobj


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20  # default items per page
    page_size_query_param = 'page_size'
    max_page_size = 100