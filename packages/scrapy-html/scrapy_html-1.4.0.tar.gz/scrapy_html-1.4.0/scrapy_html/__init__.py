"""
Scrapy-HTML - Um pacote Python para scraping de conteúdo HTML.
"""

from .scraper import get_html_content
from .validators import DataValidator

__version__ = "0.1.0"
__all__ = ["get_html_content", "DataValidator"]
