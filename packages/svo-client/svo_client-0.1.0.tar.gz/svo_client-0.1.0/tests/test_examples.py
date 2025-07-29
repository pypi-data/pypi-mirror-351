import pytest
import asyncio
from svo_client.chunker_client import ChunkerClient, ChunkFull
import sys
import types

@pytest.mark.asyncio
async def test_example_usage(monkeypatch):
    # Мокаем методы клиента
    async def fake_chunk_text(self, text, **params):
        return [ChunkFull(uuid="1", text="Hello, ", sha256="x", ordinal=0), ChunkFull(uuid="2", text="world!", sha256="y", ordinal=1)]
    async def fake_health(self):
        return {"status": "ok"}
    async def fake_get_help(self, cmdname=None):
        return {"help": "info"}
    # Подмена методов
    monkeypatch.setattr(ChunkerClient, "chunk_text", fake_chunk_text)
    monkeypatch.setattr(ChunkerClient, "health", fake_health)
    monkeypatch.setattr(ChunkerClient, "get_help", fake_get_help)

    async with ChunkerClient() as client:
        chunks = await client.chunk_text("test")
        assert isinstance(chunks, list)
        assert all(isinstance(c, ChunkFull) for c in chunks)
        text = client.reconstruct_text(chunks)
        assert text == "Hello, world!"
        health = await client.health()
        assert health["status"] == "ok"
        help_info = await client.get_help()
        assert help_info["help"] == "info" 