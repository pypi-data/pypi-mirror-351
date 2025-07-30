import requests


def read_url(url: str):
    response = requests.get(url, stream=True)
    for line in response.iter_lines():
        if line:
            yield line.decode('utf-8').strip()


def read_file(file_path: str):
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


def get_lines(path: str):
    """
    Generator function to read lines from a file or URL.
    
    Args:
        path (str): The file path or URL to read from.
    Yields:
        str: Lines from the file or URL.
    """
    if path.startswith("http"):
        yield from read_url(path)
    else:
        yield from read_file(path)
