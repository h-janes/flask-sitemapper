import flask
import pytest

from flask_sitemapper import Sitemapper


def test_error():
    with pytest.raises(ValueError):
        sitemapper = Sitemapper()
        app = flask.Flask(__name__)
        sitemapper.init_app(app)

        @sitemapper.include()
        def r_home():
            return "<h1>Home</h1>"

        @app.route("/sitemap.xml")
        def r_sitemap():
            return sitemapper.generate()
