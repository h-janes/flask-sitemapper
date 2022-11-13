import flask

from flask_sitemapper import Sitemapper

# ----------------- TEST APP -----------------

sitemapper = Sitemapper()

about = flask.Blueprint("about", __name__)


@sitemapper.include(lastmod="2022-02-03")
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


@sitemapper.include(lastmod="2022-02-01", changefreq="monthly")
@app.route("/")
def r_home():
    return "<h1>Home</h1>"


@app.route("/admin")
def r_admin():
    return "<h1>Admin</h1>"


@app.route("/sitemap.xml")
def r_sitemap():
    return sitemapper.generate()


# ----------------- END TEST APP -----------------


def test_running():
    with app.test_client() as test_client:
        response = test_client.get("/")
        assert response.text == "<h1>Home</h1>"


def test_status_code():
    with app.test_client() as test_client:
        response = test_client.get("/sitemap.xml")
        assert response.status_code == 200


def test_mimetype():
    with app.test_client() as test_client:
        response = test_client.get("/sitemap.xml")
        assert response.mimetype == "application/xml"


def test_xml():
    with app.test_client() as test_client:
        response = test_client.get("/sitemap.xml")
        assert (
            response.text
            == """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://localhost/about</loc>
    <lastmod>2022-02-03</lastmod>
  </url>
  <url>
    <loc>https://localhost/contact/email</loc>
  </url>
  <url>
    <loc>https://localhost/</loc>
    <lastmod>2022-02-01</lastmod>
    <changefreq>monthly</changefreq>
  </url>
</urlset>"""
        )
