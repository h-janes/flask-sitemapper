import flask

from flask_sitemapper import Sitemapper

# ----------------- TEST APP -----------------

sitemapper1 = Sitemapper()
sitemapper2 = Sitemapper()
master_sitemapper = Sitemapper(master=True)

app = flask.Flask(__name__)

sitemapper1.init_app(app)
sitemapper2.init_app(app)
master_sitemapper.init_app(app)


@sitemapper1.include()
@app.route("/")
def r_home():
    return "<h1>Home</h1>"


@sitemapper2.include()
@app.route("/about")
def r_about():
    return "<h1>About</h1>"


@master_sitemapper.include()
@app.route("/sitemap1.xml")
def r_sitemap1():
    return sitemapper1.generate()


@master_sitemapper.include()
@app.route("/sitemap2.xml")
def r_sitemap2():
    return sitemapper1.generate()


@app.route("/sitemap.xml")
def r_sitemap_index():
    return master_sitemapper.generate()


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
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://localhost/sitemap1.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://localhost/sitemap2.xml</loc>
  </sitemap>
</sitemapindex>"""
        )
