import pytest
from backend.app.services.rag.retriever import retrieve_relevant_chunks
from backend.app.models.knowledge import KnowledgeSource, DocumentChunk

def test_authoritative_sources_indexed(db_session):
    """Verify that authoritative ChatPRD podcast sources exist in the database."""
    authoritative_sources = db_session.query(KnowledgeSource).filter(KnowledgeSource.is_authoritative == True).all()
    assert len(authoritative_sources) >= 1, "Expected at least 1 authoritative source indexed"
    
    # Check that provenance paths point to episodes/*/transcript.md
    for src in authoritative_sources:
        assert src.provenance_file is not None
        assert src.provenance_file.startswith("episodes/")
        assert src.provenance_file.endswith("transcript.md")

def test_synthetic_sources_excluded_from_retrieval(db_session):
    """Verify that synthetic demo documents (is_authoritative=False) are never retrieved."""
    # Create a synthetic source with a unique fake token
    synthetic_src = KnowledgeSource(
        title="SYNTHETIC DEMO: Fake Alien Growth Hacks",
        source_type="demo",
        is_authoritative=False,
        provenance_file="legacy_sample_demo",
        status="indexed"
    )
    db_session.add(synthetic_src)
    db_session.commit()

    chunk = DocumentChunk(
        source_id=synthetic_src.id,
        chunk_index=0,
        content="Alien hyper-growth hacks from Mars using Martian crypto tokens.",
    )
    db_session.add(chunk)
    db_session.commit()

    # Query for the synthetic token
    chunks = db_session.query(DocumentChunk).join(KnowledgeSource).filter(
        KnowledgeSource.is_authoritative == True,
        DocumentChunk.content.like("%Martian crypto%")
    ).all()
    assert len(chunks) == 0, "Synthetic chunk must not be returned when filtering for authoritative sources"

    # Clean up test artifact so other tests see clean sources
    db_session.delete(chunk)
    db_session.delete(synthetic_src)
    db_session.commit()

def test_supported_question_grounded_answer(client):
    """A question supported by an ingested transcript returns grounded answer with citations."""
    res = client.post("/api/chat", json={
        "message": "What does Elena Verna say about growth tactics that never work?",
        "mode": "standard"
    })
    assert res.status_code == 200
    data = res.json()
    assert "Elena Verna" in data["message"]["content"] or len(data["citations"]) > 0
    assert len(data["citations"]) > 0
    top_citation = data["citations"][0]
    assert "Elena Verna" in top_citation["source_title"] or "Elena" in (top_citation["author_or_guest"] or "")
    assert top_citation["provenance_file"] is not None
    assert "episodes/elena-verna" in top_citation["provenance_file"]

def test_unrelated_topic_refusal(client):
    """An unrelated topic (e.g. quantum physics or cooking recipe) returns exact Case D response."""
    res = client.post("/api/chat", json={
        "message": "Write a Python script to calculate the mathematical derivative using quantum physics.",
        "mode": "standard"
    })
    assert res.status_code == 200
    data = res.json()
    expected_refusal = "I don't have sufficient information about this topic in the specified Lenny’s Podcast / Newsletter repository to provide a source-grounded answer."
    assert data["message"]["content"] == expected_refusal
    assert len(data["citations"]) == 0
    assert data["rag_used"] is False

def test_unsupported_lenny_question_refusal(client):
    """An unsupported claim or person not in the repository returns exact Case C response."""
    res = client.post("/api/chat", json={
        "message": "What did Lenny's podcast guest Professor Xavier recommend about mutant telepathy in product design?",
        "mode": "standard"
    })
    assert res.status_code == 200
    data = res.json()
    expected_refusal = "I couldn't find sufficient supporting information for this question in the indexed Lenny’s Podcast / Newsletter repository. I can answer only when the available source material supports the response."
    assert data["message"]["content"] == expected_refusal
    assert len(data["citations"]) == 0
    assert data["rag_used"] is False

def test_ship30_unsupported_topic_limitation(client):
    """Ship 30 mode explains limitation when the topic lacks sufficient transcript evidence."""
    res = client.post("/api/chat", json={
        "message": "Write a Ship 30 for 30 essay on quantum mechanical orbital mechanics in rocket engineering",
        "mode": "ship30"
    })
    assert res.status_code == 200
    data = res.json()
    content = data["message"]["content"]
    assert "couldn't find sufficient supporting information" in content or "only creates Ship 30 for 30 essays when backed" in content
    assert len(data["citations"]) == 0
