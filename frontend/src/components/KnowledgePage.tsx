import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Search,
  ExternalLink,
  Plus,
  RefreshCw,
  MessageSquare,
} from 'lucide-react';
import type { KnowledgeSource } from '../types';
import { fetchKnowledgeSources, ingestDocument, refreshKnowledge } from '../services/api';

interface KnowledgePageProps {
  onBackToChat: () => void;
  onAskAboutEpisode: (query: string) => void;
  onSourcesUpdated: () => void;
}

export const KnowledgePage: React.FC<KnowledgePageProps> = ({
  onBackToChat,
  onAskAboutEpisode,
  onSourcesUpdated,
}) => {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'explore' | 'ingest'>('explore');

  // Ingest form state
  const [newTitle, setNewTitle] = useState('');
  const [newAuthor, setNewAuthor] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [newContent, setNewContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    loadSources();
  }, []);

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
      setToastMessage('Knowledge database successfully synchronized.');
      setTimeout(() => setToastMessage(null), 3000);
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
        url: newUrl.trim() || undefined,
        source_type: 'podcast_transcript',
      });
      setNewTitle('');
      setNewAuthor('');
      setNewUrl('');
      setNewContent('');
      await loadSources();
      onSourcesUpdated();
      setActiveTab('explore');
      setToastMessage('Document indexed and embedded successfully.');
      setTimeout(() => setToastMessage(null), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredSources = sources.filter((s) => {
    const q = searchQuery.toLowerCase();
    return (
      s.title.toLowerCase().includes(q) ||
      (s.author_or_guest && s.author_or_guest.toLowerCase().includes(q))
    );
  });

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-left">
          <button className="icon-btn-subtle" onClick={onBackToChat} title="Back to Chat">
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="page-title">Knowledge Library</h1>
            <p className="page-subtitle">
              Browse {sources.length} authoritative episodes from Lenny's Podcast transcript repository
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {toastMessage && (
            <div className="page-toast-pill">
              <span>{toastMessage}</span>
            </div>
          )}
          <button className="btn-secondary" onClick={handleRefresh} disabled={loading} title="Re-sync Database">
            <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
            <span>Sync</span>
          </button>
          <button
            className={`btn-secondary ${activeTab === 'ingest' ? 'active' : ''}`}
            onClick={() => setActiveTab(activeTab === 'explore' ? 'ingest' : 'explore')}
          >
            <Plus size={14} />
            <span>{activeTab === 'ingest' ? 'View Archive' : 'Add Transcript'}</span>
          </button>
        </div>
      </div>

      <div className="knowledge-body-pane">
        {activeTab === 'explore' ? (
          <>
            {/* Search Input Bar */}
            <div className="knowledge-search-row">
              <div className="knowledge-search-input-wrapper">
                <Search size={16} color="var(--text-muted)" />
                <input
                  type="text"
                  className="knowledge-search-input"
                  placeholder="Search by guest (e.g. Elena Verna, Casey Winters, Brian Chesky) or growth topic..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            {/* Grid of Knowledge Cards */}
            <div className="knowledge-grid">
              {filteredSources.length === 0 ? (
                <div className="knowledge-empty">
                  <p>No matching episodes found for "{searchQuery}".</p>
                </div>
              ) : (
                filteredSources.map((s) => (
                  <div key={s.id} className="knowledge-card">
                    <div className="knowledge-card-header">
                      <h3 className="knowledge-card-title">{s.title}</h3>
                      {s.url && (
                        <a
                          href={s.url}
                          target="_blank"
                          rel="noreferrer"
                          className="icon-btn-subtle"
                          title="Watch on YouTube"
                        >
                          <ExternalLink size={14} />
                        </a>
                      )}
                    </div>

                    <div className="knowledge-card-meta">
                      {s.author_or_guest && (
                        <span className="badge-pill active">Guest: {s.author_or_guest}</span>
                      )}
                      <span className="badge-pill">{s.chunk_count} Chunks</span>
                    </div>

                    {s.summary && (
                      <p className="knowledge-card-summary">{s.summary}</p>
                    )}

                    <div className="knowledge-card-footer">
                      <button
                        className="btn-secondary"
                        style={{ fontSize: '0.78rem', padding: '5px 10px', width: '100%', justifyContent: 'center' }}
                        onClick={() =>
                          onAskAboutEpisode(
                            `What core insights and growth frameworks does ${s.author_or_guest || s.title} share?`
                          )
                        }
                      >
                        <MessageSquare size={13} />
                        <span>Ask Assistant About This Episode</span>
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        ) : (
          /* Ingest New Transcript Form */
          <div className="ingest-form-card">
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 6 }}>Index New Source Material</h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: 20 }}>
              Add extra podcast episodes or newsletter articles. The text will be chunked and indexed into the active database.
            </p>

            <form onSubmit={handleIngest} className="settings-form">
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Episode or Article Title *</label>
                  <input
                    type="text"
                    className="form-input"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Guest or Author Name</label>
                  <input
                    type="text"
                    className="form-input"
                    value={newAuthor}
                    onChange={(e) => setNewAuthor(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Source URL (YouTube or Substack)</label>
                <input
                  type="url"
                  className="form-input"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Transcript / Article Content *</label>
                <textarea
                  className="form-textarea"
                  rows={8}
                  placeholder="Paste raw transcript text here..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  required
                />
              </div>

              <div className="form-actions-row">
                <button type="submit" className="btn-primary" disabled={isSubmitting}>
                  <Plus size={14} />
                  <span>{isSubmitting ? 'Indexing...' : 'Index & Save into Knowledge Base'}</span>
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgePage;
