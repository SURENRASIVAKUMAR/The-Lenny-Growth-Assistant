import React from 'react';
import { Database, Settings as SettingsIcon, PanelRightClose, PanelRightOpen, Menu, Feather } from 'lucide-react';
import type { ConfigStatus } from '../types';

interface HeaderProps {
  sessionTitle: string;
  config: ConfigStatus | null;
  onOpenShip30: () => void;
  onOpenKnowledge: () => void;
  onOpenSettings: () => void;
  showArtifacts: boolean;
  onToggleArtifacts: () => void;
  onToggleSidebar: () => void;
  hasArtifacts: boolean;
  activeMode: 'standard' | 'ship30';
}

export const Header: React.FC<HeaderProps> = ({
  sessionTitle,
  config,
  onOpenShip30,
  onOpenKnowledge,
  onOpenSettings,
  showArtifacts,
  onToggleArtifacts,
  onToggleSidebar,
  hasArtifacts,
  activeMode,
}) => {
  return (
    <header className="top-nav">
      <div className="top-nav-left">
        <button
          className="icon-btn-subtle"
          onClick={onToggleSidebar}
          title="Toggle Sidebar"
          style={{ display: 'none' }}
        >
          <Menu size={18} />
        </button>
        <div className="active-session-title">
          <span>{sessionTitle || 'New Conversation'}</span>
        </div>
      </div>

      <div className="top-nav-right">
        {/* Ship 30 for 30 Skill Trigger */}
        <button
          className={`btn-secondary ${activeMode === 'ship30' ? 'btn-ship30-active' : ''}`}
          onClick={onOpenShip30}
          title="Ship 30 for 30 Essay Writer Mode"
        >
          <Feather size={15} />
          <span>Ship 30 for 30</span>
        </button>

        {/* Knowledge Base Explorer */}
        <button
          className="btn-secondary"
          onClick={onOpenKnowledge}
          title="Lenny Knowledge Base"
        >
          <Database size={15} />
          <span>Knowledge ({config?.rag_sources_count || 0})</span>
        </button>

        {/* Artifact Viewer Toggle */}
        <button
          className={`btn-secondary ${showArtifacts ? 'active' : ''}`}
          onClick={onToggleArtifacts}
          title={showArtifacts ? 'Hide Artifact Viewer' : 'Open Artifact Viewer'}
        >
          {showArtifacts ? <PanelRightClose size={15} /> : <PanelRightOpen size={15} />}
          <span>Artifacts {hasArtifacts ? '•' : ''}</span>
        </button>

        {/* Settings Modal */}
        <button
          className="btn-secondary"
          onClick={onOpenSettings}
          title="Settings & Provider Config"
        >
          <SettingsIcon size={15} />
          <span>Settings</span>
        </button>
      </div>
    </header>
  );
};
