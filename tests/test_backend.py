import pytest
from flask import session
from datetime import datetime, timedelta

def test_addcourse_good(client):
    """Tests adding a course to the database."""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        teacher = pytest.db['users'].find_one(
            {"username": "teacher"}
        )

        # set session vars
        prelim_session["id"] = str(teacher["_id"])
        prelim_session['username'] = teacher['username']
        prelim_session["fname"] = teacher["firstname"]
        prelim_session["lname"] = teacher["lastname"]
        prelim_session["role"] = teacher["role"]

    # use client context
    with client:

        # try logging in with user credentials
        res = client.post(
            "/secretary/add-course",
            data = {
                "course-name": "Test Course 3",
                "course-code": "TEST003",
                "course-desc": "This course was made by PyTest!"
            },
            follow_redirects=True
        )

        # check to make sure we were redirected
        # also check to see if new class is rendering
        assert res.status_code == 200
        assert res.request.path == "/"
        assert '<div class="course-code">TEST003</div>' in res.get_data(as_text=True)

        # assert class was actually created in db
        course = pytest.db['classes'].find_one(
            {"code": "TEST003"}
        )
        assert course is not None


def test_addcourse_noauth(client):
    """Tests adding a course to the database while a user is not logged in."""

    # use client context
    with client:

        # try logging in with user credentials
        res = client.post(
            "/secretary/add-course",
            data = {
                "course-name": "Test Course 4",
                "course-code": "TEST004",
                "course-desc": "This course should never be made by PyTest!"
            },
            follow_redirects=True
        )

        # check to make sure we were redirected
        # also check to see if new class is rendering
        assert res.status_code == 401

        # assert class was not created in db
        course = pytest.db['classes'].find_one(
            {"code": "TEST004"}
        )
        assert course is None


def test_addcourse_noperms(client):
    """Tests adding a course to the database while a user doesnt have perms."""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        student = pytest.db['users'].find_one(
            {"username": "student1"}
        )

        # set session vars
        prelim_session["id"] = str(student["_id"])
        prelim_session['username'] = student['username']
        prelim_session["fname"] = student["firstname"]
        prelim_session["lname"] = student["lastname"]
        prelim_session["role"] = student["role"]

    # use client context
    with client:

        # try logging in with user credentials
        res = client.post(
            "/secretary/add-course",
            data = {
                "course-name": "Test Course 4",
                "course-code": "TEST004",
                "course-desc": "This course should never be made by PyTest!"
            },
            follow_redirects=True
        )

        # check to make sure we were redirected
        # also check to see if new class is rendering
        assert res.status_code == 403

        # assert class was not created in db
        course = pytest.db['classes'].find_one(
            {"code": "TEST004"}
        )
        assert course is None


def test_submitasst_good(client):
    """Tests Student1 submitting to Assignment 2"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        student = pytest.db['users'].find_one(
            {"username": "student1"}
        )

        # set session vars
        prelim_session["id"] = str(student["_id"])
        prelim_session['username'] = student['username']
        prelim_session["fname"] = student["firstname"]
        prelim_session["lname"] = student["lastname"]
        prelim_session["role"] = student["role"]

        # get assignment id from db
        assignment = pytest.db['assignments'].find_one(
            {"name": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assignment",
            data = {
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest!",
                "assg-course": assignment["class"],
                "assg-user-id": str(student["_id"])
            },
            follow_redirects=True
        )

        # check to make sure we were redirected
        # also check to see if new class is rendering
        assert res.status_code == 200
        assert res.request.path == f"/c/{assignment['class']}"
        

def test_submitasst_csrf(client):
    """Tests Student2 submitting on Student1's behalf to Assignment 3"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        student = pytest.db['users'].find_one(
            {"username": "student2"}
        )

        # set session vars
        prelim_session["id"] = str(student["_id"])
        prelim_session['username'] = student['username']
        prelim_session["fname"] = student["firstname"]
        prelim_session["lname"] = student["lastname"]
        prelim_session["role"] = student["role"]

        student1_id = pytest.db['users'].find_one(
            {"username": "student1"}
        )["_id"]

        # get assignment id from db
        assignment = pytest.db['assignments'].find_one(
            {"name": "Test Assignment 3"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assignment",
            data = {
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest!",
                "assg-course": assignment["class"],
                "assg-user-id": str(student1_id)
            },
            follow_redirects=True
        )

        # check to make sure we were redirected
        # also check to see if new class is rendering
        assert res.status_code == 403

        # ensure no submission was made
        submission = pytest.db['submissions'].find_one(
            {"assignment": str(assignment["_id"]), "user": str(student1_id)}
        )
        assert submission is None
        

def test_submitasst_noasst(client):
    """Tests Student1 submitting to an assignment that doesnt exist"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        student = pytest.db['users'].find_one(
            {"username": "student1"}
        )

        # set session vars
        prelim_session["id"] = str(student["_id"])
        prelim_session['username'] = student['username']
        prelim_session["fname"] = student["firstname"]
        prelim_session["lname"] = student["lastname"]
        prelim_session["role"] = student["role"]

        # get assignment id from db
        assignment = pytest.db['assignments'].find_one(
            {"name": "Test Assignment 3"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assignment",
            data = {
                "assg-id": "624531668a53f81a7dff5452", # bogus assignment id
                "assg-entry": "This assignment submission was made by PyTest!",
                "assg-course": assignment["class"],
                "assg-user-id": str(student["_id"])
            },
            follow_redirects=True
        )

        # check return code
        assert res.status_code == 400

def test_submitasst_notenrolled(client):
    """Tests Student2 submitting to an assignment whose class they are not in"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        student = pytest.db['users'].find_one(
            {"username": "student2"}
        )

        # set session vars
        prelim_session["id"] = str(student["_id"])
        prelim_session['username'] = student['username']
        prelim_session["fname"] = student["firstname"]
        prelim_session["lname"] = student["lastname"]
        prelim_session["role"] = student["role"]

        # get assignment id from db
        assignment = pytest.db['assignments'].find_one(
            {"name": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assignment",
            data = {
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest!",
                "assg-course": assignment["class"],
                "assg-user-id": str(student["_id"])
            },
            follow_redirects=True
        )

        # check return code
        assert res.status_code == 403

def test_submitasst_noresubmit(client):
    """Tests Student1 submitting again to Assignment 2"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        student = pytest.db['users'].find_one(
            {"username": "student1"}
        )

        # set session vars
        prelim_session["id"] = str(student["_id"])
        prelim_session['username'] = student['username']
        prelim_session["fname"] = student["firstname"]
        prelim_session["lname"] = student["lastname"]
        prelim_session["role"] = student["role"]

        # get assignment id from db
        assignment = pytest.db['assignments'].find_one(
            {"name": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assignment",
            data = {
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest!",
                "assg-course": assignment["class"],
                "assg-user-id": str(student["_id"])
            },
            follow_redirects=True
        )

        # check to make sure it failed
        assert res.status_code == 400


def test_addasst_good(client):
    """Tests adding an assignment to a class"""
    
    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:
        
        # get teacher data from db
        teacher = pytest.db['users'].find_one(
            {"username": "teacher"}
        )
        
        # set session vars
        prelim_session["id"] = str(teacher["_id"])
        prelim_session['username'] = teacher['username']
        prelim_session["fname"] = teacher["firstname"]
        prelim_session["lname"] = teacher["lastname"]
        prelim_session["role"] = teacher["role"]
        
        # get class id from db
        course = pytest.db['classes'].find_one(
            {"name": "Test Course 2"}
        )
        
    # use client context
    with client:
        
        # try sending in submission
        res = client.post(
            "/secretary/add-assignment",
            data = {
                "assg-name": "Calculus Homework 1",
                "assg-desc": "Page 32 of the textbook, #6-12",
                "course-code": str(course['_id']),
                "due-date": (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
            },
            follow_redirects=True
        )
        
        # check to make sure we were redirected
        # also check to see if new class is rendering
        assert res.status_code == 200
        
        # ensure assignment was made
        assignment = pytest.db['assignments'].find_one(
            {"title": "Calculus Homework 1"}
        )
        assert assignment is not None
    

def test_addasst_noperms(client):
    """Tests adding an assignment to a class"""
    
    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:
        
        # get teacher data from db
        student = pytest.db['users'].find_one(
            {"username": "student1"}
        )
        
        # set session vars
        prelim_session["id"] = str(student["_id"])
        prelim_session['username'] = student['username']
        prelim_session["fname"] = student["firstname"]
        prelim_session["lname"] = student["lastname"]
        prelim_session["role"] = student["role"]
        
        # get class id from db
        course = pytest.db['classes'].find_one(
            {"name": "Test Course 2"}
        )
        
    # use client context
    with client:
        
        # try sending in submission
        res = client.post(
            "/secretary/add-assignment",
            data = {
                "assg-name": "Calculus Homework 2",
                "assg-desc": "Page 64 of the textbook, #18-32",
                "course-code": str(course['_id']),
                "due-date": (datetime.now()+timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
            },
            follow_redirects=True
        )
        
        # check to make sure we were redirected
        # also check to see if new class is rendering
        assert res.status_code == 403
        
        # ensure assignment was made
        assignment = pytest.db['assignments'].find_one(
            {"title": "Calculus Homework 2"}
        )
        assert assignment is None