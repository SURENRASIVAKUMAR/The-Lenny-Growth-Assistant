import React, { useState } from 'react';
import { Feather, X, Sparkles } from 'lucide-react';
import type { Ship30Config } from '../types';

interface Ship30ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (config: Ship30Config) => void;
}

const PRESET_TOPICS = [
  'Why Activation Metrics Fail in B2B SaaS and How to Fix Them',
  'The Four PMF Fits Every Founder Overlooks Before Series A',
  'The Hidden Per-Seat Pricing Trap in Collaborative Products',
  'The Three PM Archetypes: When to Hire for Innovation vs Execution',
];

export const Ship30Modal: React.FC<Ship30ModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [topic, setTopic] = useState('');
  const [audience, setAudience] = useState('Product managers, founders, and growth leaders');
  const [tone, setTone] = useState('Authoritative, tactical, conversational, and analytical');
  const [targetLength, setTargetLength] = useState(1250);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    onSubmit({
      topic: topic.trim(),
      audience,
      tone,
      target_length: targetLength,
    });
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                background: 'var(--gold-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#1a1001',
              }}
            >
              <Feather size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Ship 30 for 30 Essay Writer</h3>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                Dedicated high-impact essay generation (~1,250 words) grounded in Lenny's Growth Knowledge Base
              </p>
            </div>
          </div>
          <button className="icon-btn-subtle" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {/* Quick Topic Chips */}
            <div style={{ marginBottom: 16 }}>
              <label className="form-label">Suggested High-Signal Topics:</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {PRESET_TOPICS.map((t, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="example-card"
                    style={{ padding: '8px 12px', fontSize: '0.8rem', textAlign: 'left' }}
                    onClick={() => setTopic(t)}
                  >
                    <Sparkles size={12} style={{ marginRight: 6, color: '#f59e0b', verticalAlign: 'middle' }} />
                    <span>{t}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Topic Input */}
            <div className="form-group">
              <label className="form-label">Essay Topic & Thesis Statement *</label>
              <textarea
                className="form-textarea"
                rows={2}
                placeholder="What core growth or product insight should this essay explore?"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                required
              />
            </div>

            {/* Target Audience */}
            <div className="form-group">
              <label className="form-label">Target Audience</label>
              <input
                type="text"
                className="form-input"
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {/* Tone */}
              <div className="form-group">
                <label className="form-label">Tone & Style</label>
                <input
                  type="text"
                  className="form-input"
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                />
              </div>

              {/* Target Length */}
              <div className="form-group">
                <label className="form-label">Target Word Count (~{targetLength} words)</label>
                <input
                  type="number"
                  className="form-input"
                  min={500}
                  max={2500}
                  step={50}
                  value={targetLength}
                  onChange={(e) => setTargetLength(Number(e.target.value))}
                />
              </div>
            </div>

            <div
              style={{
                padding: '10px 14px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.25)',
                fontSize: '0.78rem',
                color: '#fcd34d',
                lineHeight: 1.5,
              }}
            >
              <strong>Ship 30 Framework:</strong> Includes a counter-intuitive hook, single clear thesis, narrative progression with high-signal subheadings, evidence citations from the knowledge base, and an actionable takeaway.
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="new-chat-btn"
              style={{ margin: 0, background: 'var(--gold-gradient)', color: '#1a1001' }}
              disabled={!topic.trim()}
            >
              <Feather size={14} />
              <span>Generate Essay Artifact</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
