import React, { useState, useRef, useEffect } from 'react';
import { Plus, ArrowUp, Sparkles, Globe, AlertCircle, X, Compass, Feather } from 'lucide-react';
import type { Message } from '../types';
import { ChatMessage } from './ChatMessage';
import { Logo } from './Logo';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  activeMode: 'standard' | 'ship30';
  onResetMode: () => void;
  onOpenShip30: () => void;
  onOpenKnowledge: () => void;
  errorMessage: string | null;
  onClearError: () => void;
  onOpenArtifact: () => void;
  hasArtifacts: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSendMessage,
  activeMode,
  onOpenShip30,
  onOpenKnowledge,
  errorMessage,
  onClearError,
  onOpenArtifact,
  hasArtifacts,
}) => {
  const [inputText, setInputText] = useState('');
  const [thinkActive, setThinkActive] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="chat-panel">
      {/* Scrollable conversation stream */}
      <div className="chat-scroll-container" ref={scrollRef}>
        {!hasMessages ? (
          /* Professional Monochrome Hero Empty State */
          <div className="hero-empty-state">
            <div className="hero-logo-wrapper">
              <Logo size={48} />
            </div>

            <h1 className="hero-title">Where should we begin?</h1>
            <p className="hero-subtitle">
              Tactical growth frameworks, retention loops, and Ship 30 essays strictly grounded in Lenny's Podcast archive.
            </p>

            {/* Central Animated Input Bar */}
            <div className="input-card-container">
              <div className="input-textarea-row">
                <button
                  className="icon-circle-btn"
                  title="Ship 30 for 30 Essay Studio"
                  onClick={onOpenShip30}
                >
                  <Plus size={17} />
                </button>

                <textarea
                  id="hero-chat-input"
                  className="main-chat-input"
                  placeholder={
                    activeMode === 'ship30'
                      ? 'Enter topic for Ship 30 for 30 essay...'
                      : 'Ask about retention, growth loops, or frameworks...'
                  }
                  rows={1}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  autoFocus
                />

                <div className="input-actions-right">
                  <button
                    id="hero-think-btn"
                    className={`think-toggle-pill ${thinkActive ? 'active' : ''}`}
                    onClick={() => setThinkActive(!thinkActive)}
                    title="Deep Reasoning Mode"
                  >
                    <span>Think</span>
                  </button>

                  <button
                    id="hero-send-btn"
                    className={`send-arrow-btn ${inputText.trim() && !isLoading ? 'ready' : ''}`}
                    onClick={handleSend}
                    disabled={!inputText.trim() || isLoading}
                    title="Send message"
                  >
                    <ArrowUp size={16} />
                  </button>
                </div>
              </div>
            </div>

            {/* Curated Monochrome Suggestion Chips */}
            <div className="prompt-suggestions-grid">
              <button
                id="chip-elena"
                className="prompt-chip"
                onClick={() => onSendMessage('What does Elena Verna say about growth tactics that never work?')}
              >
                <div className="prompt-chip-icon">
                  <Sparkles size={14} />
                </div>
                <div className="prompt-chip-content">
                  <span className="prompt-chip-title">Growth tactics that never work</span>
                  <span className="prompt-chip-desc">Elena Verna's empirical critique</span>
                </div>
              </button>

              <button
                id="chip-retention"
                className="prompt-chip"
                onClick={() => onSendMessage('What is the fundamental law of retention according to Casey Winters and Elena Verna?')}
              >
                <div className="prompt-chip-icon">
                  <Compass size={14} />
                </div>
                <div className="prompt-chip-content">
                  <span className="prompt-chip-title">Fundamental law of retention</span>
                  <span className="prompt-chip-desc">Activation milestones & habit loops</span>
                </div>
              </button>

              <button
                id="chip-ship30"
                className="prompt-chip"
                onClick={onOpenShip30}
              >
                <div className="prompt-chip-icon">
                  <Feather size={14} />
                </div>
                <div className="prompt-chip-content">
                  <span className="prompt-chip-title">Ship 30 for 30 Essay Studio</span>
                  <span className="prompt-chip-desc">Generate grounded 1,250-word tactical essay</span>
                </div>
              </button>

              <button
                id="chip-knowledge"
                className="prompt-chip"
                onClick={onOpenKnowledge}
              >
                <div className="prompt-chip-icon">
                  <Globe size={14} />
                </div>
                <div className="prompt-chip-content">
                  <span className="prompt-chip-title">Inspect Knowledge Base</span>
                  <span className="prompt-chip-desc">Authoritative ChatPRD podcast archive</span>
                </div>
              </button>
            </div>
          </div>
        ) : (
          /* Active Message Stream */
          <div className="messages-stream-wrapper">
            {messages.map((m, idx) => (
              <ChatMessage
                key={m.id || idx}
                message={m}
                hasArtifact={hasArtifacts && idx === messages.length - 1}
                onOpenArtifact={onOpenArtifact}
              />
            ))}

            {isLoading && (
              <div className="message-row assistant">
                <div className="thinking-indicator">
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                  <span className="thinking-text">Synthesizing grounded evidence from transcripts...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Error Alert Banner */}
      {errorMessage && (
        <div className="error-toast-banner">
          <div className="error-toast-content">
            <AlertCircle size={15} />
            <span>{errorMessage}</span>
          </div>
          <button className="icon-btn-subtle" onClick={onClearError}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Bottom Pinned Input Bar when Chat has Messages */}
      {hasMessages && (
        <div className="chat-bottom-dock">
          <div className="input-card-container">
            <div className="input-textarea-row">
              <button
                className="icon-circle-btn"
                title="Ship 30 for 30 Essay Studio"
                onClick={onOpenShip30}
              >
                <Plus size={17} />
              </button>

              <textarea
                id="chat-input"
                className="main-chat-input"
                placeholder={
                  activeMode === 'ship30'
                    ? 'Enter topic for Ship 30 for 30 essay...'
                    : 'Ask The Lenny Growth Assistant...'
                }
                rows={1}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                autoFocus
              />

              <div className="input-actions-right">
                <button
                  id="chat-think-btn"
                  className={`think-toggle-pill ${thinkActive ? 'active' : ''}`}
                  onClick={() => setThinkActive(!thinkActive)}
                  title="Deep Reasoning Mode"
                >
                  <span>Think</span>
                </button>

                <button
                  id="send-btn"
                  className={`send-arrow-btn ${inputText.trim() && !isLoading ? 'ready' : ''}`}
                  onClick={handleSend}
                  disabled={!inputText.trim() || isLoading}
                  title="Send message"
                >
                  <ArrowUp size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
