import React, { useState } from 'react';
import {
  Feather,
  ArrowLeft,
  Sparkles,
  Copy,
  Download,
  Check,
  BookOpen,
} from 'lucide-react';
import type { Ship30Config, Artifact } from '../types';

interface Ship30StudioPageProps {
  onGenerateEssay: (config: Ship30Config) => void;
  onBackToChat: () => void;
  latestArtifact?: Artifact | null;
  isLoading: boolean;
}

const PRESET_TOPICS = [
  {
    title: '10 Growth Tactics That Never Work',
    guest: 'Elena Verna',
    desc: 'Empirical critique of superficial growth hacks vs durable loops',
  },
  {
    title: 'Why Your Activation Metric is Lying to You',
    guest: 'Casey Winters',
    desc: 'Optimizing for long-term habit formation over vanity signups',
  },
  {
    title: 'The SaaS Pricing & Packaging Playbook',
    guest: 'Patrick Campbell',
    desc: 'Avoiding the per-seat trap and aligning with value metrics',
  },
  {
    title: 'Founder-Led Product Management',
    guest: 'Brian Chesky',
    desc: 'Moving past feature factory PM models towards agency and design craft',
  },
];

export const Ship30StudioPage: React.FC<Ship30StudioPageProps> = ({
  onGenerateEssay,
  onBackToChat,
  latestArtifact,
  isLoading,
}) => {
  const [topic, setTopic] = useState('10 Growth Tactics That Never Work');
  const [audience, setAudience] = useState('Founders, VPs of Growth, and Product Leaders');
  const [tone, setTone] = useState('Authoritative, tactical, conversational, and analytical');
  const [targetLength, setTargetLength] = useState(1250);
  const [copied, setCopied] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim() || isLoading) return;
    onGenerateEssay({
      topic: topic.trim(),
      audience,
      tone,
      target_length: targetLength,
    });
  };

  const handleCopy = () => {
    if (!latestArtifact) return;
    navigator.clipboard.writeText(latestArtifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!latestArtifact) return;
    const blob = new Blob([latestArtifact.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(latestArtifact.title || 'ship30-essay').toLowerCase().replace(/[^a-z0-9]+/g, '-')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-container">
      {/* Studio Header */}
      <div className="page-header">
        <div className="page-header-left">
          <button className="icon-btn-subtle" onClick={onBackToChat} title="Back to Chat">
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="page-title">Ship 30 for 30 Essay Studio</h1>
            <p className="page-subtitle">
              Draft structured, high-signal essays (~1,250 words) backed by Lenny's Podcast transcripts archive
            </p>
          </div>
        </div>
      </div>

      <div className="studio-layout-grid">
        {/* Left Form Builder Pane */}
        <aside className="studio-builder-pane">
          <form onSubmit={handleSubmit} className="studio-form">
            <div className="form-group">
              <label className="form-label">Essay Topic or Thesis *</label>
              <textarea
                className="form-textarea"
                rows={3}
                placeholder="What growth framework, PM law, or tactic do you want to explore?"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                required
              />
            </div>

            {/* Curated Presets */}
            <div className="form-group">
              <label className="form-label">High-Signal Transcripts Presets</label>
              <div className="preset-topics-list">
                {PRESET_TOPICS.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="preset-topic-btn"
                    onClick={() => setTopic(p.title)}
                  >
                    <div className="preset-topic-header">
                      <strong>{p.title}</strong>
                      <span className="badge-pill">{p.guest}</span>
                    </div>
                    <p>{p.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Target Audience</label>
              <input
                type="text"
                className="form-input"
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Tone & Style</label>
              <input
                type="text"
                className="form-input"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
              />
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <label className="form-label" style={{ marginBottom: 0 }}>Target Word Count</label>
                <span style={{ fontSize: '0.82rem', color: '#ffffff', fontWeight: 600 }}>{targetLength} words</span>
              </div>
              <input
                type="range"
                min={600}
                max={2000}
                step={50}
                value={targetLength}
                onChange={(e) => setTargetLength(Number(e.target.value))}
                style={{ width: '100%', accentColor: '#ffffff' }}
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '12px 18px', marginTop: 10 }}
              disabled={isLoading || !topic.trim()}
            >
              <Feather size={16} />
              <span>{isLoading ? 'Synthesizing Grounded Essay...' : 'Generate Ship 30 Essay'}</span>
            </button>
          </form>
        </aside>

        {/* Right Output / Live Preview Pane */}
        <main className="studio-preview-pane">
          <div className="studio-preview-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <BookOpen size={16} />
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                {latestArtifact ? latestArtifact.title : 'Generated Essay Preview'}
              </span>
            </div>
            {latestArtifact && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <button className="btn-secondary" onClick={handleCopy} title="Copy to clipboard">
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
                <button className="btn-secondary" onClick={handleDownload} title="Download Markdown">
                  <Download size={14} />
                  <span>Download .md</span>
                </button>
              </div>
            )}
          </div>

          <div className="studio-preview-body">
            {isLoading ? (
              <div className="studio-empty-state">
                <div className="thinking-indicator" style={{ flexDirection: 'column', gap: 14 }}>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <span className="thinking-dot" />
                    <span className="thinking-dot" />
                    <span className="thinking-dot" />
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Retrieving transcript excerpts & applying Ship 30 structure...
                  </p>
                </div>
              </div>
            ) : latestArtifact ? (
              <div className="markdown-body studio-essay-content">
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', background: 'transparent', border: 'none', padding: 0 }}>
                  {latestArtifact.content}
                </pre>
              </div>
            ) : (
              <div className="studio-empty-state">
                <div className="hero-logo-wrapper" style={{ marginBottom: 12 }}>
                  <Sparkles size={36} color="#71717a" />
                </div>
                <h3>Ready to Draft</h3>
                <p>Select a topic from the left pane and click Generate to produce an authoritative essay.</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Ship30StudioPage;
