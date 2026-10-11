import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Feather, AlertCircle, X } from 'lucide-react';
import type { Message } from '../types';
import { ChatMessage } from './ChatMessage';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  activeMode: 'standard' | 'ship30';
  onResetMode: () => void;
  errorMessage: string | null;
  onClearError: () => void;
  onOpenArtifact: () => void;
  hasArtifacts: boolean;
}

const EXAMPLE_PROMPTS = [
  {
    title: 'Retention & Activation',
    prompt: 'How do I diagnose retention issues and find our core activation milestone before scaling acquisition?',
  },
  {
    title: 'Product-Market Fit',
    prompt: "What is Rahul Vohra's Sean Ellis survey benchmark for Product-Market Fit and how do the Four Fits work?",
  },
  {
    title: 'SaaS Pricing & Packaging',
    prompt: 'How should B2B SaaS companies choose their core value metric and avoid the per-seat pricing trap?',
  },
  {
    title: 'PM Team Archetypes',
    prompt: 'What are the three product manager archetypes outlined by Shreyas Doshi, and how should teams hire for them?',
  },
];

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onSendMessage,
  activeMode,
  onResetMode,
  errorMessage,
  onClearError,
  onOpenArtifact,
  hasArtifacts,
}) => {
  const [inputText, setInputText] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages or loading state changes
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

  return (
    <div className="chat-panel">
      {/* Scrollable message stream */}
      <div className="chat-scroll-container" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <Sparkles size={28} color="#fff" />
            </div>
            <h2>The Lenny Growth Assistant</h2>
            <p>
              Ask questions grounded in Lenny's podcast transcripts and newsletter deep dives, or generate high-impact essays with the Ship 30 for 30 writing skill.
            </p>

            <div className="example-grid">
              {EXAMPLE_PROMPTS.map((ex, i) => (
                <div
                  key={i}
                  className="example-card"
                  onClick={() => onSendMessage(ex.prompt)}
                >
                  <strong style={{ display: 'block', color: 'var(--text-main)', marginBottom: 4 }}>
                    {ex.title}
                  </strong>
                  <span>{ex.prompt}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, idx) => (
            <ChatMessage
              key={m.id || idx}
              message={m}
              hasArtifact={hasArtifacts && idx === messages.length - 1}
              onOpenArtifact={onOpenArtifact}
            />
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="message-row assistant">
            <div className="avatar assistant">
              <Sparkles size={18} />
            </div>
            <div className="message-bubble" style={{ color: 'var(--text-muted)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span className="status-dot active" style={{ animation: 'pulse 1.2s infinite' }} />
                <span>Searching knowledge base and formulating grounded answer...</span>
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div
          style={{
            margin: '0 24px 8px 24px',
            padding: '10px 14px',
            backgroundColor: 'var(--error-bg)',
            border: '1px solid var(--error)',
            borderRadius: 'var(--radius-md)',
            color: '#fca5a5',
            fontSize: '0.84rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertCircle size={16} color="#ef4444" />
            <span>{errorMessage}</span>
          </div>
          <button className="icon-btn-subtle" onClick={onClearError} title="Dismiss">
            <X size={14} />
          </button>
        </div>
      )}

      {/* Input Form Bar */}
      <div className="chat-input-area">
        <div className="input-box-wrapper">
          <textarea
            className="chat-textarea"
            placeholder={
              activeMode === 'ship30'
                ? 'Enter topic or prompt for Ship 30 for 30 essay (e.g. "Why activation metrics fail in B2B SaaS")...'
                : "Ask about product strategy, retention, PMF, hiring, or Lenny's guests (Shift+Enter for new line)..."
            }
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />

          <div className="input-toolbar">
            <div className="mode-badge-indicator">
              {activeMode === 'ship30' ? (
                <span
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    background: 'rgba(245, 158, 11, 0.2)',
                    color: '#fbbf24',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-full)',
                    fontWeight: 600,
                  }}
                >
                  <Feather size={12} />
                  <span>Ship 30 for 30 Mode</span>
                  <button
                    type="button"
                    style={{ background: 'none', border: 'none', color: '#fbbf24', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                    onClick={onResetMode}
                    title="Switch back to Standard Mode"
                  >
                    <X size={12} />
                  </button>
                </span>
              ) : (
                <span>Grounded with Lenny Knowledge Base</span>
              )}
            </div>

            <button
              className="send-btn"
              onClick={handleSend}
              disabled={!inputText.trim() || isLoading}
            >
              <Send size={14} />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
