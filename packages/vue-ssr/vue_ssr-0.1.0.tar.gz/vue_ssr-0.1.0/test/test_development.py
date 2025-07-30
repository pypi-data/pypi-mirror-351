import pytest


def test_server_offline(client, development):
    with pytest.raises(Exception) as exc_info:
        client.get("/")
    assert "Could not connect to Vue SSR service. Is it running?" in str(exc_info)


def test_server_running(client, development, vite_dev_server):
    r = client.get("/")
    assert "forceClientRender" not in str(r.content)
    assert "You are not logged in." in str(r.content)
