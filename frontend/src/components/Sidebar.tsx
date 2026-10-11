import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Edit2, Database, Cpu } from 'lucide-react';
import type { Session, ConfigStatus } from '../types';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;
  onRenameSession: (id: string, newTitle: string) => void;
  onDeleteSession: (id: string) => void;
  config: ConfigStatus | null;
  isMobileOpen: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onRenameSession,
  onDeleteSession,
  config,
  isMobileOpen,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const handleStartRename = (e: React.MouseEvent, s: Session) => {
    e.stopPropagation();
    setEditingId(s.id);
    setEditTitle(s.title);
  };

  const handleSaveRename = (s: Session) => {
    if (editTitle.trim() && editTitle.trim() !== s.title) {
      onRenameSession(s.id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      onDeleteSession(id);
    }
  };

  return (
    <aside className={`sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-header">
        <div className="brand-badge">
          <div className="brand-icon">L</div>
          <div className="brand-text">
            <h1>Lenny Assistant</h1>
            <p>Product & Growth Intelligence</p>
          </div>
        </div>
      </div>

      <button className="new-chat-btn" onClick={onCreateSession}>
        <Plus size={16} />
        <span>New Conversation</span>
      </button>

      <div className="session-list-section">
        <div className="session-section-title">Conversations</div>
        {sessions.map((s) => {
          const isActive = s.id === activeSessionId;
          const isEditing = editingId === s.id;

          return (
            <div
              key={s.id}
              className={`session-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectSession(s.id)}
            >
              <MessageSquare size={14} style={{ marginRight: 8, flexShrink: 0 }} />
              
              {isEditing ? (
                <input
                  type="text"
                  className="form-input"
                  style={{ padding: '2px 6px', fontSize: '0.82rem', height: 26 }}
                  value={editTitle}
                  autoFocus
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={() => handleSaveRename(s)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveRename(s);
                    if (e.key === 'Escape') setEditingId(null);
                  }}
                />
              ) : (
                <span className="session-item-title" title={s.title}>
                  {s.title}
                </span>
              )}

              <div className="session-actions">
                <button
                  className="icon-btn-subtle"
                  title="Rename"
                  onClick={(e) => handleStartRename(e, s)}
                >
                  <Edit2 size={12} />
                </button>
                <button
                  className="icon-btn-subtle"
                  title="Delete"
                  onClick={(e) => handleDelete(e, s.id)}
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          );
        })}

        {sessions.length === 0 && (
          <div style={{ padding: '16px 10px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            No saved conversations yet. Click "New Conversation" to start.
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <div className="provider-status-badge">
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span className={`status-dot ${config?.database_status === 'connected' ? 'active' : 'inactive'}`} />
            <Database size={13} style={{ marginRight: 6 }} />
            <span>MySQL: {config?.database_name || 'lenny_growth_assistant'}</span>
          </div>
        </div>

        <div className="provider-status-badge">
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span className="status-dot active" />
            <Cpu size={13} style={{ marginRight: 6 }} />
            <span>
              {config?.active_provider === 'openai' ? 'OpenAI' : 'Ollama'}: {config?.active_model || 'Local'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
