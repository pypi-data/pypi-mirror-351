from __future__ import annotations
from contextlib import AbstractContextManager
from typing import Iterator, Iterable

from ._http import _HTTP
from ._models import CompletionRequest, CompletionResponse, Message


class CompletionEndpoint:
    """
    Thin namespaced helper so people can call
    `client.create.completion(...)` like in the prompt.
    """

    def __init__(self, http: _HTTP):
        self._http = http

    def __call__(
        self,
        *,
        messages: Iterable[dict] | Iterable[Message],
        model: str,
        stream: bool = False,
    ) -> CompletionResponse | Iterator[CompletionResponse]:
        # Allow plain dicts or pydantic Message instances
        msgs = [
            m if isinstance(m, Message) else Message(**m)  # type: ignore[arg-type]
            for m in messages
        ]
        payload = CompletionRequest(model=model, messages=msgs, stream=stream).model_dump()

        if stream:
            return self._streaming_post(payload)
        return CompletionResponse.model_validate(self._http.post("/ollama/completion", payload))

    def _streaming_post(
        self, payload: dict
    ) -> Iterator[CompletionResponse]:
        # very simplified Server-Sent Events loop
        with self._http._client.stream("POST", self._http.BASE_URL + "/ollama/completion", json=payload) as r:
            for line in r.iter_lines():
                if line.startswith(b"data: "):
                    yield CompletionResponse.model_validate_json(line[6:])  # strip "data: "


class AstarClient(AbstractContextManager):
    """
    >>> from AstarCloud import AstarClient
    >>> client = AstarClient(api_key="sk-...")
    >>> resp = client.create.completion(
    ...     messages=[{"role": "user", "content": "Hello"}],
    ...     model="llama3.2"
    ... )
    """

    def __init__(self, api_key: str, *, timeout: float = 30.0):
        self._http = _HTTP(api_key, timeout=timeout)
        self.create = CompletionEndpoint(self._http)

    def __exit__(self, exc_type, exc, tb):
        self._http.close()
