import pytest
from backend.app.services.rag.retriever import retrieve_relevant_chunks

def test_knowledge_sources_list(client):
    res = client.get("/api/knowledge/sources")
    assert res.status_code == 200
    sources = res.json()
    assert len(sources) >= 4
    first = sources[0]
    assert "title" in first
    assert "source_type" in first
    assert "chunk_count" in first
    assert first["chunk_count"] > 0

@pytest.mark.asyncio
async def test_retrieval_and_citations(db_session):
    # Search for a concept present in our knowledge base: retention
    chunks, citations, has_evidence = await retrieve_relevant_chunks(
        query="What is the fundamental law of retention and Elena Verna's view?",
        db=db_session,
        top_k=3,
    )
    assert len(chunks) > 0
    assert len(citations) > 0
    assert has_evidence is True
    # Verify citation attributes
    top_citation = citations[0]
    assert top_citation.source_title != ""
    assert top_citation.snippet != ""
    assert "retention" in top_citation.snippet.lower() or "retention" in top_citation.source_title.lower()

@pytest.mark.asyncio
async def test_retrieval_insufficient_evidence(db_session):
    # Query completely outside the domain of product growth
    chunks, citations, has_evidence = await retrieve_relevant_chunks(
        query="Quantum gravity string theory spacetime perturbation tensor in black hole astrophysics",
        db=db_session,
        top_k=3,
        min_confidence_score=0.25,
    )
    # The retriever should correctly identify that evidence is insufficient
    assert has_evidence is False
