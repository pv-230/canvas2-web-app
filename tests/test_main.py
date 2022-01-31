def test_main(client):
    res = client.get("/")
    assert res.data == b"<p>Hello, World!</p>"
