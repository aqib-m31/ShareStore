import requests


def file_iterator(url, chunk_size=8192):
    response = requests.get(url)
    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            yield chunk
