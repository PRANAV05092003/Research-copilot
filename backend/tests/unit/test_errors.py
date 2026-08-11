from app.core.errors import AppError


def test_app_error_initialization():
    err = AppError(
        status_code=400,
        title="Bad Request",
        detail="The request is invalid.",
        error_type="https://example.com/probs/bad-request",
        instance="/api/v1/resource/123",
        extra={"invalid_params": [{"name": "age", "reason": "must be positive"}]},
    )

    assert err.status_code == 400
    assert err.title == "Bad Request"
    assert err.detail == "The request is invalid."
    assert err.type == "https://example.com/probs/bad-request"
    assert err.instance == "/api/v1/resource/123"
    assert err.extra == {"invalid_params": [{"name": "age", "reason": "must be positive"}]}
    assert str(err) == "The request is invalid."


def test_app_error_defaults():
    err = AppError(status_code=500, title="Server Error", detail="Something went wrong.")

    assert err.status_code == 500
    assert err.title == "Server Error"
    assert err.detail == "Something went wrong."
    assert err.type == "about:blank"
    assert err.instance is None
    assert err.extra == {}
