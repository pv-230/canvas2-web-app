import pytest
from bson import ObjectId

from .utils import setuser

###############################################################################
#  EDIT ASSIGNMENT TESTS
###############################################################################


def test_editassg_good(client):
    """Tests teacher's ability to edit assignment 1"""

    # set teacher
    setuser(client, "teacher")

    # get assignment id from db
    assignment = pytest.db["assignments"].find_one(
        {"title": "Test Assignment 3"}
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

    # set student1
    setuser(client, "student1")

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

    # set TA
    setuser(client, "teachasst")

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

    # set teacher2
    setuser(client, "teacher2")

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

    # set teacher
    setuser(client, "teacher")

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

    # set TA
    setuser(client, "teachasst")

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

    # set student
    setuser(client, "student1")

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

    # set teacher
    setuser(client, "teacher")

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

    # set TA
    setuser(client, "teachasst")

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

    # set teacher 2
    setuser(client, "teacher2")

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
