import requests

def file_iterator(url, chunk_size=8192):
    """
    Iterate over chunks of a file fetched from a given URL.

    This function reads a file from the provided URL in small chunks and
    yields each chunk as it's received. It allows for streaming file content
    from an external source, making it memory-efficient for large files.
    """
    response = requests.get(url)
    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            yield chunk
