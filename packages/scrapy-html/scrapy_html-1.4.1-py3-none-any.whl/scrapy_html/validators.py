"""
Módulo de validação e limpeza de dados para o Scrapy-HTML.
"""
import html
import re
from typing import Any, Dict

from bs4 import BeautifulSoup, Tag


class DataValidator:
    """Classe para validação e limpeza de dados HTML."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Limpa o texto removendo espaços extras e caracteres especiais.
        
        Args:
            text: Texto a ser limpo
            
        Returns:
            Texto limpo
        """
        if not isinstance(text, str):
            return str(text)
        
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text)
        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # Decodifica entidades HTML
        text = html.unescape(text)
        return text.strip()
    
    @staticmethod
    def clean_html(html_content: str) -> str:
        """
        Limpa o HTML removendo scripts, estilos e outros elementos desnecessários.
        
        Args:
            html_content: Conteúdo HTML a ser limpo
            
        Returns:
            HTML limpo
        """
        if not isinstance(html_content, str):
            return str(html_content)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts e estilos
        for element in soup(['script', 'style', 'meta', 'link']):
            element.decompose()
            
        # Remove comentários
        for comment in soup.find_all(
            string=lambda s: isinstance(s, str) and 
            s.strip().startswith('<!--')
        ):
            comment.extract()
            
        return str(soup)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Valida se uma URL é válida.
        
        Args:
            url: URL a ser validada
            
        Returns:
            True se a URL for válida, False caso contrário
        """
        if not isinstance(url, str):
            return False
            
        url_pattern = re.compile(
            r'^(?:http|https)://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # porta opcional
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
        return bool(url_pattern.match(url))
    
    @staticmethod
    def sanitize_attributes(tag: Tag) -> Tag:
        """
        Sanitiza atributos de uma tag HTML.
        
        Args:
            tag: Tag BeautifulSoup a ser sanitizada
            
        Returns:
            Tag sanitizada
        """
        if not isinstance(tag, Tag):
            return tag
            
        # Lista de atributos permitidos
        allowed_attrs = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'div': ['class', 'id', 'title'],
            'span': ['class', 'id', 'title'],
            'p': ['class', 'id'],
            '*': ['class', 'id', 'title']
        }
        
        # Obtém atributos permitidos para a tag
        tag_name = tag.name.lower()
        attrs = allowed_attrs.get(tag_name, allowed_attrs['*'])
        
        # Remove atributos não permitidos
        for attr in list(tag.attrs):
            if attr not in attrs:
                del tag[attr]
                
        return tag
    
    @staticmethod
    def extract_structured_data(html_content: str) -> Dict[str, Any]:
        """
        Extrai dados estruturados do HTML (meta tags, JSON-LD, etc).
        
        Args:
            html_content: Conteúdo HTML
            
        Returns:
            Dicionário com dados estruturados
        """
        if not isinstance(html_content, str):
            return {}
            
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {
            'meta': {},
            'json_ld': [],
            'open_graph': {},
            'twitter_cards': {}
        }
        
        # Extrai meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                data['meta'][name] = content
                
        # Extrai JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data['json_ld'].append(json.loads(script.string))
            except (json.JSONDecodeError, TypeError):
                continue
                
        # Extrai Open Graph
        for meta in soup.find_all('meta', attrs={'property': re.compile(r'^og:')}):
            name = meta.get('property', '')[3:]  # Remove 'og:' do início
            data['open_graph'][name] = meta.get('content', '')
            
        # Extrai Twitter Cards
        for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = meta.get('name', '')[8:]  # Remove 'twitter:' do início
            data['twitter_cards'][name] = meta.get('content', '')
            
        return data 