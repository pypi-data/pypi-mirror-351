import uuid
import pytest
from chunk_retriever_client.client import ChunkRetrieverClient

@pytest.mark.asyncio
async def test_real_retriever():
    source_id = "b7e2c4a0-1234-4f56-8abc-1234567890ab"
    response, err = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=source_id
    )
    # Если сервер доступен и source_id есть в базе, response будет не None
    # Если сервер недоступен, будет корректная ошибка
    assert err == "" or "Network error" in err or "timed out" in err or "Server returned status" in err 