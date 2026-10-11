import React, { useState, useEffect } from 'react';
import { Database, X, RefreshCw, Plus, ExternalLink, CheckCircle } from 'lucide-react';
import type { KnowledgeSource } from '../types';
import { fetchKnowledgeSources, ingestDocument, refreshKnowledge } from '../services/api';

interface KnowledgeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSourcesUpdated: () => void;
}

export const KnowledgeModal: React.FC<KnowledgeModalProps> = ({
  isOpen,
  onClose,
  onSourcesUpdated,
}) => {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'list' | 'ingest'>('list');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [newTitle, setNewTitle] = useState('');
  const [newAuthor, setNewAuthor] = useState('');
  const [newType, setNewType] = useState('podcast_transcript');
  const [newUrl, setNewUrl] = useState('');
  const [newContent, setNewContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSources();
    }
  }, [isOpen]);

  const loadSources = async () => {
    setLoading(true);
    try {
      const data = await fetchKnowledgeSources();
      setSources(data);
    } catch (e) {
      console.error('Failed to load knowledge sources', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await refreshKnowledge();
      await loadSources();
      onSourcesUpdated();
      setSuccessMessage('Knowledge base counts successfully refreshed!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;
    setIsSubmitting(true);
    try {
      await ingestDocument({
        title: newTitle.trim(),
        content: newContent.trim(),
        author_or_guest: newAuthor.trim() || undefined,
        source_type: newType,
        url: newUrl.trim() || undefined,
      });
      setNewTitle('');
      setNewAuthor('');
      setNewUrl('');
      setNewContent('');
      setActiveTab('list');
      await loadSources();
      onSourcesUpdated();
      setSuccessMessage('Document successfully indexed into the knowledge base!');
      setTimeout(() => setSuccessMessage(null), 3500);
    } catch (e: any) {
      alert(`Ingestion failed: ${e.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" style={{ maxWidth: 680 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                background: 'var(--accent-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
              }}
            >
              <Database size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Lenny Growth Knowledge Base</h3>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                Indexed sources, transcripts, and retrieval documents
              </p>
            </div>
          </div>
          <button className="icon-btn-subtle" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-subtle)', padding: '0 24px' }}>
          <button
            className={`artifact-tab ${activeTab === 'list' ? 'active' : ''}`}
            style={{ padding: '10px 16px', borderRadius: 0 }}
            onClick={() => setActiveTab('list')}
          >
            Indexed Sources ({sources.length})
          </button>
          <button
            className={`artifact-tab ${activeTab === 'ingest' ? 'active' : ''}`}
            style={{ padding: '10px 16px', borderRadius: 0 }}
            onClick={() => setActiveTab('ingest')}
          >
            + Ingest New Document
          </button>
        </div>

        <div className="modal-body">
          {successMessage && (
            <div
              style={{
                marginBottom: 16,
                padding: '8px 14px',
                backgroundColor: 'var(--success-bg)',
                border: '1px solid var(--success)',
                borderRadius: 'var(--radius-sm)',
                color: '#6ee7b7',
                fontSize: '0.82rem',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <CheckCircle size={15} />
              <span>{successMessage}</span>
            </div>
          )}

          {activeTab === 'list' ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Total Sources: {sources.length}
                </span>
                <button className="btn-secondary" onClick={handleRefresh} disabled={loading}>
                  <RefreshCw size={13} className={loading ? 'spin' : ''} />
                  <span>Refresh Counts</span>
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {sources.map((s) => (
                  <div
                    key={s.id}
                    style={{
                      padding: '12px 14px',
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <strong style={{ fontSize: '0.88rem', color: 'var(--text-main)' }}>{s.title}</strong>
                      <span className="badge-tag" style={{ color: 'var(--text-pure)', backgroundColor: 'var(--bg-hover)' }}>
                        {s.chunk_count} chunks
                      </span>
                    </div>

                    <div style={{ marginTop: 4, fontSize: '0.76rem', color: 'var(--text-muted)', display: 'flex', gap: 12 }}>
                      {s.author_or_guest && <span>Speaker / Guest: {s.author_or_guest}</span>}
                      <span>Type: {s.source_type}</span>
                      {s.url && (
                        <a
                          href={s.url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 3 }}
                        >
                          Link <ExternalLink size={10} />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <form onSubmit={handleIngest}>
              <div className="form-group">
                <label className="form-label">Document Title *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Lenny Podcast: Brian Chesky on Founder Mode"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="form-group">
                  <label className="form-label">Speaker / Author Reference</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Brian Chesky (Airbnb)"
                    value={newAuthor}
                    onChange={(e) => setNewAuthor(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Source Type</label>
                  <select
                    className="form-select"
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                  >
                    <option value="podcast_transcript">Podcast Transcript</option>
                    <option value="newsletter">Newsletter Article</option>
                    <option value="case_study">Case Study</option>
                    <option value="essay">Growth Essay</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Source URL (optional)</label>
                <input
                  type="url"
                  className="form-input"
                  placeholder="https://www.lennysnewsletter.com/..."
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Raw Text or Transcript Content *</label>
                <textarea
                  className="form-textarea"
                  rows={6}
                  placeholder="Paste article text or transcript here. It will be automatically parsed, chunked, and indexed with embeddings."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
                <button type="button" className="btn-secondary" onClick={() => setActiveTab('list')}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isSubmitting || !newTitle.trim() || !newContent.trim()}
                >
                  <Plus size={14} />
                  <span>{isSubmitting ? 'Indexing...' : 'Index Document'}</span>
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
