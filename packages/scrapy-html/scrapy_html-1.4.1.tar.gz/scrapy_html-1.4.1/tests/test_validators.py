"""
Testes para o módulo de validação e limpeza de dados.
"""
from bs4 import BeautifulSoup

from scrapy_html.validators import DataValidator


def test_clean_text():
    """Testa a limpeza de texto."""
    validator = DataValidator()
    
    # Teste com texto normal
    assert validator.clean_text("  Hello   World  ") == "Hello World"
    
    # Teste com caracteres especiais
    assert validator.clean_text("Hello\n\tWorld") == "Hello World"
    
    # Teste com entidades HTML
    assert validator.clean_text("Hello &amp; World") == "Hello & World"
    
    # Teste com tipo não string
    assert validator.clean_text(123) == "123"


def test_clean_html():
    """Testa a limpeza de HTML."""
    validator = DataValidator()
    
    html = """
    <html>
        <head>
            <script>alert('test');</script>
            <style>body { color: red; }</style>
            <meta name="description" content="test">
        </head>
        <body>
            <!-- Comment -->
            <p>Hello World</p>
        </body>
    </html>
    """
    
    cleaned = validator.clean_html(html)
    soup = BeautifulSoup(cleaned, 'html.parser')
    
    # Verifica se scripts foram removidos
    assert not soup.find('script')
    
    # Verifica se estilos foram removidos
    assert not soup.find('style')
    
    # Verifica se meta tags foram removidas
    assert not soup.find('meta')
    
    # Verifica se comentários foram removidos
    assert not soup.find(
        string=lambda s: isinstance(s, str) and 
        s.strip().startswith('<!--')
    )
    
    # Verifica se o conteúdo principal permanece
    assert soup.find('p').text.strip() == "Hello World"


def test_validate_url():
    """Testa a validação de URLs."""
    validator = DataValidator()
    
    # URLs válidas
    assert validator.validate_url("http://example.com")
    assert validator.validate_url("https://example.com")
    assert validator.validate_url("http://localhost:8000")
    assert validator.validate_url("http://192.168.1.1")
    
    # URLs inválidas
    assert not validator.validate_url("not-a-url")
    assert not validator.validate_url("ftp://example.com")
    assert not validator.validate_url("http://")
    assert not validator.validate_url(123)


def test_sanitize_attributes():
    """Testa a sanitização de atributos."""
    validator = DataValidator()
    
    # Teste com tag <a>
    html = '<a href="http://example.com" onclick="alert(1)" title="Link">Link</a>'
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('a')
    sanitized = validator.sanitize_attributes(tag)
    
    assert 'href' in sanitized.attrs
    assert 'title' in sanitized.attrs
    assert 'onclick' not in sanitized.attrs
    
    # Teste com tag <img>
    html = '<img src="image.jpg" onerror="alert(1)" alt="Image">'
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('img')
    sanitized = validator.sanitize_attributes(tag)
    
    assert 'src' in sanitized.attrs
    assert 'alt' in sanitized.attrs
    assert 'onerror' not in sanitized.attrs
    
    # Teste com tipo não Tag
    assert validator.sanitize_attributes("not a tag") == "not a tag"


def test_extract_structured_data():
    """Testa a extração de dados estruturados."""
    validator = DataValidator()
    
    html = """
    <html>
        <head>
            <meta name="description" content="Test description">
            <meta property="og:title" content="Test OG Title">
            <meta name="twitter:card" content="summary">
            <script type="application/ld+json">
                {"@context": "http://schema.org", "@type": "WebPage"}
            </script>
        </head>
        <body>
            <p>Content</p>
        </body>
    </html>
    """
    
    data = validator.extract_structured_data(html)
    
    # Verifica meta tags
    assert data['meta']['description'] == "Test description"
    
    # Verifica Open Graph
    assert data['open_graph']['title'] == "Test OG Title"
    
    # Verifica Twitter Cards
    assert data['twitter_cards']['card'] == "summary"
    
    # Verifica JSON-LD
    assert len(data['json_ld']) == 1
    assert data['json_ld'][0]['@type'] == "WebPage"
    
    # Teste com tipo não string
    assert validator.extract_structured_data(123) == {} 