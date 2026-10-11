import React, { useState } from 'react';
import { Copy, Download, Check, X, Code, Eye, FileText, Globe } from 'lucide-react';
import type { Artifact } from '../types';

interface ArtifactViewerProps {
  artifacts: Artifact[];
  activeArtifactId: string | null;
  onSelectArtifact: (id: string) => void;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifacts,
  activeArtifactId,
  onSelectArtifact,
  onClose,
}) => {
  const [viewTab, setViewTab] = useState<'preview' | 'source'>('preview');
  const [copied, setCopied] = useState(false);

  const activeArtifact =
    artifacts.find((a) => a.id === activeArtifactId) || artifacts[0] || null;

  if (!activeArtifact) {
    return (
      <div className="artifact-panel">
        <div className="artifact-panel-header">
          <span style={{ fontWeight: 600 }}>Artifact Viewer</span>
          <button className="icon-btn-subtle" onClick={onClose}>
            <X size={16} />
          </button>
        </div>
        <div style={{ padding: 30, textAlign: 'center', color: 'var(--text-muted)' }}>
          No artifacts generated yet. Ask the assistant to write an essay or create a page to view it here.
        </div>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(activeArtifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = activeArtifact.artifact_type === 'html' ? 'html' : 'md';
    const blob = new Blob([activeArtifact.content], {
      type: activeArtifact.artifact_type === 'html' ? 'text/html' : 'text/markdown',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeArtifact.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const isHtml = activeArtifact.artifact_type === 'html';

  return (
    <aside className="artifact-panel">
      {/* Header */}
      <div className="artifact-panel-header">
        <div className="artifact-title-group">
          {isHtml ? <Globe size={16} color="#818cf8" /> : <FileText size={16} color="#818cf8" />}
          
          {artifacts.length > 1 ? (
            <select
              className="form-select"
              style={{ width: 'auto', padding: '4px 8px', fontSize: '0.82rem', height: 28 }}
              value={activeArtifact.id}
              onChange={(e) => onSelectArtifact(e.target.value)}
            >
              {artifacts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.title} ({a.artifact_type.toUpperCase()})
                </option>
              ))}
            </select>
          ) : (
            <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>
              {activeArtifact.title}
            </span>
          )}

          <span className="badge-tag" style={{ textTransform: 'uppercase' }}>
            {activeArtifact.artifact_type}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Tabs: Preview vs Source */}
          <div className="artifact-panel-tabs">
            <button
              className={`artifact-tab ${viewTab === 'preview' ? 'active' : ''}`}
              onClick={() => setViewTab('preview')}
            >
              <Eye size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
              Preview
            </button>
            <button
              className={`artifact-tab ${viewTab === 'source' ? 'active' : ''}`}
              onClick={() => setViewTab('source')}
            >
              <Code size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
              Source
            </button>
          </div>

          {/* Copy Button */}
          <button
            className="icon-btn-subtle"
            onClick={handleCopy}
            title={copied ? 'Copied to clipboard!' : 'Copy raw content'}
          >
            {copied ? <Check size={15} color="#10b981" /> : <Copy size={15} />}
          </button>

          {/* Download Button */}
          <button
            className="icon-btn-subtle"
            onClick={handleDownload}
            title="Download file"
          >
            <Download size={15} />
          </button>

          {/* Close Panel */}
          <button className="icon-btn-subtle" onClick={onClose} title="Close Artifact Viewer">
            <X size={15} />
          </button>
        </div>
      </div>

      {/* Artifact Content Body */}
      <div className="artifact-content-body">
        {viewTab === 'preview' ? (
          isHtml ? (
            <iframe
              className="artifact-iframe-sandbox"
              srcDoc={activeArtifact.content}
              sandbox="allow-scripts"
              title={activeArtifact.title}
            />
          ) : (
            <div className="markdown-body">
              {activeArtifact.content.split('\n').map((line, idx) => {
                if (line.startsWith('# ')) return <h1 key={idx}>{line.substring(2)}</h1>;
                if (line.startsWith('## ')) return <h2 key={idx}>{line.substring(3)}</h2>;
                if (line.startsWith('### ')) return <h3 key={idx}>{line.substring(4)}</h3>;
                if (line.startsWith('- ') || line.startsWith('* ')) {
                  return <li key={idx} style={{ marginLeft: 20 }}>{line.substring(2)}</li>;
                }
                if (!line.trim()) return <div key={idx} style={{ height: 12 }} />;
                return <p key={idx}>{line}</p>;
              })}
            </div>
          )
        ) : (
          <pre
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.84rem',
              color: '#cbd5e1',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
              lineHeight: 1.6,
            }}
          >
            {activeArtifact.content}
          </pre>
        )}
      </div>
    </aside>
  );
};
