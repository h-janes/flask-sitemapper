# Necessary imports
import flask
from flask_sitemapper import Sitemapper

# Create the test app
app = flask.Flask("test_app")
app.config["SERVER_NAME"] = "127.0.0.1:5000"  # SERVER_NAME is required
app.config["PREFFERED_URL_SCHEME"] = "http"

# Initialise sitemapper
sitemapper = Sitemapper(app)

# Define a route and include it in the sitemap with all arguments
@sitemapper.include(lastmod="2022-02-08", changefreq="monthly", priority=1.0)
@app.route("/")
def r_home():
    return "<h1>Home Page</h1>"


# Define another route and include it in the sitemap without arguments
@sitemapper.include()
@app.route("/about")
def r_about():
    return "<h1>About Page</h1>"


# Only the last URL will be included in the sitemap
@sitemapper.include()
@app.route("/shop")  # This won't be included
@app.route("/buy")  # This won't be included
@app.route("/store")  # This will be included
def r_store():
    return "<h1>Store Page</h1>"


# This route will not appear in the sitemap
@app.route("/admin")
def r_admin():
    return "<h1>Admin Page</h1>"


# Creating a second sitemap
sitemapper2 = Sitemapper(app, url_path="/sitemap_2.xml")

# Adding a route to the second sitemap
@sitemapper2.include()
@app.route("/something")
def r_something():
    return "<h1>Something...</h1>"


# Run the test app
app.run()
