"""Integration tests for API patterns."""

from src.utils.response_builder import error, success


class TestApiEnvelope:
    def test_success_envelope(self):
        result = success({"reports": []})
        assert result["body"]["success"] is True
        assert result["body"]["data"] == {"reports": []}
        assert result["body"]["error"] is None

    def test_error_envelope(self):
        result = error("Not found", 404)
        assert result["body"]["success"] is False
        assert result["body"]["data"] is None
        assert result["body"]["error"]["message"] == "Not found"

    def test_cors_headers_present(self):
        result = success({})
        assert "Access-Control-Allow-Origin" in result["headers"]
        assert result["headers"]["Access-Control-Allow-Origin"] == "*"

    def test_status_codes(self):
        assert success({}, 201)["statusCode"] == 201
        assert error("bad", 400)["statusCode"] == 400
        assert error("unauth", 401)["statusCode"] == 401
        assert error("forbid", 403)["statusCode"] == 403
        assert error("not found", 404)["statusCode"] == 404
        assert error("conflict", 409)["statusCode"] == 409
        assert error("oops")["statusCode"] == 500
