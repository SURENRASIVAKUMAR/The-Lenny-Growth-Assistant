import React, { useState } from 'react';
import { User, Bot, BookOpen, ExternalLink, ChevronDown, ChevronUp, FileCode } from 'lucide-react';
import type { Message, Citation } from '../types';

interface ChatMessageProps {
  message: Message;
  onOpenArtifact?: () => void;
  hasArtifact?: boolean;
}

function renderFormattedText(text: string) {
  const lines = text.split('\n');
  return lines.map((line, idx) => {
    if (line.startsWith('### ')) {
      return <h3 key={idx}>{line.substring(4)}</h3>;
    }
    if (line.startsWith('## ')) {
      return <h2 key={idx}>{line.substring(3)}</h2>;
    }
    if (line.startsWith('# ')) {
      return <h1 key={idx}>{line.substring(2)}</h1>;
    }
    if (line.startsWith('- ') || line.startsWith('* ')) {
      return (
        <li key={idx} style={{ marginLeft: 20 }}>
          {formatInline(line.substring(2))}
        </li>
      );
    }
    if (!line.trim()) {
      return <div key={idx} style={{ height: 10 }} />;
    }
    return <p key={idx}>{formatInline(line)}</p>;
  });
}

function formatInline(str: string): React.ReactNode {
  const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onOpenArtifact,
  hasArtifact,
}) => {
  const isUser = message.role === 'user';
  const [showSources, setShowSources] = useState(false);
  const citations: Citation[] = message.citations || [];

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div className="message-bubble">
        <div className="markdown-body">
          {renderFormattedText(message.content)}
        </div>

        {hasArtifact && onOpenArtifact && (
          <div style={{ marginTop: 12 }}>
            <button
              className="btn-secondary"
              style={{
                background: 'rgba(99, 102, 241, 0.15)',
                borderColor: 'var(--accent-primary)',
                color: '#c7d2fe',
              }}
              onClick={onOpenArtifact}
            >
              <FileCode size={14} />
              <span>Open Generated Artifact in Viewer</span>
            </button>
          </div>
        )}

        {citations.length > 0 && (
          <div className="citations-container">
            <button
              className="icon-btn-subtle"
              style={{
                width: '100%',
                justifyContent: 'space-between',
                padding: '4px 6px',
                color: '#a5b4fc',
                fontWeight: 600,
                fontSize: '0.78rem',
              }}
              onClick={() => setShowSources(!showSources)}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <BookOpen size={14} />
                <span>Grounded Sources & Citations ({citations.length})</span>
              </span>
              {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showSources && (
              <div className="citation-cards" style={{ marginTop: 8 }}>
                {citations.map((c, i) => (
                  <div key={i} className="citation-card">
                    <div className="citation-title">
                      <span>{c.source_title}</span>
                      {c.url && (
                        <a
                          href={c.url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: '#818cf8', display: 'flex', alignItems: 'center' }}
                        >
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                    {c.author_or_guest && (
                      <div className="citation-author">Guest / Author: {c.author_or_guest}</div>
                    )}
                    <div className="citation-snippet">"{c.snippet}"</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {!isUser && (
          <div className="message-meta">
            {message.provider_used && (
              <span className="badge-tag">
                {message.provider_used}: {message.model_used || 'default'}
              </span>
            )}
            <span>{new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        )}
      </div>
    </div>
  );
};
