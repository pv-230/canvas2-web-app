from urllib.request import urlopen

from flask_pymongo import PyMongo
from pymongo.errors import ServerSelectionTimeoutError

# static vars
db_conn = None


def init_db(app):
    """Initializes the database."""

    # register vars as global
    global db_conn

    # get app context for mongodb connection
    with app.app_context():

        # make sure we have a conn string
        # see: conftest.py:pytest_configure()
        if not app.config["MONGO_URI"]:
            raise Exception("MONGO_URI is not set!")

        # ensure the URI meets our specifications
        # NOTE: "mirrored" with conftest.py
        if "canvas2" not in app.config["MONGO_URI"]:
            raise Exception(
                "MONGO_URI was loaded, but is improper!\n\n"
                + "Survey says you appended either a random db or your "
                + "default auth db to the end\nof your URI. STOP! "
                + "Flask-PyMongo will not work with this URI! Your URI MUST"
                + "end\nwith the name of the default db you wish to use, i.e. "
                + "either canvas2 or canvas2_test,\nno others will work! "
                + "Please fix this and try again!"
            )

        # init mongodb connection and save it in global state
        # start by creating our client with a connection timeout of 3 seconds
        db_conn = PyMongo(app, serverSelectionTimeoutMS=3000)

        # now, test the connection
        # is not whitelisted, this will throw ServerSelectionTimeoutError
        # on fail, print verbose error to help other devs understand what's up
        try:
            db_conn.cx.server_info()
        except ServerSelectionTimeoutError:
            external_ip = urlopen("https://v4.ident.me").read().decode("utf8")
            print(
                "ERROR: Could not connect to Mongo! Please ensure that your "
                + "IP is whitelisted on Atlas!"
            )
            print(f"Your current IP: {external_ip}")
            exit(-1)
