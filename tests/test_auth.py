import pytest
from flask import session


def test_login_good(client):
    """Tests a login using good credentials"""

    # use client context to keep session static after request is processed
    with client:

        # try logging in with user credentials
        res = client.post(
            "/auth/login",
            data={"username": "teacher", "password": "pass"},
            follow_redirects=True,
        )

        # check to make sure we were redirected
        assert res.status_code == 200
        assert res.request.path == "/"

        # check session state
        assert session["username"] == "teacher"
        assert session["fname"] == "Teacher"
        assert session["lname"] == "User"
        assert session["role"] == 3


def test_login_baduser(client):
    """Tests a login using bad username"""

    # use client context to keep session static after request is processed
    with client:

        # try logging in with user credentials
        res = client.post(
            "/auth/login",
            data={"username": "user_no_exist", "password": "pass"},
            follow_redirects=True,
        )

        # asserts, session should still be available
        assert res.status_code == 200
        assert res.request.path == "/auth/login"
        assert "Invalid username or password" in res.get_data(as_text=True)


def test_logout_good(client):
    """Tests logging out"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # set session
        prelim_session["id"] = "id_placeholder_idk"
        prelim_session["username"] = "teacher"
        prelim_session["fname"] = "Teacher"
        prelim_session["lname"] = "User"
        prelim_session["role"] = 3

    # use client context to keep session static after request is processed
    with client:

        # attempt logout
        res = client.get("/auth/logout", follow_redirects=True)

        # assert we were logged out and redirected to login
        assert res.status_code == 200
        assert res.request.path == "/auth/login"
        assert "You have been logged out." in res.get_data(as_text=True)

        # ensure session was cleared
        assert "id" not in session
        assert "username" not in session
        assert "fname" not in session
        assert "lname" not in session
        assert "role" not in session


def test_logout_nosession(client):
    """Tests logging out w/ no session"""

    # use client context to keep session static after request is processed
    with client:

        # attempt logout
        res = client.get("/auth/logout", follow_redirects=True)

        # assert we were logged out and redirected to login
        assert res.status_code == 200
        assert res.request.path == "/auth/login"


def test_signup_good(client):
    """Tests a successful signup"""

    # use client context
    with client:

        # try signing up
        res = client.post(
            "/auth/signup",
            data={
                "firstname": "student3",
                "lastname": "User",
                "username": "student3",
                "email": "student3@example.com",
                "password": "password",
                "role": 1,
            },
            follow_redirects=True,
        )

        # assert website returns normal
        assert res.status_code == 200
        assert res.request.path == "/auth/login"
        assert "Account created!" in res.get_data(as_text=True)

        # assert database is actually updated
        newuser = pytest.db["users"].find_one({"username": "student3"})
        assert newuser is not None


def test_signup_badusername(client):
    """Tests a bad signup with bad username"""

    # use client context
    with client:

        # try signing up
        res = client.post(
            "/auth/signup",
            data={
                "firstname": "student4",
                "lastname": "User",
                "username": "teacher",
                "email": "student4@example.com",
                "password": "password",
                "role": 1,
            },
            follow_redirects=True,
        )

        # assert website returns error
        assert res.status_code == 200
        assert res.request.path == "/auth/signup"
        assert "Username already in use!" in res.get_data(as_text=True)

        # assert database hasnt actually been touched
        teacher = pytest.db["users"].find({"username": "teacher"})
        assert len(list(teacher)) == 1


def test_signup_bademail(client):
    """Tests a bad signup with bad email"""

    # use client context
    with client:

        # try signing up
        res = client.post(
            "/auth/signup",
            data={
                "firstname": "student4",
                "lastname": "User",
                "username": "student4",
                "email": "teacher@example.com",
                "password": "password",
                "role": 1,
            },
            follow_redirects=True,
        )

        # assert website returns error
        assert res.status_code == 200
        assert res.request.path == "/auth/signup"
        assert "Email already in use!" in res.get_data(as_text=True)

        # assert database hasnt actually been touched
        teacher = pytest.db["users"].find({"email": "teacher@example.com"})
        assert len(list(teacher)) == 1
