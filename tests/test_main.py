
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


def test_db(client):
    response = client.get('/test_db')
    assert response.status_code == 200

