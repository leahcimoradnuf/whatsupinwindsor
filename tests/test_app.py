import pytest
from tests.seed import SeedData
from bs4 import BeautifulSoup

# Test routes
def test_v05_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_v05_about(client):
    response = client.get("/about")
    assert response.status_code == 200

def test_v05_support(client):
    response = client.get("/support")
    assert response.status_code == 200

def test_v05_contact(client):
    response = client.get("/contact")
    assert response.status_code == 200

def test_v05_articles(client):
    response = client.get("/articles")
    assert response.status_code == 200

def test_v05_signup(client):
    response = client.get("/signup")
    assert response.status_code == 200

def test_v05_valid_article_id(client):
    data = SeedData()
    response = client.get(f"/articles/{data.articles[0]['meeting_id']}")
    assert response.status_code == 200

def test_v05_invalid_article_id(client):
    response = client.get("/articles/poop")
    assert response.status_code == 404

def test_v05_index_empty(empty_client):
    response = empty_client.get("/")
    assert response.status_code == 200

def test_v05_articles_empty(empty_client):
    response = empty_client.get("/articles")
    assert response.status_code == 200

@pytest.mark.parametrize("route", ["/", "/about", "/contact", "/support", "/articles"])
def test_internal_links_resolve(client, route):
    response = client.get(route)
    soup = BeautifulSoup(response.data, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):  # internal links only
            assert client.get(href).status_code == 200