import os
import pytest
import nltk
from bson import ObjectId
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from canvas2 import create_app


def init_db(db):
    """
    Initialize the database.
    """

    # drop all collections
    db.drop_collection("users")
    db.drop_collection("classes")
    db.drop_collection("enrollments")
    db.drop_collection("assignments")
    db.drop_collection("submissions")

    # insert users
    # NOTE: username == password for testing purposes
    admin_id = (
        db["users"]
        .insert_one(
            {
                "username": "admin",
                "password": "$2b$14$XvXqLn3QFEkJHHOzEMkgAuIHcXvw.2jcnaddbY9hBcglJxmDeAtmi",
                "firstname": "Admin",
                "lastname": "User",
                "email": "admin@example.com",
                "role": 4,
                "approved": True,
            }
        )
        .inserted_id
    ); admin_id = admin_id # flask8: noqa; shhhhh......
    teacher_id = (
        db["users"]
        .insert_one(
            {
                "username": "teacher",
                "password": "$2b$14$asNJZSOhP/vUd9tdnzsd3OclY2vWnusEYDS9tAyJVPb.4F5VUcj2q",
                "firstname": "Teacher",
                "lastname": "User",
                "email": "teacher@example.com",
                "role": 3,
                "approved": True,
            }
        )
        .inserted_id
    )
    teacher2_id = (  # noqa: F841
        db["users"]
        .insert_one(
            {
                "username": "teacher2",
                "password": "password",
                "firstname": "Teacher2",
                "lastname": "User",
                "email": "teacher2@example.com",
                "role": 3,
                "approved": True,
            }
        )
        .inserted_id
    )
    asst_id = (
        db["users"]
        .insert_one(
            {
                "username": "teachasst",
                "password": "$2b$14$asNJZSOhP/vUd9tdnzsd3ONgDV4NouCVufDveRd9qtDuxSNaNncvK",
                "firstname": "Assistant",
                "lastname": "User",
                "email": "teachasst@example.com",
                "role": 2,
                "approved": True,
            }
        )
        .inserted_id
    )
    student1_id = (
        db["users"]
        .insert_one(
            {
                "username": "student1",
                "password": "$2b$14$asNJZSOhP/vUd9tdnzsd3OmV.pqlRhTijFwXRl3zgv68QTHPE1N2q",
                "firstname": "Student1",
                "lastname": "User",
                "email": "student1@example.com",
                "role": 1,
                "approved": True,
            }
        )
        .inserted_id
    )
    student2_id = (
        db["users"]
        .insert_one(
            {
                "username": "student2",
                "password": "password",
                "firstname": "$2b$14$asNJZSOhP/vUd9tdnzsd3OJxxTLoFKtafOG1THK0cM5icGl0YHhfK",
                "lastname": "User",
                "email": "student2@example.com",
                "role": 1,
                "approved": True,
            }
        )
        .inserted_id
    )

    # insert classes
    class1_id = (
        db["classes"]
        .insert_one(
            {
                "code": "TEST001",
                "title": "Test Course 1",
                "desc": "This is the first test course!",
            }
        )
        .inserted_id
    )
    class2_id = (
        db["classes"]
        .insert_one(
            {
                "code": "TEST002",
                "title": "Test Course 2",
                "desc": "This is the second test course!",
            }
        )
        .inserted_id
    )
    db["classes"].insert_one(
        {
            "code": "BLANK001",
            "title": "Hidden Course",
            "desc": "No-one should see this!",
        }
    ).inserted_id

    # create enrollments
    # teacher & ta are in both classes
    # student 1 is in first; student 2 is in second
    db["enrollments"].insert_one(
        {"class": ObjectId(class1_id), "user": ObjectId(teacher_id)}
    )
    db["enrollments"].insert_one(
        {"class": ObjectId(class2_id), "user": ObjectId(teacher_id)}
    )
    db["enrollments"].insert_one(
        {"class": ObjectId(class1_id), "user": ObjectId(asst_id)}
    )
    db["enrollments"].insert_one(
        {"class": ObjectId(class2_id), "user": ObjectId(asst_id)}
    )
    db["enrollments"].insert_one(
        {"class": ObjectId(class1_id), "user": ObjectId(student1_id)}
    )
    db["enrollments"].insert_one(
        {"class": ObjectId(class2_id), "user": ObjectId(student2_id)}
    )

    # create assignments
    # class 1 will have 3 assignments, class 2 will have 0
    # deadlines might need to change later
    tempdue = datetime.now() + timedelta(days=7)
    assg1_id = (
        db["assignments"]
        .insert_one(
            {
                "class": ObjectId(class1_id),
                "title": "Test Assignment 1",
                "description": "This is the test assignment!",
                "deadline": tempdue,
            }
        )
        .inserted_id
    )
    db["assignments"].insert_one(
        {
            "class": ObjectId(class1_id),
            "title": "Test Assignment 2",
            "description": "This is the second assignment!",
            "deadline": tempdue,
        }
    )
    db["assignments"].insert_one(
        {
            "class": ObjectId(class1_id),
            "title": "Test Assignment 3",
            "description": "This is the third assignment!",
            "deadline": tempdue,
        }
    )

    # create submissions
    # student 1 submits to assignment 1 in class 1 ONLY
    db["submissions"].insert_one(
        {
            "assignment": ObjectId(assg1_id),
            "user": ObjectId(student1_id),
            "class": ObjectId(class1_id),
            "timestamp": datetime.now(),
            "contents": "This is the test submission!",
            "comments": [],
            "simhash": 0.0,
            "grade": 0.0,
        }
    )


def check_db(db):
    """Checks DB to make sure entries are in the right place."""

    # check counts
    assert db["users"].count_documents({}) >= 4
    assert db["classes"].count_documents({}) == 3
    assert db["enrollments"].count_documents({}) == 6
    assert db["assignments"].count_documents({}) == 3
    assert db["submissions"].count_documents({}) == 1

    # get list of objects in each collection
    print("- Collections:", db.list_collection_names())
    print("- Users:", db["users"].distinct("username"))
    print("- Classes:", db["classes"].distinct("code"))
    print("- Assignments:", db["assignments"].distinct("title"))


def init_nltk():
    """
    Initializes the NLTK library with required corpora and tokenizers.
    """
    required = ["stopwords", "brown", "omw-1.4", "wordnet", "punkt"]
    for x in required:
        nltk.download(x)


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    # NOTE: A cautionary tale for any devs looking at this in the future:
    #
    # Getting the database to connect proved to be a bigger issue than
    # expected. This project uses two MongoDB drivers to help it run. They are
    # PyMongo.MongoClient and Flask_PyMongo.PyMongo. Flask_PyMongo is used
    # in-app because it meshes with Flask better than the MongoClient driver.
    # However, because our test suite is not a flask app, we have to use
    # MongoClient out here to prep the db before tests. IT IS EXTREMELY
    # IMPORTANT TO KNOW THAT THESE TWO PACKAGES HAVE ONE FUNDAMENTAL DIFFERENCE
    # FROM OTHER PACKAGES WHEN IT COMES TO CONNECTING USING A URI.
    #
    # Most packages (like PyMongo.MongoClient) would have you append a
    # `defaultAuthDB` to the end of your URI, used to specify which table to
    # authenticate against, before letting you specify the database you wish
    # to actually use later in the runtime. FLASK_PYMONGO DOES NOT DO THIS.
    # Flask_PyMongo instead desires the database you wish to use during
    # runtime to be appended to the end of the URI, rather than the
    # defaultAuthDB.
    #
    # If you start getting mysterious runtime errors, where you confirm your
    # collections are being made in the test suite, but later not being
    # properly reflected in the actual application, it is more than likely
    # that your MONGO_URI is malformed and PyMongo.MongoClient is working
    # properly while Flask_PyMongo.PyMongo is read/writing to whatever
    # database you have appended, rather than the one you desire. You should
    # double check your MONGO_URI env var and make sure
    # it looks like this:
    #
    #     MONGO_URI=mongodb[+srv]://user:pass@host[:port]/database
    #
    # In the case of this project, `database` should always be either
    # `canvas2` or `canvas2_test`. This bug has wasted so many hours of dev
    # time, both while indev and while in testing that I feel I MUST leave
    # this long-ass note here. Don't make my mistakes again. And if you do,
    # feel free to increment the counter below.
    #
    # Total man-hours wasted on this: ~5 hours

    # print
    print("Setting up test environment...")

    # initialize NLTK with corpora and tokenizers
    init_nltk()

    # if on github, initialize database
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("Detected github actions, setting local MONGO_URI...")

        # set client to local database
        pytest.MONGO_URI = "mongodb://localhost:27017/canvas2_test"

    # else, if at home, just use test atlas DB
    else:
        print("Local run detected, swapping to test db...")

        # load flaskenv
        load_dotenv(".flaskenv")

        # see if we have a environment variable
        if not os.environ.get("MONGO_URI"):
            raise Exception("MONGO_URI env var is not set!")

        # ensure the URI meets our specifications
        # NOTE: "mirrored" with utils/db.py
        if "canvas2" not in os.environ.get("MONGO_URI"):
            raise Exception(
                "MONGO_URI was loaded, but is improper!\n\n"
                + "Survey says you appended either a random db or your "
                + "default auth db to the end\nof your URI. STOP! "
                + "Flask-PyMongo will not work with this URI! Your URI MUST "
                + "end\nwith the name of the default db you wish to use, i.e. "
                + "either canvas2 or canvas2_test,\nno others will work! "
                + "Please fix this and try again!"
            )

        # set URI to atlas test DB
        pytest.MONGO_URI = os.environ.get("MONGO_URI").replace(
            "canvas2", "canvas2_test"
        )

    # print our string
    print("Configuring using URI: " + pytest.MONGO_URI)

    # initialize test database
    print("Re-initializing database...")
    client = MongoClient(pytest.MONGO_URI)
    init_db(client["canvas2_test"])

    # check database
    print("Checking database...")
    check_db(client["canvas2_test"])

    # save database conn to pytest, for use in tests
    pytest.db = client["canvas2_test"]

    # done!
    print("Done! Ready to test!")


def pytest_unconfigure(config):
    """
    Called before test process is exited.
    """

    # print
    print("Cleaning up test environment...")

    # close database connection
    # NOTE: Disabled for now, since keeping connections open for MongoDB is
    #       apparently good? In my hours of scouring the internet, saw some
    #       stack comment mentioning it, but now I can't find it for the life
    #       of me. I'm not sure how true it is, but uh... Makes my
    #       life easier so whatever, I guess! -A
    # client = MongoClient(os.environ.get("MONGO_URI"))
    # client.drop_database('canvas2_test')


@pytest.fixture
def app():

    # make sure our mongo uri is set
    if not pytest.MONGO_URI:
        raise Exception(
            "MONGO_URI global is not set! Potential race condition?"
        )

    # create app using testing config
    app = create_app({"TESTING": True, "MONGO_URI": pytest.MONGO_URI})

    # return it
    return app


@pytest.fixture
def client(app):
    return app.test_client()
