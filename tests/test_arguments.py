import flask
import pytest

from flask_sitemapper import Sitemapper


@pytest.fixture
def client():
    sitemapper = Sitemapper()
    app = flask.Flask(__name__)
    sitemapper.init_app(app)

    @sitemapper.include(lastmod="2022-02-01", changefreq="monthly", priority=1.0)
    @app.route("/")
    def r_home():
        return "<h1>Home</h1>"

    @sitemapper.include(changefreq="yearly")
    @app.route("/about")
    def r_about():
        return "<h1>About</h1>"

    @app.route("/admin")
    def r_admin():
        return "<h1>Admin</h1>"

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
    <lastmod>2022-02-01</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://localhost/about</loc>
    <changefreq>yearly</changefreq>
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
