import pytest
from flask import session

from .utils import util_setuser

def test_admin_redirect(client):
    """Ensure that admins get redirected"""

    # set admin user
    util_setuser(client, "admin")

    # with context...
    with client:

        res = client.get("/")

        assert res.status_code == 302
        assert session['username'] == 'admin'

