import pytest
import asyncio
from svo_client.chunker_client import ChunkerClient, ChunkFull, Token, SV
from typing import List
import aiohttp
import sys
import types

@pytest.mark.asyncio
async def test_chunk_text_and_reconstruct(monkeypatch):
    # Мокаем ответ сервера
    fake_chunks = [
        {
            "uuid": "1", "text": "Hello, ", "ordinal": 0, "sha256": "x", "embedding": [1.0],
            "tokens": [{"text": "Hello"}], "block": [{"text": "Hello"}], "sv": {"subject": {"text": "Hello"}, "verb": {"text": "is"}}
        },
        {
            "uuid": "2", "text": "world!", "ordinal": 1, "sha256": "y", "embedding": [2.0],
            "tokens": [{"text": "world"}], "block": [{"text": "world"}], "sv": {"subject": {"text": "world"}, "verb": {"text": "exists"}}
        }
    ]
    class FakeResponse:
        def __init__(self, data): self._data = data
        async def json(self): return {"result": {"chunks": self._data}}
        def raise_for_status(self): pass
    class FakeSession:
        def __init__(self): self.last_url = None; self.last_json = None
        def post(self, url, json):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse(fake_chunks)
                async def __aexit__(self_, exc_type, exc, tb): pass
            self.last_url = url; self.last_json = json
            return _Ctx()
        def get(self, url):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse({"openapi": "3.0.2"})
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    # chunk_text
    chunks = await client.chunk_text("Hello, world!")
    assert isinstance(chunks, list)
    assert all(isinstance(c, ChunkFull) for c in chunks)
    assert chunks[0].text == "Hello, "
    assert chunks[1].text == "world!"
    # reconstruct_text
    text = client.reconstruct_text(chunks)
    assert text == "Hello, world!"
    # Проверка вложенных структур
    assert isinstance(chunks[0].tokens[0], Token)
    assert isinstance(chunks[0].sv, SV)
    assert chunks[0].sv.subject.text == "Hello"
    assert chunks[1].sv.verb.text == "exists"

@pytest.mark.asyncio
async def test_get_openapi_schema(monkeypatch):
    class FakeResponse:
        async def json(self): return {"openapi": "3.0.2"}
        def raise_for_status(self): pass
    class FakeSession:
        def get(self, url):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    schema = await client.get_openapi_schema()
    assert schema["openapi"] == "3.0.2"

@pytest.mark.asyncio
async def test_get_help(monkeypatch):
    class FakeResponse:
        async def json(self): return {"result": {"commands": {"chunk": {}}}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    help_info = await client.get_help()
    assert "commands" in help_info["result"]

@pytest.mark.asyncio
async def test_health(monkeypatch):
    class FakeResponse:
        async def json(self): return {"result": {"success": True}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    health = await client.health()
    assert health["result"]["success"] is True

# Интеграционный тест (если сервер доступен)
@pytest.mark.asyncio
async def test_chunk_text_integration():
    try:
        async with ChunkerClient() as client:
            chunks = await client.chunk_text("Integration test.")
            assert isinstance(chunks, list)
            assert all(isinstance(c, ChunkFull) for c in chunks)
            if chunks:
                assert hasattr(chunks[0], "text")
    except aiohttp.ClientConnectorError:
        pytest.skip("Chunker server not available for integration test.") 