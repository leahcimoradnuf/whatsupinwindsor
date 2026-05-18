import os

# Test Auth
def test_v07_admin_route_redirects_when_not_logged_in(client):
    response = client.get("/admin")
    assert response.status_code == 302

def test_v07_login_get_renders_form(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_v07_login_post_correct_password(client):
    response = client.post("/login", data={"passkey": os.getenv("ADMIN-PASSWORD")})
    assert response.status_code == 302

def test_v07_login_post_wrong_password(client):
    response = client.post("/login", data={"passkey": "wrongpassword"})
    assert response.status_code == 302
    # should redirect back to login, not dashboard

def test_v07_admin_accessible_when_logged_in(admin_client):
    response = admin_client.get("/admin")
    assert response.status_code == 200

def test_v07_logout_clears_session(admin_client):
    admin_client.get("/logout")
    response = admin_client.get("/admin")
    assert response.status_code == 302

# Test New Admin Routes
def test_v07_admin_article_edit(admin_client, seeded_db):
    response = admin_client.get("/admin/articles/town_council_1263_2026")
    assert response.status_code == 200

def test_v07_admin_view(admin_client, seeded_db):
    response = admin_client.get("/")
    assert response.status_code == 200