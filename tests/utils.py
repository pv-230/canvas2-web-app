import pytest

def util_setuser(client, username):
    """Utility function"""

    # use session_transaction to set prelim session state
    with client.session_transaction() as prelim_session:

        # get teacher data from db
        user = pytest.db["users"].find_one({"username": username})

        # ensure we have data
        if not user:
            raise Exception("util_admin_setuser: Bad username")

        # set session vars
        prelim_session["id"] = str(user["_id"])
        prelim_session["username"] = user["username"]
        prelim_session["fname"] = user["firstname"]
        prelim_session["lname"] = user["lastname"]
        prelim_session["role"] = user["role"]

    # return user, in case its used in tests
    return user