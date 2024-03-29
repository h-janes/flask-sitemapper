import gzip

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

    @app.route("/sitemap.xml")
    def r_sitemap():
        return sitemapper.generate(gzip=True)

    return app.test_client()


@pytest.fixture
def expected_xml():
    return """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://localhost/</loc>
  </url>
</urlset>"""


def test_running(client):
    response = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.text == "<h1>Home</h1>"


def test_status_code(client):
    response = client.get("/sitemap.xml", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200


def test_encoding(client):
    response = client.get("/sitemap.xml", headers={"Accept-Encoding": "gzip"})
    assert response.headers["Content-Encoding"] == "gzip"


def test_mimetype(client):
    response = client.get("/sitemap.xml", headers={"Accept-Encoding": "gzip"})
    assert response.mimetype == "application/xml"


def test_xml(client, expected_xml):
    response = client.get("/sitemap.xml", headers={"Accept-Encoding": "gzip"})
    data = str(gzip.decompress(response.data), "utf-8")
    assert data == expected_xml


def test_not_accepting_gzip(client, expected_xml):
    response = client.get("/sitemap.xml")
    assert response.text == expected_xml
