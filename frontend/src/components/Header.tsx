import React, { useState, useRef, useEffect } from 'react';
import {
  Sidebar as SidebarIcon,
  PanelRightClose,
  PanelRightOpen,
  Settings as SettingsIcon,
  BookOpen,
  Feather,
  MessageSquare,
  Palette,
  Check,
} from 'lucide-react';
import type { ConfigStatus, ThemeType } from '../types';
import type { ActiveView } from './Sidebar';

interface HeaderProps {
  showArtifacts: boolean;
  onToggleArtifacts: () => void;
  onToggleSidebar: () => void;
  hasArtifacts: boolean;
  activeView: ActiveView;
  onNavigate: (view: ActiveView) => void;
  config?: ConfigStatus | null;
  theme: ThemeType;
  onThemeChange: (theme: ThemeType) => void;
}

const THEMES: { id: ThemeType; label: string; color: string; desc: string }[] = [
  { id: 'oled', label: 'Black (Dark Mode)', color: '#000000', desc: 'Pure Pitch Black' },
  { id: 'light', label: 'White (Light Mode)', color: '#ffffff', desc: 'Pure Clean White' },
];

export const Header: React.FC<HeaderProps> = ({
  showArtifacts,
  onToggleArtifacts,
  onToggleSidebar,
  hasArtifacts,
  activeView,
  onNavigate,
  theme,
  onThemeChange,
}) => {
  const [isThemeOpen, setIsThemeOpen] = useState(false);
  const themeMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (themeMenuRef.current && !themeMenuRef.current.contains(e.target as Node)) {
        setIsThemeOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  return (
    <header className="top-nav">
      {/* Left: Sidebar toggle */}
      <div className="top-nav-left">
        <button
          className="gpt-circle-btn"
          onClick={onToggleSidebar}
          title="Toggle Sidebar"
        >
          <SidebarIcon size={17} />
        </button>
      </div>

      {/* Center: Sleek Monochrome Page Switcher */}
      <div className="top-nav-center">
        <div className="segmented-control">
          <button
            id="header-tab-chat"
            type="button"
            className={`segmented-tab ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => onNavigate('chat')}
          >
            <MessageSquare size={13} />
            <span>Chat</span>
          </button>
          <button
            id="header-tab-ship30"
            type="button"
            className={`segmented-tab ${activeView === 'ship30' ? 'active' : ''}`}
            onClick={() => onNavigate('ship30')}
          >
            <Feather size={13} />
            <span>Ship 30 Studio</span>
          </button>
          <button
            id="header-tab-knowledge"
            type="button"
            className={`segmented-tab ${activeView === 'knowledge' ? 'active' : ''}`}
            onClick={() => onNavigate('knowledge')}
          >
            <BookOpen size={13} />
            <span>Knowledge</span>
          </button>
        </div>
      </div>

      {/* Right Actions: Canvas Toggle & Settings */}
      <div className="top-nav-right">
        {/* Canvas Toggle (visible on chat view) */}
        {activeView === 'chat' && (
          <button
            id="header-canvas-btn"
            type="button"
            className={`btn-secondary ${showArtifacts ? 'active' : ''}`}
            onClick={onToggleArtifacts}
            title={showArtifacts ? 'Close Canvas' : 'Open Canvas'}
          >
            {showArtifacts ? <PanelRightClose size={14} /> : <PanelRightOpen size={14} />}
            <span>Canvas</span>
            {hasArtifacts && <span className="canvas-dot-indicator" />}
          </button>
        )}

        {/* Theme Switcher Dropdown */}
        <div className="theme-switcher-wrapper" ref={themeMenuRef}>
          <button
            id="header-theme-btn"
            type="button"
            className="gpt-circle-btn"
            onClick={() => setIsThemeOpen(!isThemeOpen)}
            title="Change Background & Theme"
          >
            <Palette size={16} />
          </button>

          {isThemeOpen && (
            <div className="theme-dropdown-menu">
              <div className="theme-menu-header">Background Theme</div>
              {THEMES.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  className={`theme-menu-item ${theme === t.id ? 'active' : ''}`}
                  onClick={() => {
                    onThemeChange(t.id);
                    setIsThemeOpen(false);
                  }}
                >
                  <div className="theme-item-left">
                    <span
                      className="theme-color-bullet"
                      style={{ backgroundColor: t.color, boxShadow: `0 0 6px ${t.color}` }}
                    />
                    <span>{t.label}</span>
                  </div>
                  {theme === t.id && <Check size={13} color="var(--accent-color, #fff)" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Settings Page Button */}
        <button
          id="header-settings-btn"
          type="button"
          className={`gpt-circle-btn ${activeView === 'settings' ? 'active' : ''}`}
          onClick={() => onNavigate('settings')}
          title="Settings & Account"
        >
          <SettingsIcon size={16} />
        </button>
      </div>
    </header>
  );
};

export default Header;
