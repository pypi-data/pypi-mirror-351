from collections import defaultdict

from . import utils


class Term(object):
    """
    A class to represent a term in the OBO file.

    Attributes:
        data (dict): A dictionary containing the term data.
    """
    def __init__(self, data):
        self._data = data
        for k, v in data.items():
            setattr(self, k, v)

    def __repr__(self):
        return f'Term({self._data})'
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data.items())

    def __len__(self):
        return len(self._data)
    
    def get(self, key, default=None):
        return self._data.get(key, default)


class OBO_Parser(object):
    """
    A class to parse OBO (Open Biomedical Ontology) files.
    This class provides methods to extract headers and terms from the OBO file.

    Attributes:
        path (str): The path to the OBO file.
    """

    def __init__(self, path):
        self.path = path
        self._headers = None
        self._terms = None

    @property
    def headers(self):
        """
        Returns the headers of the OBO file.
        
        Returns:
            dict: A dictionary containing the headers of the OBO file.
        """
        if self._headers is None:
            self._parse_headers()
        return self._headers
    
    @property
    def terms(self):
        """
        Generator function to yield Term(terms) from the OBO file.
        
        Yields:
            dict: A dictionary representing a term in the OBO file.
        """
        if self._terms is None:
            self._terms = self._parse_terms()
        return self._terms

    def _parse_headers(self):
        self._headers = defaultdict(list)
        for line in utils.get_lines(self.path):
            if line == '[Term]':
                break

            key, value = line.split(': ', 1)
            if ' ' in value:
                self._headers[key].append(value)
            else:
                self._headers[key] = value

    def _parse_terms(self):
        start = False
        term = {}
        for line in utils.get_lines(self.path):
            if line == '[Term]':
                start = True
                if term:
                    yield Term(term)
                term = {}
                continue
            elif line == '[Typedef]':
                yield Term(term)
                break

            if start:
                key, value = line.split(': ', 1)
                term[key] = value
