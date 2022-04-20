import json
import pytest
from secrets import token_hex
from datetime import datetime
from bson import ObjectId

from .utils import setuser


def util_add_teacher():
    """Add a pending teacher user to the database"""

    return pytest.db["users"].insert_one({
        "username": "approvemepls",
        "password": "$2b$14$asNJZSOhP/vUd9tdnzsd3OclY2vWnusEYDS9tAyJVPb.4F5VUcj2q",
        "firstname": "Approveme",
        "lastname": "User",
        "email": f"{token_hex(16)}@example.com",
        "role": 3,
        "approved": False,
    })


def util_remove_teacher():
    """Remove a pending teacher user from the database"""
    return pytest.db["users"].delete_many(
        {"username": "approvemepls"}
    )


def test_admin_redirect(client):
    """Ensure that admins get redirected"""

    # set admin user
    setuser(client, "admin")

    # with context...
    with client:

        res = client.get(
            "/",
            follow_redirects=True
        )

        assert res.status_code == 200
        assert "/admin/panel" in res.request.path


def test_panel_baduser_access(client):
    """Ensure that non-admins get denied"""

    # set admin user
    setuser(client, "teacher")

    # with context...
    with client:

        res = client.get(
            "/admin/panel",
            follow_redirects=True
        )

        assert res.status_code == 401


def test_panel_approveteacher(client):
    """Sim approving a teacher user"""

    # set admin user
    setuser(client, "admin")

    # add teacher user to db
    tempuser = util_add_teacher()

    # with context...
    with client:

        # send post request to approve user
        res = client.post(
            "/admin/action/approveRequest",
            data={
                "approve-id": tempuser.inserted_id
            },
            follow_redirects=True
        )

        # ensure we got a 200
        assert res.status_code == 200

        # ensure user is now approved
        assert pytest.db["users"].find_one(
            {"_id": tempuser.inserted_id}
        )["approved"] == True

    # remove temp teacher user
    util_remove_teacher()


def test_panel_denyteacher(client):
    """Sim denying a teacher user"""

    # set admin user
    setuser(client, "admin")

    # add teacher user to db
    tempuser = util_add_teacher()

    # with context...
    with client:

        # send post request to approve user
        res = client.post(
            "/admin/action/denyRequest",
            data={
                "deny-id": tempuser.inserted_id
            },
            follow_redirects=True
        )

        # ensure we got a 200
        assert res.status_code == 200

        # ensure user is now deleted
        assert pytest.db["users"].find_one(
            {"_id": tempuser.inserted_id}
        ) is None
    
    # remove temp teacher user
    util_remove_teacher()

def test_panel_updateuser(client):
    """Sim updating a user"""

    # set admin user
    setuser(client, "admin")

    # get teacher2 user from db
    tempuser = pytest.db["users"].find_one(
        {"username": "teacher2"}
    )

    # with context...
    with client:

        # send post request to approve user
        res = client.post(
            "/admin/action/updateUserInfo",
            json=[
                "newlast",
                "newfirst",
                "teacher2",
                "newemail@whooooo.com",
                str(tempuser["_id"])
            ],
            follow_redirects=True
        )

        # ensure we got a 200
        assert res.status_code == 200

        # ensure user is now updated
        newuser = pytest.db["users"].find_one({"username": "teacher2"})
        assert newuser["lastname"] == "newlast"
        assert newuser["firstname"] == "newfirst"
        assert newuser["email"] == "newemail@whooooo.com"


def test_panel_baduser_approveteacher(client):
    """Sim baduser approving a teacher user"""

    # set admin user
    setuser(client, "teacher")

    # add teacher user to db
    tempuser = util_add_teacher()

    # with context...
    with client:

        # send post request to approve user
        res = client.post(
            "/admin/action/approveRequest",
            data={
                "approve-id": tempuser.inserted_id
            },
            follow_redirects=True
        )

        # ensure we got an error
        assert res.status_code == 401
    
    # remove temp teacher user
    util_remove_teacher()


def test_panel_removecourse(client):
    """Sim removing a course"""

    # set admin user
    setuser(client, "admin")

    # insert course
    course_id = pytest.db["classes"].insert_one({
        "code": "TEST404",
        "title": "Delete Me!",
        "desc": "I should not exist!",
    }).inserted_id
    assg_id = pytest.db["assignments"].insert_one({
        "class": ObjectId(course_id),
        "title": "Delete me too!",
        "description": "This is the deleted assignment!",
        "deadline": datetime.now(),
    }).inserted_id

    # with context...
    with client:

        # send post request to remove course
        res = client.post(
            "/admin/action/removeCourse",
            json=str(course_id),
            follow_redirects=True
        )

        # ensure we got a 200
        assert res.status_code == 200

        # ensure course is now deleted
        assert pytest.db["courses"].find_one(
            {"_id": course_id}
        ) is None
        assert pytest.db["assignments"].find_one(
            {"_id": assg_id}
        ) is None


def test_panel_search(client):
    """Sim searching for a user"""

    # set admin user
    setuser(client, "admin")

    # with context...
    with client:

        # send post request to search
        res = client.post(
            "/admin/search-users",
            json="teacher",
            follow_redirects=True
        )

        # ensure we got a 200
        assert res.status_code == 200
        results = json.loads(res.get_data(as_text=True))
        assert len(results) == 2