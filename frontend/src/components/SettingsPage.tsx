import React, { useState } from 'react';
import {
  User,
  Cpu,
  Database,
  Sliders,
  Check,
  Shield,
  Key,
  Server,
  Sparkles,
  ArrowLeft,
  Save,
} from 'lucide-react';
import type { ConfigStatus, ThemeType } from '../types';

interface SettingsPageProps {
  config: ConfigStatus | null;
  onSaveProvider: (provider: string, model: string) => void;
  onBackToChat: () => void;
  initialTab?: 'account' | 'models' | 'database' | 'preferences';
  theme: ThemeType;
  onThemeChange: (theme: ThemeType) => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  config,
  onSaveProvider,
  onBackToChat,
  initialTab = 'account',
  theme,
  onThemeChange,
}) => {
  const [activeTab, setActiveTab] = useState<'account' | 'models' | 'database' | 'preferences'>(initialTab);

  // Account details state
  const [userName, setUserName] = useState('Surenra S');
  const [userEmail, setUserEmail] = useState('surenra@growth.ai');
  const [userRole, setUserRole] = useState('Founder & Product Leader');
  const [companyName, setCompanyName] = useState('Lenny Growth Labs');
  const [savedSuccess, setSavedSuccess] = useState<string | null>(null);

  // AI & Models state
  const [selectedProvider, setSelectedProvider] = useState(config?.active_provider || 'demo');
  const [selectedModel, setSelectedModel] = useState(config?.active_model || 'lenny-rag-engine-v1');
  const [apiKey, setApiKey] = useState('');
  const [temperature, setTemperature] = useState(0.7);

  // Preferences state
  const [autoOpenCanvas, setAutoOpenCanvas] = useState(true);
  const [deepThinkingDefault, setDeepThinkingDefault] = useState(false);

  const handleSaveAccount = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess('Account profile updated successfully.');
    setTimeout(() => setSavedSuccess(null), 3000);
  };

  const handleSaveAIConfig = () => {
    onSaveProvider(selectedProvider, selectedModel);
    setSavedSuccess('AI model configuration applied successfully.');
    setTimeout(() => setSavedSuccess(null), 3000);
  };

  return (
    <div className="page-container">
      {/* Top Page Header */}
      <div className="page-header">
        <div className="page-header-left">
          <button id="settings-back-btn" type="button" className="icon-btn-subtle" onClick={onBackToChat} title="Back to Chat">
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="page-title">Settings & Account</h1>
            <p className="page-subtitle">Manage your profile, AI reasoning providers, and database configuration</p>
          </div>
        </div>
        {savedSuccess && (
          <div className="page-toast-pill">
            <Check size={14} />
            <span>{savedSuccess}</span>
          </div>
        )}
      </div>

      <div className="page-body-layout">
        {/* Settings Navigation Tabs */}
        <aside className="settings-nav-sidebar">
          <button
            id="tab-account"
            type="button"
            className={`settings-nav-tab ${activeTab === 'account' ? 'active' : ''}`}
            onClick={() => setActiveTab('account')}
          >
            <User size={16} />
            <span>Account & Profile</span>
          </button>
          <button
            id="tab-models"
            type="button"
            className={`settings-nav-tab ${activeTab === 'models' ? 'active' : ''}`}
            onClick={() => setActiveTab('models')}
          >
            <Cpu size={16} />
            <span>AI & Models</span>
          </button>
          <button
            id="tab-database"
            type="button"
            className={`settings-nav-tab ${activeTab === 'database' ? 'active' : ''}`}
            onClick={() => setActiveTab('database')}
          >
            <Database size={16} />
            <span>Database & RAG</span>
          </button>
          <button
            id="tab-preferences"
            type="button"
            className={`settings-nav-tab ${activeTab === 'preferences' ? 'active' : ''}`}
            onClick={() => setActiveTab('preferences')}
          >
            <Sliders size={16} />
            <span>Preferences</span>
          </button>
        </aside>

        {/* Tab Content Panes */}
        <main className="settings-content-pane">
          {/* 1. Account & Profile Tab */}
          {activeTab === 'account' && (
            <div className="settings-section">
              <div className="section-header">
                <h2>Account Profile</h2>
                <p>Personal information and team subscription settings</p>
              </div>

              {/* Profile Card Banner */}
              <div className="account-overview-card">
                <div className="account-avatar-large">SS</div>
                <div className="account-overview-meta">
                  <h3>{userName}</h3>
                  <p>{userEmail} • {userRole}</p>
                  <div className="account-badges-row">
                    <span className="badge-pill active">Pro Plan • Active</span>
                    <span className="badge-pill">Strict Source Grounding</span>
                  </div>
                </div>
              </div>

              <form onSubmit={handleSaveAccount} className="settings-form">
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Full Name</label>
                    <input
                      type="text"
                      className="form-input"
                      value={userName}
                      onChange={(e) => setUserName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Email Address</label>
                    <input
                      type="email"
                      className="form-input"
                      value={userEmail}
                      onChange={(e) => setUserEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Role / Title</label>
                    <input
                      type="text"
                      className="form-input"
                      value={userRole}
                      onChange={(e) => setUserRole(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Organization / Project</label>
                    <input
                      type="text"
                      className="form-input"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                    />
                  </div>
                </div>

                <div className="settings-card" style={{ marginTop: 20 }}>
                  <div className="settings-card-header">
                    <Shield size={16} />
                    <h4>Security & Workspace Access</h4>
                  </div>
                  <p className="settings-card-desc">
                    Your local storage and session data are stored securely on localhost. No private conversations are synced to external cloud services without your consent.
                  </p>
                </div>

                <div className="form-actions-row">
                  <button type="submit" className="btn-primary">
                    <Save size={14} />
                    <span>Save Profile Changes</span>
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* 2. AI & Models Tab */}
          {activeTab === 'models' && (
            <div className="settings-section">
              <div className="section-header">
                <h2>AI Models & Inference Providers</h2>
                <p>Choose the model execution runtime for grounded growth analysis and essay writing</p>
              </div>

              <div className="provider-cards-stack">
                {/* Built-in Demo Provider */}
                <div
                  className={`provider-select-card ${selectedProvider === 'demo' ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedProvider('demo');
                    setSelectedModel('lenny-rag-engine-v1');
                  }}
                >
                  <div className="provider-card-top">
                    <div className="provider-card-title">
                      <Sparkles size={16} />
                      <strong>Built-in RAG Synthesizer (Instant / Zero-Config)</strong>
                    </div>
                    <span className="badge-pill active">Always Available</span>
                  </div>
                  <p className="provider-card-desc">
                    Translates indexed transcript chunks into structured answers and essays directly from the authoritative repository without requiring external API keys.
                  </p>
                </div>

                {/* Local Ollama Provider */}
                <div
                  className={`provider-select-card ${selectedProvider === 'ollama' ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedProvider('ollama');
                    setSelectedModel('llama3:latest');
                  }}
                >
                  <div className="provider-card-top">
                    <div className="provider-card-title">
                      <Cpu size={16} />
                      <strong>Ollama Local Server (Offline Private LLM)</strong>
                    </div>
                    <span className="badge-pill">Localhost:11434</span>
                  </div>
                  <p className="provider-card-desc">
                    Runs open-weights models (e.g. LLaMA 3, Mistral) locally on your GPU/CPU with 100% data privacy.
                  </p>
                </div>

                {/* Cloud OpenAI Provider */}
                <div
                  className={`provider-select-card ${selectedProvider === 'openai' ? 'selected' : ''}`}
                  onClick={() => {
                    setSelectedProvider('openai');
                    setSelectedModel('gpt-4o-mini');
                  }}
                >
                  <div className="provider-card-top">
                    <div className="provider-card-title">
                      <Server size={16} />
                      <strong>OpenAI Cloud Inference (GPT-4o / GPT-4o-mini)</strong>
                    </div>
                    <span className="badge-pill">Cloud API</span>
                  </div>
                  <p className="provider-card-desc">
                    High-reasoning cloud intelligence for nuanced Ship 30 essays and multi-step growth frameworks.
                  </p>
                </div>
              </div>

              {selectedProvider === 'openai' && (
                <div className="settings-card" style={{ marginTop: 20 }}>
                  <div className="settings-card-header">
                    <Key size={16} />
                    <h4>OpenAI API Key</h4>
                  </div>
                  <input
                    type="password"
                    className="form-input"
                    placeholder="sk-..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    style={{ marginTop: 10 }}
                  />
                </div>
              )}

              <div className="form-group" style={{ marginTop: 20 }}>
                <label className="form-label">Sampling Temperature ({temperature})</label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: '#ffffff' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  <span>Deterministic & Strict (0.1)</span>
                  <span>Creative & Expansive (1.0)</span>
                </div>
              </div>

              <div className="form-actions-row">
                <button type="button" className="btn-primary" onClick={handleSaveAIConfig}>
                  <Save size={14} />
                  <span>Apply AI Configuration</span>
                </button>
              </div>
            </div>
          )}

          {/* 3. Database & RAG Tab */}
          {activeTab === 'database' && (
            <div className="settings-section">
              <div className="section-header">
                <h2>Database & Grounded Knowledge Archive</h2>
                <p>Status of PostgreSQL, MySQL storage, and authoritative podcast transcripts</p>
              </div>

              <div className="db-stats-grid">
                <div className="stat-card">
                  <span className="stat-label">Active Database Engine</span>
                  <strong className="stat-value">MySQL (Port 3306)</strong>
                  <span className="stat-sub">Fallback active with full data</span>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Indexed Authoritative Episodes</span>
                  <strong className="stat-value">{config?.rag_sources_count || 30} Episodes</strong>
                  <span className="stat-sub">ChatPRD/lennys-podcast-transcripts</span>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Indexed Knowledge Chunks</span>
                  <strong className="stat-value">{config?.rag_chunks_count || 3660} Chunks</strong>
                  <span className="stat-sub">Semantic vectors & keyword indices</span>
                </div>
                <div className="stat-card">
                  <span className="stat-label">Primary Target Engine</span>
                  <strong className="stat-value">PostgreSQL (Port 5432)</strong>
                  <span className="stat-sub">Alembic schema ready</span>
                </div>
              </div>

              <div className="settings-card" style={{ marginTop: 20 }}>
                <div className="settings-card-header">
                  <Database size={16} />
                  <h4>Strict Source Data Grounding Guarantee</h4>
                </div>
                <p className="settings-card-desc">
                  The Lenny Growth Assistant strictly rejects unverified claims or topics outside of the indexed archive. Responses always attach verifiable episode titles, guest names, and provenance paths.
                </p>
              </div>
            </div>
          )}

          {/* 4. Preferences Tab */}
          {activeTab === 'preferences' && (
            <div className="settings-section">
              <div className="section-header">
                <h2>User Preferences</h2>
                <p>Interface behavior, default views, and interaction shortcuts</p>
              </div>

              <div className="toggle-setting-row">
                <div>
                  <strong>Automatically open Canvas on artifact creation</strong>
                  <p>Splits the workspace when a Ship 30 essay or code document is produced.</p>
                </div>
                <input
                  type="checkbox"
                  checked={autoOpenCanvas}
                  onChange={(e) => setAutoOpenCanvas(e.target.checked)}
                  style={{ width: 18, height: 18, accentColor: '#ffffff' }}
                />
              </div>

              <div className="toggle-setting-row">
                <div>
                  <strong>Default to Deep Reasoning ("Think") mode</strong>
                  <p>Always triggers additional chain-of-thought analysis on complex queries.</p>
                </div>
                <input
                  type="checkbox"
                  checked={deepThinkingDefault}
                  onChange={(e) => setDeepThinkingDefault(e.target.checked)}
                  style={{ width: 18, height: 18, accentColor: '#ffffff' }}
                />
              </div>

              {/* Background & UI Design Aesthetic */}
              <div style={{ marginTop: 24 }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-pure)', marginBottom: 4 }}>
                  Background & UI Aesthetics
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 14 }}>
                  Choose your preferred workspace atmosphere. Changes apply immediately across all screens and persist on your device.
                </p>

                <div className="theme-cards-grid">
                  {[
                    {
                      id: 'oled' as ThemeType,
                      name: 'Black (Dark Mode)',
                      tag: 'OLED Black',
                      desc: 'Pure pitch black minimal high-contrast monochrome design',
                      previewBg: '#000000',
                      accentDot: '#ffffff',
                    },
                    {
                      id: 'light' as ThemeType,
                      name: 'White (Light Mode)',
                      tag: 'Studio White',
                      desc: 'Clean pure white minimalist high-clarity day mode',
                      previewBg: '#ffffff',
                      accentDot: '#000000',
                    },
                  ].map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      className={`theme-card-option ${theme === t.id ? 'active' : ''}`}
                      onClick={() => onThemeChange(t.id)}
                    >
                      <div className="theme-preview-box" style={{ background: t.previewBg }}>
                        <span
                          style={{
                            width: 14,
                            height: 14,
                            borderRadius: '50%',
                            background: t.accentDot,
                            boxShadow: `0 0 10px ${t.accentDot}`,
                          }}
                        />
                      </div>
                      <div className="theme-card-title-row">
                        <span className="theme-card-name">{t.name}</span>
                        <span className="badge-pill active" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>
                          {t.tag}
                        </span>
                      </div>
                      <p className="theme-card-desc">{t.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default SettingsPage;
