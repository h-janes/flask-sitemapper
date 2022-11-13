import flask

from flask_sitemapper import Sitemapper

# ----------------- TEST APP -----------------

sitemapper = Sitemapper()
app = flask.Flask(__name__)
sitemapper.init_app(app)


@sitemapper.include(lastmod="2022-02-01", changefreq="monthly")
@app.route("/")
def r_home():
    return "<h1>Home</h1>"


@sitemapper.include()
@app.route("/about")
def r_about():
    return "<h1>About</h1>"


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
    <loc>https://localhost/</loc>
    <lastmod>2022-02-01</lastmod>
    <changefreq>monthly</changefreq>
  </url>
  <url>
    <loc>https://localhost/about</loc>
  </url>
</urlset>"""
        )
