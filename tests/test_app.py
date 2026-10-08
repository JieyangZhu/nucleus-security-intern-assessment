import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_index_renders_calculator(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Calculator" in response.data
    assert b'data-action="equals"' in response.data


def test_calculation_endpoint(client):
    response = client.post(
        "/api/calculate",
        json={"left": "0.1", "operator": "+", "right": "0.2"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"result": "0.3"}


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        ({"left": "5", "operator": "/", "right": "0"}, "cannot divide by zero"),
        ({"left": "5", "operator": "^", "right": "2"}, "operator must be one of +, -, *, /"),
        ({"left": "5", "operator": "+"}, "request must contain exactly left, operator, and right"),
        ({"left": "5", "operator": "+", "right": "2", "extra": True}, "request must contain exactly left, operator, and right"),
        (["5", "+", "2"], "request body must be a JSON object"),
    ],
)
def test_calculation_endpoint_rejects_bad_requests(client, payload, expected_error):
    response = client.post("/api/calculate", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": expected_error}


def test_endpoint_requires_json(client):
    response = client.post("/api/calculate", data="left=1&right=2")

    assert response.status_code == 415
    assert response.get_json() == {"error": "request must use application/json"}


def test_endpoint_rejects_malformed_json(client):
    response = client.post(
        "/api/calculate",
        data='{"left":',
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "request body contains invalid JSON"}


def test_endpoint_limits_request_size(client):
    response = client.post(
        "/api/calculate",
        data="{" + '"padding":"' + ("x" * 9000) + '"}',
        content_type="application/json",
    )

    assert response.status_code == 413
    assert response.get_json() == {"error": "request body is too large"}

