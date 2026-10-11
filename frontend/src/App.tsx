import React, { useState, useEffect } from 'react';
import type {
  Session,
  Message,
  Artifact,
  ConfigStatus,
  Ship30Config,
  ThemeType,
} from './types';
import {
  fetchConfigStatus,
  fetchSessions,
  createSession,
  renameSession,
  deleteSession,
  fetchMessages,
  sendChatMessage,
  fetchArtifacts,
} from './services/api';
import { Sidebar, type ActiveView } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatArea } from './components/ChatArea';
import { ArtifactViewer } from './components/ArtifactViewer';
import { SettingsPage } from './components/SettingsPage';
import { Ship30StudioPage } from './components/Ship30StudioPage';
import { KnowledgePage } from './components/KnowledgePage';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);

  const [config, setConfig] = useState<ConfigStatus | null>(null);
  const [activeView, setActiveView] = useState<ActiveView>('chat');
  const [activeMode, setActiveMode] = useState<'standard' | 'ship30'>('standard');
  const [ship30PendingParams, setShip30PendingParams] = useState<Ship30Config | null>(null);

  // Black & White Theme System: 'oled' (Black, default), 'light' (White)
  const [theme, setTheme] = useState<ThemeType>(() => {
    const saved = localStorage.getItem('lenny_theme') as ThemeType;
    if (saved === 'light') return 'light';
    return 'oled';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('lenny_theme', theme);
  }, [theme]);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Custom provider overrides from Settings
  const [providerOverride, setProviderOverride] = useState<string | undefined>(undefined);
  const [modelOverride, setModelOverride] = useState<string | undefined>(undefined);

  // Initial load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const cfg = await fetchConfigStatus();
      setConfig(cfg);
      const sessionList = await fetchSessions();
      setSessions(sessionList);
      if (sessionList.length > 0) {
        selectSession(sessionList[0].id);
      } else {
        handleCreateSession();
      }
    } catch (err: any) {
      console.error('Failed to load initial data', err);
      setErrorMessage(`Failed to connect to backend: ${err.message}`);
    }
  };

  const selectSession = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    setIsMobileSidebarOpen(false);
    try {
      const msgs = await fetchMessages(sessionId);
      setMessages(msgs);
      const arts = await fetchArtifacts(sessionId);
      setArtifacts(arts);
      if (arts.length > 0) {
        setActiveArtifactId(arts[0].id);
        setShowArtifacts(true);
      } else {
        setShowArtifacts(false);
      }
    } catch (err: any) {
      console.error('Error loading session messages', err);
    }
  };

  const handleCreateSession = async () => {
    try {
      const newSession = await createSession('New Conversation');
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
      setMessages([]);
      setArtifacts([]);
      setShowArtifacts(false);
    } catch (err: any) {
      setErrorMessage(`Failed to create conversation: ${err.message}`);
    }
  };

  const handleRenameSession = async (id: string, newTitle: string) => {
    try {
      const updated = await renameSession(id, newTitle);
      setSessions((prev) => prev.map((s) => (s.id === id ? updated : s)));
    } catch (err: any) {
      setErrorMessage(`Failed to rename conversation: ${err.message}`);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      const remaining = sessions.filter((s) => s.id !== id);
      setSessions(remaining);
      if (activeSessionId === id) {
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          handleCreateSession();
        }
      }
    } catch (err: any) {
      setErrorMessage(`Failed to delete conversation: ${err.message}`);
    }
  };

  const handleSendMessage = async (text: string, overrideMode?: 'standard' | 'ship30', overrideParams?: Ship30Config) => {
    if (!text.trim() || isLoading) return;

    setIsLoading(true);
    setErrorMessage(null);

    const modeToUse = overrideMode || activeMode;
    const paramsToUse = overrideParams || ship30PendingParams;

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: activeSessionId || '',
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendChatMessage({
        sessionId: activeSessionId || undefined,
        message: text,
        mode: modeToUse,
        ship30Params: paramsToUse || undefined,
        provider: providerOverride,
        model: modelOverride,
      });

      // Update active session ID if newly assigned
      if (!activeSessionId && response.session_id) {
        setActiveSessionId(response.session_id);
      }

      // Append assistant message
      setMessages((prev) => [...prev, response.message]);

      // If an artifact was generated
      if (response.artifact) {
        const newArtifact = response.artifact as Artifact;
        setArtifacts((prev) => [newArtifact, ...prev]);
        setActiveArtifactId(newArtifact.id);
        setShowArtifacts(true);
      }

      // Reset mode back to standard after Ship 30 execution
      if (modeToUse === 'ship30') {
        setActiveMode('standard');
        setShip30PendingParams(null);
      }

      // Refresh sessions to update titles and message counts
      const updatedSessions = await fetchSessions();
      setSessions(updatedSessions);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error occurred while contacting the model.');
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleShip30StudioGenerate = (shipConfig: Ship30Config) => {
    setActiveMode('ship30');
    setShip30PendingParams(shipConfig);
    handleSendMessage(`Write a Ship 30 for 30 essay on: ${shipConfig.topic}`, 'ship30', shipConfig);
  };

  const handleAskAboutEpisode = (query: string) => {
    setActiveView('chat');
    handleSendMessage(query);
  };

  const handleSaveProviderConfig = (provider: string, model: string) => {
    setProviderOverride(provider);
    setModelOverride(model);
    if (config) {
      setConfig({
        ...config,
        active_provider: provider,
        active_model: model,
      });
    }
  };

  return (
    <div className="app-container">
      {/* Primary Sidebar with Page Navigation */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={selectSession}
        onCreateSession={handleCreateSession}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
        config={config}
        isMobileOpen={isMobileSidebarOpen}
        activeView={activeView}
        onNavigate={(view) => {
          setActiveView(view);
          setIsMobileSidebarOpen(false);
        }}
      />

      <div className="main-content">
        {/* Top Header with Active Page Switcher & Theme Picker */}
        <Header
          config={config}
          showArtifacts={showArtifacts}
          onToggleArtifacts={() => setShowArtifacts(!showArtifacts)}
          onToggleSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
          hasArtifacts={artifacts.length > 0}
          activeView={activeView}
          onNavigate={setActiveView}
          theme={theme}
          onThemeChange={setTheme}
        />

        {/* View Routing */}
        {activeView === 'chat' && (
          <div className="workspace-layout">
            <ChatArea
              messages={messages}
              isLoading={isLoading}
              onSendMessage={(text) => handleSendMessage(text)}
              activeMode={activeMode}
              onResetMode={() => {
                setActiveMode('standard');
                setShip30PendingParams(null);
              }}
              onOpenShip30={() => setActiveView('ship30')}
              onOpenKnowledge={() => setActiveView('knowledge')}
              errorMessage={errorMessage}
              onClearError={() => setErrorMessage(null)}
              onOpenArtifact={() => setShowArtifacts(true)}
              hasArtifacts={artifacts.length > 0}
            />

            {showArtifacts && (
              <ArtifactViewer
                artifacts={artifacts}
                activeArtifactId={activeArtifactId}
                onSelectArtifact={(id) => setActiveArtifactId(id)}
                onClose={() => setShowArtifacts(false)}
              />
            )}
          </div>
        )}

        {activeView === 'settings' && (
          <SettingsPage
            config={config}
            onSaveProvider={handleSaveProviderConfig}
            onBackToChat={() => setActiveView('chat')}
            theme={theme}
            onThemeChange={setTheme}
          />
        )}

        {activeView === 'ship30' && (
          <Ship30StudioPage
            onGenerateEssay={handleShip30StudioGenerate}
            onBackToChat={() => setActiveView('chat')}
            latestArtifact={artifacts.find((a) => a.artifact_type === 'essay') || artifacts[0]}
            isLoading={isLoading}
          />
        )}

        {activeView === 'knowledge' && (
          <KnowledgePage
            onBackToChat={() => setActiveView('chat')}
            onAskAboutEpisode={handleAskAboutEpisode}
            onSourcesUpdated={async () => {
              const cfg = await fetchConfigStatus();
              setConfig(cfg);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default App;
