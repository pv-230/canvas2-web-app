from flask import session

def test_good_login(client):
    """Tests a login using good credentials"""

    # use client context to keep session static after request is processed
    with client:
        
        # try logging in with user credentials
        res = client.post(
            "/auth/login",
            data = {
                "username": "teacher",
                "password": "pass"
            },
            follow_redirects=True
        )

        # asserts, session should still be available
        assert res.status_code == 200
        assert res.request.path == "/"
        assert session['username'] == 'teacher'
        assert session["fname"] == "Teacher"
        assert session["lname"] == "User"
        assert session["role"] == 3


def test_bad_login(client):
    """Tests a login using bad credentials"""

    # use client context to keep session static after request is processed
    with client:
        
        # try logging in with user credentials
        res = client.post(
            "/auth/login",
            data = {
                "username": "user_no_exist",
                "password": "pass"
            },
            follow_redirects=True
        )

        # asserts, session should still be available
        assert res.status_code == 200
        assert res.request.path == "/auth/login"
        assert "Invalid username or password" in res.text


def test_logout(client):
    """Tests logging out"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as session:

        # set session 
        session["id"] = "id_placeholder_idk"
        session['username'] = 'teacher'
        session["fname"] = "Teacher"
        session["lname"] = "User"
        session["role"] = 3

    # use client context to keep session static after request is processed
    with client:

        # attempt logout
        res = client.get(
            "/auth/logout",
            follow_redirects=True
        )

        # assert we were logged out and redirected to login
        assert res.status_code == 200
        assert res.request.path == "/auth/login"
        assert "You have been logged out." in res.text
