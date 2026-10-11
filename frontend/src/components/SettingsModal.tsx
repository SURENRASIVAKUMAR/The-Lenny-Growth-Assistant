import React, { useState } from 'react';
import { Settings as SettingsIcon, X, Info } from 'lucide-react';
import type { ConfigStatus } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  config: ConfigStatus | null;
  onSaveProvider: (provider: string, model: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  config,
  onSaveProvider,
}) => {
  const [selectedProvider, setSelectedProvider] = useState(config?.active_provider || 'ollama');
  const [selectedModel, setSelectedModel] = useState(config?.active_model || 'llama3:latest');

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveProvider(selectedProvider, selectedModel);
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
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-hover)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
              }}
            >
              <SettingsIcon size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>System & AI Configuration</h3>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                Provider selection, database health, and inference endpoints
              </p>
            </div>
          </div>
          <button className="icon-btn-subtle" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {/* Provider Selection */}
          <div className="form-group">
            <label className="form-label">Active AI Inference Provider</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <div
                className={`example-card ${selectedProvider === 'ollama' ? 'active' : ''}`}
                style={{
                  border: selectedProvider === 'ollama' ? '1px solid var(--accent-primary)' : undefined,
                  backgroundColor: selectedProvider === 'ollama' ? 'rgba(99, 102, 241, 0.12)' : undefined,
                }}
                onClick={() => {
                  setSelectedProvider('ollama');
                  setSelectedModel('llama3:latest');
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <strong>Local Ollama</strong>
                  {config?.ollama_available ? (
                    <span className="badge-tag" style={{ color: '#6ee7b7' }}>Online</span>
                  ) : (
                    <span className="badge-tag" style={{ color: '#fcd34d' }}>Not detected</span>
                  )}
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  Privacy-first local models (http://localhost:11434)
                </p>
              </div>

              <div
                className={`example-card ${selectedProvider === 'openai' ? 'active' : ''}`}
                style={{
                  border: selectedProvider === 'openai' ? '1px solid var(--accent-primary)' : undefined,
                  backgroundColor: selectedProvider === 'openai' ? 'rgba(99, 102, 241, 0.12)' : undefined,
                }}
                onClick={() => {
                  setSelectedProvider('openai');
                  setSelectedModel('gpt-4o-mini');
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <strong>Cloud OpenAI</strong>
                  {config?.openai_configured ? (
                    <span className="badge-tag" style={{ color: '#6ee7b7' }}>Key Present</span>
                  ) : (
                    <span className="badge-tag" style={{ color: '#f87171' }}>Missing Key</span>
                  )}
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  High-speed cloud models (gpt-4o-mini, gpt-4o)
                </p>
              </div>
            </div>
          </div>

          {/* Model Specification */}
          <div className="form-group">
            <label className="form-label">Model Identifier</label>
            <input
              type="text"
              className="form-input"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              placeholder={selectedProvider === 'openai' ? 'gpt-4o-mini' : 'llama3:latest'}
            />
          </div>

          {/* System Diagnostics Card */}
          <div
            style={{
              padding: '14px',
              backgroundColor: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.82rem',
              display: 'flex',
              flexDirection: 'column',
              gap: 8,
            }}
          >
            <strong style={{ color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Info size={14} /> System Diagnostics
            </strong>

            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Database (XAMPP MySQL):</span>
              <span style={{ color: '#6ee7b7', fontWeight: 600 }}>
                {config?.database_name} ({config?.database_status})
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Knowledge Base Chunks:</span>
              <span style={{ color: '#c7d2fe' }}>{config?.rag_chunks_count} chunks indexed</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
              <span>Ollama Endpoint:</span>
              <span>{config?.ollama_base_url}</span>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="new-chat-btn" style={{ margin: 0 }} onClick={handleSave}>
            Apply Settings
          </button>
        </div>
      </div>
    </div>
  );
};
