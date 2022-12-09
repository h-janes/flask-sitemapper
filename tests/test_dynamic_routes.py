import flask
import pytest

from flask_sitemapper import Sitemapper


@pytest.fixture
def client():
    sitemapper = Sitemapper()
    app = flask.Flask(__name__)
    sitemapper.init_app(app)

    @sitemapper.include()
    @app.route("/")
    def r_home():
        return "<h1>Home</h1>"

    @sitemapper.include(url_variables={"user_id": [1, 2, 3]})
    @app.route("/user/<int:user_id>")
    def r_user(user_id):
        return f"<h1>User #{user_id}</h1>"

    @sitemapper.include(url_variables={"user_id": [1, 2, 3], "post_id": [4, 5, 5]})
    @app.route("/post/<int:user_id>_<int:post_id>")
    def r_post(user_id, post_id):
        return f"<h1>Post #{post_id} by user #{user_id}</h1>"

    @app.route("/sitemap.xml")
    def r_sitemap():
        return sitemapper.generate()

    return app.test_client()


@pytest.fixture
def expected_xml():
    return """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://localhost/</loc>
  </url>
  <url>
    <loc>https://localhost/user/1</loc>
  </url>
  <url>
    <loc>https://localhost/user/2</loc>
  </url>
  <url>
    <loc>https://localhost/user/3</loc>
  </url>
  <url>
    <loc>https://localhost/post/1_4</loc>
  </url>
  <url>
    <loc>https://localhost/post/2_5</loc>
  </url>
  <url>
    <loc>https://localhost/post/3_5</loc>
  </url>
</urlset>"""


def test_running(client):
    response = client.get("/")
    assert response.text == "<h1>Home</h1>"


def test_status_code(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200


def test_mimetype(client):
    response = client.get("/sitemap.xml")
    assert response.mimetype == "application/xml"


def test_xml(client, expected_xml):
    response = client.get("/sitemap.xml")
    assert response.text == expected_xml
