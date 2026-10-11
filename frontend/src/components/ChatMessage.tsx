import React, { useState } from 'react';
import { User, BookOpen, ExternalLink, ChevronDown, ChevronUp, FileCode } from 'lucide-react';
import type { Message, Citation } from '../types';
import { Logo } from './Logo';

interface ChatMessageProps {
  message: Message;
  onOpenArtifact?: () => void;
  hasArtifact?: boolean;
}

function renderFormattedText(text: string) {
  const lines = text.split('\n');
  return lines.map((line, idx) => {
    if (line.startsWith('### ')) {
      return <h3 key={idx} className="md-h3">{line.substring(4)}</h3>;
    }
    if (line.startsWith('## ')) {
      return <h2 key={idx} className="md-h2">{line.substring(3)}</h2>;
    }
    if (line.startsWith('# ')) {
      return <h1 key={idx} className="md-h1">{line.substring(2)}</h1>;
    }
    if (line.startsWith('- ') || line.startsWith('* ')) {
      return (
        <li key={idx} className="md-li">
          {formatInline(line.substring(2))}
        </li>
      );
    }
    if (!line.trim()) {
      return <div key={idx} style={{ height: 10 }} />;
    }
    return <p key={idx} className="md-p">{formatInline(line)}</p>;
  });
}

function formatInline(str: string): React.ReactNode {
  const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="md-bold">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} className="md-code">{part.slice(1, -1)}</code>;
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
        {isUser ? <User size={16} /> : <Logo size={20} />}
      </div>

      <div className="message-bubble">
        <div className="markdown-body">
          {renderFormattedText(message.content)}
        </div>

        {hasArtifact && onOpenArtifact && (
          <div style={{ marginTop: 14 }}>
            <button
              className="open-canvas-action-btn"
              onClick={onOpenArtifact}
            >
              <FileCode size={14} />
              <span>Inspect Generated Artifact in Canvas</span>
            </button>
          </div>
        )}

        {citations.length > 0 && (
          <div className="citations-container">
            <button
              className="citations-toggle-btn"
              onClick={() => setShowSources(!showSources)}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <BookOpen size={13} />
                <span>Authoritative Transcript Sources ({citations.length})</span>
              </span>
              {showSources ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
            </button>

            {showSources && (
              <div className="citation-cards-grid">
                {citations.map((c, i) => (
                  <div key={i} className="citation-card-item">
                    <div className="citation-header-row">
                      <span className="citation-source-name">{c.source_title}</span>
                      {c.url && (
                        <a
                          href={c.url}
                          target="_blank"
                          rel="noreferrer"
                          className="citation-link"
                          title="Open YouTube interview"
                        >
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                    {c.author_or_guest && (
                      <div className="citation-guest-name">Guest: {c.author_or_guest}</div>
                    )}
                    {c.provenance_file && (
                      <div className="citation-file-badge">File: {c.provenance_file}</div>
                    )}
                    <div className="citation-excerpt">"{c.snippet}"</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {!isUser && (
          <div className="message-meta-footer">
            <span>{new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        )}
      </div>
    </div>
  );
};
