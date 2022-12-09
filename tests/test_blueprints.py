import flask
import pytest

from flask_sitemapper import Sitemapper


@pytest.fixture
def client():
    sitemapper = Sitemapper()

    about = flask.Blueprint("about", __name__)

    @sitemapper.include()
    @about.route("/about")
    def r_about():
        return "<h1>About</h1>"

    contact = flask.Blueprint("contact", __name__, url_prefix="/contact")

    @sitemapper.include()
    @contact.route("/email")
    def r_email():
        return "<h1>Email</h1>"

    app = flask.Flask(__name__)
    app.register_blueprint(about)
    app.register_blueprint(contact)
    sitemapper.init_app(app)

    @sitemapper.include()
    @app.route("/")
    def r_home():
        return "<h1>Home</h1>"

    @app.route("/sitemap.xml")
    def r_sitemap():
        return sitemapper.generate()

    return app.test_client()


@pytest.fixture
def expected_xml():
    return """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://localhost/about</loc>
  </url>
  <url>
    <loc>https://localhost/contact/email</loc>
  </url>
  <url>
    <loc>https://localhost/</loc>
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
