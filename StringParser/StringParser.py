from unicodedata import normalize
from html import unescape
from datetime import datetime
import re

class Parser:
    """Custom parser for spider.py"""

    def __init__(self,mode,encoding,decoding):
        self.normalization_mode = mode
        self.encoding = encoding
        self.decoding = decoding

    def normalizer(self,string):
        try:
            return normalize(self.normalization_mode,string).encode(self.encoding, 'ignore').decode(self.decoding)

        except TypeError:
            return 'N/A'

    def cleaner(self,pat,sub,string):
        return re.sub(pat,sub,string)

    def spliter(self,pat,string):
        return re.split(pat,string)

    def searcher(self,pat,string):
        try:
            return re.search(pat,string).group(1).strip()

        except AttributeError:
            return 'N/A'

    def convert_to_datetime(self,string,format):
        try:
            return datetime.strptime(string,format)

        except ValueError:
            return 'N/A'

    def unescape_html(self,string):
        return unescape(string)
