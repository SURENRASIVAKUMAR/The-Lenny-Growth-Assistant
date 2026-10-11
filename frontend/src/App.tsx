import React, { useState, useEffect } from 'react';
import type {
  Session,
  Message,
  Artifact,
  ConfigStatus,
  Ship30Config,
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
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatArea } from './components/ChatArea';
import { ArtifactViewer } from './components/ArtifactViewer';
import { Ship30Modal } from './components/Ship30Modal';
import { KnowledgeModal } from './components/KnowledgeModal';
import { SettingsModal } from './components/SettingsModal';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);

  const [config, setConfig] = useState<ConfigStatus | null>(null);
  const [activeMode, setActiveMode] = useState<'standard' | 'ship30'>('standard');
  const [ship30PendingParams, setShip30PendingParams] = useState<Ship30Config | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  // Modals state
  const [isShip30ModalOpen, setIsShip30ModalOpen] = useState(false);
  const [isKnowledgeModalOpen, setIsKnowledgeModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

  // Custom provider overrides from Settings modal
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

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    setIsLoading(true);
    setErrorMessage(null);

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
        mode: activeMode,
        ship30Params: ship30PendingParams || undefined,
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

      // If a fallback warning occurred
      if (response.warning) {
        console.warn('Inference warning:', response.warning);
      }

      // Reset mode back to standard after Ship 30 execution
      if (activeMode === 'ship30') {
        setActiveMode('standard');
        setShip30PendingParams(null);
      }

      // Refresh sessions to update titles and message counts
      const updatedSessions = await fetchSessions();
      setSessions(updatedSessions);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error occurred while contacting the model.');
      // Remove temporary user message on error so user can retry
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleShip30Configure = (shipConfig: Ship30Config) => {
    setActiveMode('ship30');
    setShip30PendingParams(shipConfig);
    // Automatically trigger essay generation
    handleSendMessage(`Write a Ship 30 for 30 essay on: ${shipConfig.topic}`);
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

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <div className="app-container">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={selectSession}
        onCreateSession={handleCreateSession}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
        config={config}
        isMobileOpen={isMobileSidebarOpen}
      />

      <div className="main-content">
        <Header
          sessionTitle={activeSession?.title || 'New Conversation'}
          config={config}
          onOpenShip30={() => setIsShip30ModalOpen(true)}
          onOpenKnowledge={() => setIsKnowledgeModalOpen(true)}
          onOpenSettings={() => setIsSettingsModalOpen(true)}
          showArtifacts={showArtifacts}
          onToggleArtifacts={() => setShowArtifacts(!showArtifacts)}
          onToggleSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)}
          hasArtifacts={artifacts.length > 0}
          activeMode={activeMode}
        />

        <div className="workspace-layout">
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            activeMode={activeMode}
            onResetMode={() => {
              setActiveMode('standard');
              setShip30PendingParams(null);
            }}
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
      </div>

      {/* Modals */}
      <Ship30Modal
        isOpen={isShip30ModalOpen}
        onClose={() => setIsShip30ModalOpen(false)}
        onSubmit={handleShip30Configure}
      />

      <KnowledgeModal
        isOpen={isKnowledgeModalOpen}
        onClose={() => setIsKnowledgeModalOpen(false)}
        onSourcesUpdated={async () => {
          const cfg = await fetchConfigStatus();
          setConfig(cfg);
        }}
      />

      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        config={config}
        onSaveProvider={handleSaveProviderConfig}
      />
    </div>
  );
};

export default App;
