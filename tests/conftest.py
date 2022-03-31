import os
import pytest
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
    db.drop_collection('users')
    db.drop_collection('classes')
    db.drop_collection('enrollments')
    db.drop_collection('assignments')
    db.drop_collection('submissions')

    # insert users
    admin_id = db['users'].insert_one({
        'username': 'admin', 'password': 'password', 
        'firstname': 'Admin', 'lastname': 'User',
        'email': 'admin@example.com',
        'role': 4, 'approved': True
    }).inserted_id
    teacher_id = db['users'].insert_one({
        'username': 'teacher', 'password': 'password', 
        'firstname': 'Teacher', 'lastname': 'User', 
        'email': 'teacher@example.com',
        'role': 3, 'approved': True
    }).inserted_id
    asst_id = db['users'].insert_one({
        'username': 'teachasst', 'password': 'password', 
        'firstname': 'Assistant', 'lastname': 'User', 
        'email': 'teachasst@example.com',
        'role': 2, 'approved': True
    }).inserted_id
    student1_id = db['users'].insert_one({
        'username': 'student1', 'password': 'password', 
        'firstname': 'Student1', 'lastname': 'User', 
        'email': 'student1@example.com',
        'role': 1, 'approved': True
    }).inserted_id
    student2_id = db['users'].insert_one({
        'username': 'student2', 'password': 'password', 
        'firstname': 'Student2', 'lastname': 'User', 
        'email': 'student2@example.com',
        'role': 1, 'approved': True
    }).inserted_id

    # insert classes
    class1_id = db['classes'].insert_one({
        'code': 'TEST001', 'name': 'Test Course 1', 'desc': 'This is the first test course!',
    }).inserted_id
    class2_id = db['classes'].insert_one({
        'code': 'TEST002', 'name': 'Test Course 2', 'desc': 'This is the second test course!',
    }).inserted_id
    db['classes'].insert_one({
        'code': 'BLANK001', 'name': 'Hidden Course', 'desc': 'No-one should see this!',
    }).inserted_id

    # create enrollments
    # teacher & ta are in both classes; student 1 is in first; student 2 is in second
    db['enrollments'].insert_one({
        'class': ObjectId(class1_id), 'user': ObjectId(teacher_id)
    })
    db['enrollments'].insert_one({
        'class': ObjectId(class2_id), 'user': ObjectId(teacher_id)
    })
    db['enrollments'].insert_one({
        'class': ObjectId(class1_id), 'user': ObjectId(asst_id)
    })
    db['enrollments'].insert_one({
        'class': ObjectId(class2_id), 'user': ObjectId(asst_id)
    })
    db['enrollments'].insert_one({
        'class': ObjectId(class1_id), 'user': ObjectId(student1_id)
    })
    db['enrollments'].insert_one({
        'class': ObjectId(class2_id), 'user': ObjectId(student2_id)
    })

    # create assignments
    # class 1 will have 3 assignments, class 2 will have 0
    # deadlines might need to change later
    tempdue = datetime.now() + timedelta(days=7)
    assg1_id = db['assignments'].insert_one({
        'class': ObjectId(class1_id), 'name': 'Test Assignment 1', 
        'desc': 'This is the test assignment!', 'deadline': tempdue
    }).inserted_id
    db['assignments'].insert_one({
        'class': ObjectId(class1_id), 'name': 'Test Assignment 2', 
        'desc': 'This is the second assignment!', 'deadline': tempdue
    })
    db['assignments'].insert_one({
        'class': ObjectId(class1_id), 'name': 'Test Assignment 3', 
        'desc': 'This is the third assignment!', 'deadline': tempdue
    })

    # create submissions
    # student 1 submits to assignment 1 in class 1 ONLY
    db['submissions'].insert_one({
        'assignment': ObjectId(assg1_id), 'user': ObjectId(student1_id), 
        'class': ObjectId(class1_id), 'timestamp': datetime.now(),
        'contents': 'This is the test submission!', 'comments': []
    })

def check_db(db):
    """Checks DB to make sure entries are in the right place."""

    # check counts
    assert db['users'].count_documents({}) == 5
    assert db['classes'].count_documents({}) == 3
    assert db['enrollments'].count_documents({}) == 6
    assert db['assignments'].count_documents({}) == 3
    assert db['submissions'].count_documents({}) == 1

    # get list of objects in each collection
    print("- Collections:", db.list_collection_names())
    print("- Users:", db['users'].distinct('username'))
    print("- Classes:", db['classes'].distinct('code'))
    print("- Assignments:", db['assignments'].distinct('name'))

def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    # print
    print("Setting up test environment...")

    # if on github, initialize database
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("Detected github actions, setting local MONGO_URI...")

        # set client to local database
        # NOTE: This proved to be a big PITA to get working.
        #       While most drivers will want the suffix to be set to the auth collection name,
        #       Flask_PyMongo requires for it to be the table that you wish to default to.
        #       This URI will still work for MongoClient luckily, but you'll still need to
        #       pick the DB. Don't mess with this unless you know what you're doing.
        pytest.MONGO_URI = "mongodb://localhost:27017/canvas2_test"

    # else, if at home, just use test atlas DB
    else:
        print("Local run detected, swapping to test db...")

        # load flaskenv
        load_dotenv(".flaskenv")

        # see if we have a environment variable
        if not os.environ.get("MONGO_URI"):
            raise Exception("MONGO_URI env var is not set!")
            
        # initialize database
        pytest.MONGO_URI = os.environ.get("MONGO_URI").replace("canvas2", "canvas2_test")

    # print our string
    print("Configuring using URI: " + pytest.MONGO_URI)

    # initialize test database
    print("Re-initializing database...")
    client = MongoClient(pytest.MONGO_URI)
    init_db(client['canvas2_test'])

    # check database
    print("Checking database...")
    check_db(client['canvas2_test'])

    # save database conn to pytest, for use in tests
    pytest.db = client['canvas2_test']

    # done!
    print("Done! Ready to test!")


def pytest_unconfigure(config):
    """
    Called before test process is exited.
    """

    # print
    print("Cleaning up test environment...")

    # close database connection
    # NOTE: Disabled for now, since keeping connections open for MongoDB is apparently good?
    #       In my hours of scouring the internet, saw some stack comment mentioning it, but now
    #       I can't find it for the life of me. I'm not sure how true it is, but uh... Makes my 
    #       life easier so whatever, I guess! -A
    # client = MongoClient(os.environ.get("MONGO_URI"))
    # client.drop_database('canvas2_test')


@pytest.fixture
def app():

    # make sure our mongo uri is set
    if not pytest.MONGO_URI:
        raise Exception("MONGO_URI global is not set! Potential race condition?")

    # create app using testing config
    app = create_app({
        'TESTING': True,
        'MONGO_URI': pytest.MONGO_URI
    })

    # return it
    return app


@pytest.fixture
def client(app):
    return app.test_client()
