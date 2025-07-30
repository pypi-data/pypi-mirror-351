from vue_ssr.services import setup_renderer


def test_server_offline(client, production, settings):
    r = client.get("/")
    assert "forceClientRender" in str(r.content)
    assert "You are not logged in." not in str(r.content)


def test_server_running(client, vue_ssr_server, production):
    r = client.get("/")

    assert "forceClientRender" not in str(r.content)
    assert "You are not logged in." in str(r.content)


def test_socket_server_running(client, settings, vue_ssr_socket_server, production):
    _server, socket = vue_ssr_socket_server
    settings.VUE_SSR = {"socket": socket}
    setup_renderer()

    r = client.get("/")

    assert "forceClientRender" not in str(r.content)
    assert "You are not logged in." in str(r.content)
