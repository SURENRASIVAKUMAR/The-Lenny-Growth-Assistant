import React, { useState } from 'react';
import {
  Plus,
  Trash2,
  Edit2,
  Check,
  X,
  MessageSquare,
  Feather,
  BookOpen,
  Settings as SettingsIcon,
} from 'lucide-react';
import type { Session, ConfigStatus } from '../types';
import { Logo } from './Logo';

export type ActiveView = 'chat' | 'settings' | 'ship30' | 'knowledge';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onCreateSession: () => void;
  onRenameSession: (id: string, newTitle: string) => void;
  onDeleteSession: (id: string) => void;
  config: ConfigStatus | null;
  isMobileOpen: boolean;
  activeView: ActiveView;
  onNavigate: (view: ActiveView) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onRenameSession,
  onDeleteSession,
  isMobileOpen,
  activeView,
  onNavigate,
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
    if (window.confirm('Delete this conversation?')) {
      onDeleteSession(id);
    }
  };

  const handleChatSelect = (id: string) => {
    onSelectSession(id);
    onNavigate('chat');
  };

  const handleNewChat = () => {
    onCreateSession();
    onNavigate('chat');
  };

  return (
    <aside className={`sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
      {/* Brand Header */}
      <div className="sidebar-header" onClick={() => onNavigate('chat')}>
        <div className="sidebar-brand">
          <Logo size={24} />
          <span className="sidebar-brand-title">Lenny Growth</span>
        </div>
      </div>

      {/* Primary Action: New Chat Button */}
      <div className="sidebar-new-chat-wrapper">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <Plus size={16} />
          <span>New chat</span>
        </button>
      </div>

      {/* Main Pages Navigation */}
      <div className="sidebar-nav-links">
        <button
          id="nav-chat"
          type="button"
          className={`sidebar-nav-item ${activeView === 'chat' ? 'active' : ''}`}
          onClick={() => onNavigate('chat')}
        >
          <MessageSquare size={16} />
          <span>Chat</span>
        </button>
        <button
          id="nav-ship30"
          type="button"
          className={`sidebar-nav-item ${activeView === 'ship30' ? 'active' : ''}`}
          onClick={() => onNavigate('ship30')}
        >
          <Feather size={16} />
          <span>Ship 30 Studio</span>
        </button>
        <button
          id="nav-knowledge"
          type="button"
          className={`sidebar-nav-item ${activeView === 'knowledge' ? 'active' : ''}`}
          onClick={() => onNavigate('knowledge')}
        >
          <BookOpen size={16} />
          <span>Knowledge Library</span>
        </button>
        <button
          id="nav-settings"
          type="button"
          className={`sidebar-nav-item ${activeView === 'settings' ? 'active' : ''}`}
          onClick={() => onNavigate('settings')}
        >
          <SettingsIcon size={16} />
          <span>Settings & Account</span>
        </button>
      </div>

      {/* Conversations Stream */}
      <div className="session-list-section">
        <div className="session-section-title">Recent Conversations</div>
        <div className="session-items-scroll">
          {sessions.length === 0 ? (
            <div className="session-empty-hint">No past conversations</div>
          ) : (
            sessions.map((s) => {
              const isActive = activeView === 'chat' && s.id === activeSessionId;
              const isEditing = editingId === s.id;

              return (
                <div
                  key={s.id}
                  className={`session-item ${isActive ? 'active' : ''}`}
                  onClick={() => handleChatSelect(s.id)}
                >
                  <MessageSquare size={13} className="session-item-icon" />

                  {isEditing ? (
                    <div className="session-edit-row" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        className="session-edit-input"
                        value={editTitle}
                        autoFocus
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveRename(s);
                          if (e.key === 'Escape') setEditingId(null);
                        }}
                      />
                      <button
                        className="icon-btn-micro"
                        onClick={() => handleSaveRename(s)}
                        title="Save"
                      >
                        <Check size={12} />
                      </button>
                      <button
                        className="icon-btn-micro"
                        onClick={() => setEditingId(null)}
                        title="Cancel"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  ) : (
                    <span className="session-item-title" title={s.title}>
                      {s.title}
                    </span>
                  )}

                  {!isEditing && (
                    <div className="session-actions">
                      <button
                        className="icon-btn-subtle"
                        title="Rename"
                        onClick={(e) => handleStartRename(e, s)}
                      >
                        <Edit2 size={12} />
                      </button>
                      <button
                        className="icon-btn-subtle delete-action"
                        title="Delete"
                        onClick={(e) => handleDelete(e, s.id)}
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Sidebar Footer: User Profile Card (Navigates to Settings Page) */}
      <div className="sidebar-footer">
        <button
          type="button"
          className={`sidebar-user-card ${activeView === 'settings' ? 'active' : ''}`}
          onClick={() => onNavigate('settings')}
          title="Open Settings & Account"
        >
          <div className="sidebar-user-avatar">SS</div>
          <div className="sidebar-user-meta">
            <span className="sidebar-user-name">Surenra S</span>
            <span className="sidebar-user-badge">Pro Member • Settings</span>
          </div>
          <span className="sidebar-user-settings-icon">
            <SettingsIcon size={15} />
          </span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
