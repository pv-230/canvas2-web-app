import pytest
from bson import ObjectId
from datetime import datetime, timedelta

###############################################################################
#  CLASS CREATION TESTS
###############################################################################


def test_addcourse_good(client):
    """Tests adding a course to the database."""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teacher"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # use client context
    with client:

        # try making course
        res = client.post(
            "/secretary/add-course",
            data={
                "course-name": "PyTest Course 1",
                "course-code": "PYT001",
                "course-desc": "This course was made by PyTest! "
                + "(test_addcourse_good)",
            },
            follow_redirects=True,
        )

        # check to make sure we were redirected to new class page
        assert res.status_code == 200
        assert "/c/" in res.request.path

        # assert class was actually created in db
        course = pytest.db["classes"].find_one({"code": "PYT001"})
        assert course is not None

        # assert teacher was added to class
        enrollment = pytest.db["enrollments"].find_one(
            {"class": course["_id"], "user": user["_id"]}
        )
        assert enrollment is not None


def test_addcourse_noauth(client):
    """Tests adding a course to the database while a user is not logged in."""

    # use client context
    with client:

        # try making course
        res = client.post(
            "/secretary/add-course",
            data={
                "course-name": "PyTest Course 2",
                "course-code": "PYT002",
                "course-desc": "This course should never be made by PyTest! "
                + "(test_addcourse_noauth)",
            },
            follow_redirects=True,
        )

        # check to make sure we were unauthorized
        assert res.status_code == 401

        # assert class was not created in db
        course = pytest.db["classes"].find_one({"code": "PYT002"})
        assert course is None


def test_addcourse_noperms(client):
    """Tests adding a course to the database while a user doesnt have perms."""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "student1"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # use client context
    with client:

        # try logging in with user credentials
        res = client.post(
            "/secretary/add-course",
            data={
                "course-name": "PyTest Course 3",
                "course-code": "PYT003",
                "course-desc": "This course should never be made by PyTest! "
                + " (test_addcourse_noperms)",
            },
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # assert class was not created in db
        course = pytest.db["classes"].find_one({"code": "PYT003"})
        assert course is None


###############################################################################
#  ASSIGNMENT CREATION TESTS
###############################################################################


def test_createassg_good(client):
    """Tests adding an assignment to a class"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teacher"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get class id from db
        course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 1",
                "assg-desc": "Page 32 of the textbook, #6-12",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were permitted
        assert res.status_code == 200

        # ensure assignment was made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 1"}
        )
        assert assignment is not None


def test_createassg_noauth(client):
    """Tests adding an assignment to a class without being logged in."""

    # get class id from db
    course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 2",
                "assg-desc": "Page 64 of the textbook, #12-24",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were unauthorized
        assert res.status_code == 401

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 2"}
        )
        assert assignment is None


def test_createassg_nouser(client):
    """Tests adding an assignment using spoofed session data that doesnt
    exist."""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # set session vars
        prelim_session["id"] = "6245d9258519c7e387c9e85f"
        prelim_session["username"] = "bogus_user"
        prelim_session["fname"] = "spoofed"
        prelim_session["lname"] = "user"
        prelim_session["role"] = 9

        # get class id from db
        course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 3",
                "assg-desc": "Page 128 of the textbook, #24-48",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 3"}
        )
        assert assignment is None


def test_createassg_noperms(client):
    """Tests adding an assignment using student data, which shouldn't be
    allowed."""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get user data from db
        user = pytest.db["users"].find_one({"username": "student1"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get class id from db
        course = pytest.db["classes"].find_one({"title": "Test Course 2"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 4",
                "assg-desc": "Page 256 of the textbook, #48-96",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 4"}
        )
        assert assignment is None


def test_createassg_noenroll(client):
    """Tests adding an assignment to a class we're not allowed to
    administer."""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get user data from db
        user = pytest.db["users"].find_one({"username": "teacher"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get class id from db
        course = pytest.db["classes"].find_one({"title": "Hidden Course"})

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/create-assg",
            data={
                "assg-name": "Calculus Homework 5",
                "assg-desc": "Page 512 of the textbook, #96-192",
                "course-code": str(course["_id"]),
                "due-date": (datetime.now() + timedelta(days=1)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
            headers={"Referer": "/c/" + str(course["_id"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure assignment was not made
        assignment = pytest.db["assignments"].find_one(
            {"title": "Calculus Homework 5"}
        )
        assert assignment is None


###############################################################################
#  ASSIGNMENT SUBMISSION TESTS
###############################################################################


def test_submitassg_good(client):
    """Tests Student1 submitting to Assignment 2"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "student1"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_good)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were allowed
        assert res.status_code == 200
        assert res.request.path == f"/c/{assignment['class']}"

        # ensure submission was made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is not None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )


def test_submitassg_noauth(client):
    """Tests Student1 submitting with no auth"""

    # get student 1 id
    student1_id = pytest.db["users"].find_one({"username": "student1"})["_id"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noauth)",
                "assg-course": assignment["class"],
                "assg-user-id": str(student1_id),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were unauthorized
        assert res.status_code == 401

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )


def test_submitassg_nouser(client):
    """Tests submitting with spoofed user data"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # set session vars
        prelim_session["id"] = "6245d9258519c7e387c9e85f"
        prelim_session["username"] = "bogus_user"
        prelim_session["fname"] = "spoofed"
        prelim_session["lname"] = "user"
        prelim_session["role"] = 9

        # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_nouser)",
                "assg-course": assignment["class"],
                "assg-user-id": "6245d9258519c7e387c9e85f",
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were given bad request
        assert res.status_code == 400

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {
                "assignment": assignment["_id"],
                "user": ObjectId("6245d9258519c7e387c9e85f"),
            }
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {
                "assignment": assignment["_id"],
                "user": ObjectId("6245d9258519c7e387c9e85f"),
            }
        )


def test_submitassg_noperms(client):
    """Tests teacher submitting to Assignment 2"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "teacher"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noperms)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )


def test_submitassg_noforgery(client):
    """Tests Student2 submitting to Assignment 2 on Student1's behalf"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "student2"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get student 1 id
        student1_id = pytest.db["users"].find_one({"username": "student1"})[
            "_id"
        ]

        # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_nocsrf)",
                "assg-course": assignment["class"],
                "assg-user-id": str(student1_id),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were forbidden
        assert res.status_code == 403

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": student1_id}
        )


def test_submitassg_noassg(client):
    """Tests Student1 submitting to a bogus assignment"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "student1"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": ObjectId("6245d9258519c7e387c9e85f"),
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noassg)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were denied
        assert res.status_code == 400

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )


def test_submitassg_noenroll(client):
    """Tests Student2 submitting to a class they're not enrolled in"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "student2"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 2"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noenroll)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were denied
        assert res.status_code == 403

        # ensure submission was not made
        submission = pytest.db["submissions"].find_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert submission is None

        # clean up
        pytest.db["submissions"].delete_one(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )


def test_submitassg_noresubmit(client):
    """Tests Student2 submitting to a class they're not enrolled in"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "student1"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

        # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 1"}
        )

    # use client context
    with client:

        # try sending in submission
        res = client.post(
            "/secretary/submit-assg",
            data={
                "assg-id": assignment["_id"],
                "assg-entry": "This assignment submission was made by PyTest! \
                    (test_submitassg_noresubmit)",
                "assg-course": assignment["class"],
                "assg-user-id": str(user["_id"]),
            },
            headers={"Referer": "/c/" + str(assignment["class"])},
            follow_redirects=True,
        )

        # check to make sure we were denied
        assert res.status_code == 400

        # ensure submission was not made
        submissions = pytest.db["submissions"].find(
            {"assignment": assignment["_id"], "user": user["_id"]}
        )
        assert len(list(submissions)) == 1


###############################################################################
#  EDIT ASSIGNMENT TESTS
###############################################################################


def test_editassg_good(client):
    """Tests teacher's ability to edit assignment 1"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teacher"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 2"}
    )

    # use client context
    with client:

        newTitle = "Edited Title"
        newDescription = "Edited Description"
        newDate = "2022-04-22T16:59"
        requestPath = f"/c/{assignment['class']}/a/{assignment['_id']}"

        # try sending new assignment details
        res = client.post(
            "/secretary/edit-assg",
            data={
                "assg-name": newTitle,
                "assg-desc": newDescription,
                "due-date": newDate,
                "assg-id": assignment["_id"],
                "course-id": assignment["class"]
            },
            headers={"Referer": requestPath},
            follow_redirects=True,
        )

        # check to make sure we were allowed
        assert res.status_code == 200
        assert res.request.path == requestPath

        # ensure edit was made
        assignment = pytest.db["assignments"].find_one(
            {
                "title": newTitle,
                "description": newDescription,
            }
        )
        assert assignment is not None


def test_editassg_studentedit(client):
    """Tests if students are able to edit assignments"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "student1"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 1"}
        )

    # use client context
    with client:

        # POST data
        newTitle = "Student Edited This Title"
        newDescription = "Student edited this description"
        newDate = "2022-04-22T16:59"

        # try sending new assignment details
        res = client.post(
            "/secretary/edit-assg",
            data={
                "assg-name": newTitle,
                "assg-desc": newDescription,
                "due-date": newDate,
                "assg-id": assignment["_id"],
                "course-id": assignment["class"]
            },
        )

        # Check for error code
        assert res.status_code == 403

        # ensure edit was not made
        assignment = pytest.db["assignments"].find_one(
            {
                "title": newTitle,
                "description": newDescription,
            }
        )
        assert assignment is None


def test_editassg_taedit(client):
    """Tests if TA's are able to edit assignments"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get ta data from db
        user = pytest.db["users"].find_one({"username": "teachasst"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 1"}
        )

    # use client context
    with client:

        # POST data
        newTitle = "TA Edited This Title"
        newDescription = "TA edited this description"
        newDate = "2022-04-22T16:59"

        # try sending new assignment details
        res = client.post(
            "/secretary/edit-assg",
            data={
                "assg-name": newTitle,
                "assg-desc": newDescription,
                "due-date": newDate,
                "assg-id": assignment["_id"],
                "course-id": assignment["class"]
            },
        )

        # Check for error code
        assert res.status_code == 403

        # ensure edit was not made
        assignment = pytest.db["assignments"].find_one(
            {
                "title": newTitle,
                "description": newDescription,
            }
        )
        assert assignment is None


def test_editassg_wrongteacher(client):
    """Tests if the wrong teacher is able to edit assignments"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teacher2"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
        assignment = pytest.db["assignments"].find_one(
            {"title": "Test Assignment 1"}
        )

    # use client context
    with client:

        # POST data
        newTitle = "The Wrong Teacher Edited This Title"
        newDescription = "The wrong teacher edited this description"
        newDate = "2022-04-22T16:59"

        # try sending new assignment details
        res = client.post(
            "/secretary/edit-assg",
            data={
                "assg-name": newTitle,
                "assg-desc": newDescription,
                "due-date": newDate,
                "assg-id": assignment["_id"],
                "course-id": assignment["class"]
            },
        )

        # Check for error code
        assert res.status_code == 403

        # ensure edit was not made
        assignment = pytest.db["assignments"].find_one(
            {
                "title": newTitle,
                "description": newDescription,
            }
        )
        assert assignment is None


###############################################################################
#  MANAGE SUBMISSION TESTS
###############################################################################


def test_managesub_teacher(client):
    """Tests teacher's ability to grade and comment on submissions"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teacher"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 1"}
    )

    submission = pytest.db["submissions"].find_one(
        {"contents": "This is the test submission!"}
    )

    # use client context
    with client:

        newGrade = "90.05"
        newComment = "This is a new comment by a teacher."
        requestPath = f"/c/{assignment['class']}/a/{assignment['_id']}"

        # try sending new grade and comment
        res = client.post(
            f"/secretary/s/{submission['_id']}/submission-info",
            data={
                "comment": newComment,
                "grade": newGrade,
            },
            headers={"Referer": requestPath},
            follow_redirects=True,
        )

        # Check for error code
        assert res.status_code == 200
        assert res.request.path == requestPath

        # Ensure submission was updated
        submission = pytest.db["submissions"].find_one(
            {
                "_id": ObjectId(submission["_id"]),
                "grade": float(newGrade),
                "comments": {
                    "$exists": newComment
                },
            }
        )
        assert submission is not None


def test_managesub_ta(client):
    """Tests TA's ability to grade and comment on submissions"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teachasst"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 1"}
    )

    submission = pytest.db["submissions"].find_one(
        {"contents": "This is the test submission!"}
    )

    # use client context
    with client:

        newGrade = "80.5"
        newComment = "This is a new comment by a TA."
        requestPath = f"/c/{assignment['class']}/a/{assignment['_id']}"

        # try sending new grade and comment
        res = client.post(
            f"/secretary/s/{submission['_id']}/submission-info",
            data={
                "comment": newComment,
                "grade": newGrade,
            },
            headers={"Referer": requestPath},
            follow_redirects=True,
        )

        # Check for error code
        assert res.status_code == 200
        assert res.request.path == requestPath

        # Ensure submission was updated
        submission = pytest.db["submissions"].find_one(
            {
                "_id": ObjectId(submission["_id"]),
                "grade": float(newGrade),
                "comments": {
                    "$exists": newComment
                }
            }
        )
        assert submission is not None


def test_managesub_student(client):
    """Tests if students are able to manage submissions"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get student data from db
        user = pytest.db["users"].find_one({"username": "student1"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # Get submission from db
    submission = pytest.db["submissions"].find_one(
        {"contents": "This is the test submission!"}
    )

    # use client context
    with client:

        newGrade = "100"
        newComment = "This is a new comment made by a student."

        # try sending new grade and comment
        res = client.post(
            f"/secretary/s/{submission['_id']}/submission-info",
            data={
                "comment": newComment,
                "grade": newGrade,
            }
        )

        # Check for error code
        assert res.status_code != 200

        # Ensure submission was not updated
        submission = pytest.db["submissions"].find_one(
            {
                "_id": ObjectId(submission["_id"]),
                "grade": float(newGrade),
                "comments": {
                    "$exists": newComment
                }
            }
        )
        assert submission is None


def test_managesub_tablegrade_teacher(client):
    """Tests teacher's ability to update grades with the submission table"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teacher"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 1"}
    )

    submission = pytest.db["submissions"].find_one(
        {"contents": "This is the test submission!"}
    )

    # use client context
    with client:

        newGrade = "100"
        requestPath = f"/c/{assignment['class']}/a/{assignment['_id']}"
        jsonMock = {
            str(submission["_id"]): newGrade
        }

        # try sending new grades
        res = client.post(
            "/secretary/update-grades",
            json=jsonMock,
            headers={"Referer": requestPath},
            follow_redirects=True,
        )

        # Check for error code
        assert res.status_code == 200
        assert res.request.path == requestPath

        # Ensure submission was updated
        submission = pytest.db["submissions"].find_one(
            {
                "_id": ObjectId(submission["_id"]),
                "grade": float(newGrade),
            }
        )
        assert submission is not None


def test_managesub_tablegrade_ta(client):
    """Tests TA's ability to update grades with the submission table"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get ta data from db
        user = pytest.db["users"].find_one({"username": "teachasst"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 1"}
    )

    submission = pytest.db["submissions"].find_one(
        {"contents": "This is the test submission!"}
    )

    # use client context
    with client:

        newGrade = "99"
        requestPath = f"/c/{assignment['class']}/a/{assignment['_id']}"
        jsonMock = {
            str(submission["_id"]): newGrade
        }

        # try sending new grades
        res = client.post(
            "/secretary/update-grades",
            json=jsonMock,
            headers={"Referer": requestPath},
            follow_redirects=True,
        )

        # Check for error code
        assert res.status_code == 200
        assert res.request.path == requestPath

        # Ensure submission was updated
        submission = pytest.db["submissions"].find_one(
            {
                "_id": ObjectId(submission["_id"]),
                "grade": float(newGrade),
            }
        )
        assert submission is not None


def test_managesub_tablegrade_wrongteacher(client):
    """Tests if the wrong teacher is able to change grades"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": "teacher2"})

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    submission = pytest.db["submissions"].find_one(
        {"contents": "This is the test submission!"}
    )

    # use client context
    with client:

        newGrade = "1"
        jsonMock = {
            str(submission["_id"]): newGrade
        }

        # try sending new grades
        res = client.post(
            "/secretary/update-grades",
            json=jsonMock,
        )

        # Check for error code
        assert res.status_code == 403

        # Ensure submission was updated
        submission = pytest.db["submissions"].find_one(
            {
                "_id": ObjectId(submission["_id"]),
                "grade": float(newGrade),
            }
        )
        assert submission is None
