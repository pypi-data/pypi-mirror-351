import pytest
from AstarCloud import AstarClient
from AstarCloud._exceptions import AuthenticationError


def test_auth_failure(requests_mock):
    requests_mock.post(
        "https://api.astarcloud.ai/v1/chat/completions",
        status_code=401,
        json={"error": "Invalid key"},
    )
    client = AstarClient(api_key="bad")
    with pytest.raises(AuthenticationError):
        client.create.completion(messages=[], model="llama3.2")
