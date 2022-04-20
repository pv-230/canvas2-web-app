import pytest
from datetime import datetime, timedelta

# this file will only have one test that goes over many parts of the invite
# process. i would split these into multiple tests but they're so intertwined
# that its really not worth it tbh


def test_invite_creation(client):

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

        # get class 1 data from db
        class1 = pytest.db["classes"].find_one({"code": "TEST001"})

        # make sure no invites already exist for class 1
        pytest.db["invites"].delete_many(
            {"class": class1["_id"]}
        )

    # with client context
    with client:

        # simulate clicking on create invite button from class page
        # todo: csrf prevention here
        res = client.post(
            f"/c/{class1['_id']}/invite",
            follow_redirects=True,
            headers={"Referer": "/c/" + str(class1["_id"])},
        )

        # check that we get a 200
        assert res.status_code == 200

        # check that we now have an invite in db
        invite = pytest.db["invites"].find_one({"class": class1["_id"]})
        assert invite is not None

        # assert that the redirect contains the link
        assert f"{invite['code']}" in res.get_data(as_text=True)

    # clean up
    pytest.db["invites"].delete_many(
        {"class": class1["_id"]}
    )


def test_invite_consent_good(client):
    """Tests using an invite, good transaction"""

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

        # go ahead and inject a class2 invite
        class2 = pytest.db["classes"].find_one({"code": "TEST002"})
        pytest.db["invites"].insert_one({
            "class": class2['_id'],
            "code": "AJMrfOM1p4CGBdidr2oLjw",
            "expires": datetime.now() + timedelta(days=7),
        })

    # with client context
    with client:

        # simulate student1 navigating to the invite page
        res = client.get("/j/AJMrfOM1p4CGBdidr2oLjw")

        # check that we get a 200
        assert res.status_code == 200

        # make sure we weren't redicrected to auth
        assert "/j/AJMrfOM1p4CGBdidr2oLjw" in res.request.path

    # we're done now, delete the invite
    pytest.db["invites"].delete_many(
        {"code": "AJMrfOM1p4CGBdidr2oLjw"}
    )


def test_invite_consent_noauth(client):
    """Tests using an invite while not logged in"""

    # use session_transaction to set prelim session state
    with client.session_transaction():

        # go ahead and inject a class2 invite
        class2 = pytest.db["classes"].find_one({"code": "TEST002"})
        pytest.db["invites"].insert_one({
            "class": class2['_id'],
            "code": "AJMrfOM1p4CGBdidr2oLjw",
            "expires": datetime.now() + timedelta(days=7),
        })

    # with client context
    with client:

        # simulate noauth navigating to the invite page
        res = client.get(
            "/j/AJMrfOM1p4CGBdidr2oLjw",
            follow_redirects=True,
        )

        # check that we get a 200
        assert res.status_code == 200

        # make sure we were redicrected to auth
        assert "/auth/login" in res.request.path
        assert "You must be logged in to perform this action!" \
            in res.get_data(as_text=True)

    # we're done now, delete the invite
    pytest.db["invites"].delete_many(
        {"code": "AJMrfOM1p4CGBdidr2oLjw"}
    )


def test_invite_consent_noclass(client):
    """Tests using an invite for a nonexistent class"""

    # with client context
    with client:

        # simulate noauth navigating to the invite page
        res = client.get(
            "/j/this_invite_does_not_exist",
            follow_redirects=True,
        )

        # check that we get a 404
        assert res.status_code == 404


def test_invite_joinclass_good(client):
    """Tests using an invite to join a class"""

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

        # go ahead and inject a class2 invite
        class2 = pytest.db["classes"].find_one({"code": "TEST002"})
        pytest.db["invites"].insert_one({
            "class": class2['_id'],
            "code": "AJMrfOM1p4CGBdidr2oLjw",
            "expires": datetime.now() + timedelta(days=7),
        })

    # with client context
    with client:

        # simulate student1 navigating to the invite page
        res = client.post(
            "/j/AJMrfOM1p4CGBdidr2oLjw",
            follow_redirects=True,
        )

        # check that we get a 200
        assert res.status_code == 200

        # make sure we were redirected to class page
        assert f"/c/{class2['_id']}" in res.request.path

        # ensure enrollment exists in db
        enrollment = pytest.db["enrollments"].find_one({
            "class": class2["_id"],
            "user": user["_id"]
        })
        assert enrollment is not None

    # we're done now, delete the invite
    pytest.db["invites"].delete_many(
        {"code": "AJMrfOM1p4CGBdidr2oLjw"}
    )


def test_invite_joinclass_noauth(client):
    """Tests using an invite while not logged in"""

    # use session_transaction to set prelim session state
    with client.session_transaction():

        # go ahead and inject a class2 invite
        class2 = pytest.db["classes"].find_one({"code": "TEST002"})
        pytest.db["invites"].insert_one({
            "class": class2['_id'],
            "code": "AJMrfOM1p4CGBdidr2oLjw",
            "expires": datetime.now() + timedelta(days=7),
        })

    # with client context
    with client:

        # simulate noauth navigating to the invite page
        res = client.post(
            "/j/AJMrfOM1p4CGBdidr2oLjw",
            follow_redirects=True,
        )

        # check that we get a 401
        assert res.status_code == 401

    # we're done now, delete the invite
    pytest.db["invites"].delete_many(
        {"code": "AJMrfOM1p4CGBdidr2oLjw"}
    )
