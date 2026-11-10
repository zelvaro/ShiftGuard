SIGNUP = {
    "company_name": "Atlas Sécurité",
    "full_name": "Sabir Essaad",
    "email": "Admin@Atlas.ma",
    "password": "motdepasse-solide",
}


def signup(client, **overrides):
    return client.post("/api/v1/auth/signup", json={**SIGNUP, **overrides})


def login(client, email="admin@atlas.ma", password="motdepasse-solide"):
    return client.post("/api/v1/auth/login", data={"username": email, "password": password})


def test_signup_creates_admin_and_returns_token(client):
    r = signup(client)
    assert r.status_code == 201
    token = r.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "admin@atlas.ma"  # normalisé en minuscules
    assert body["role"] == "admin"


def test_signup_duplicate_email_is_rejected(client):
    assert signup(client).status_code == 201
    r = signup(client, company_name="Autre société", email="ADMIN@atlas.ma")
    assert r.status_code == 409


def test_signup_validates_input(client):
    assert signup(client, password="court").status_code == 422
    assert signup(client, email="pas-un-email").status_code == 422


def test_login_ok(client):
    signup(client)
    r = login(client, email="ADMIN@ATLAS.MA")
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_login_wrong_password_or_unknown_email(client):
    signup(client)
    assert login(client, password="mauvais-mot-de-passe").status_code == 401
    assert login(client, email="inconnu@atlas.ma").status_code == 401


def test_me_requires_valid_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    bad = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert bad.status_code == 401


def test_password_is_hashed(client, db_session):
    from app.models import User

    signup(client)
    user = db_session.query(User).one()
    assert user.password_hash != SIGNUP["password"]
    assert user.password_hash.startswith("$argon2")
