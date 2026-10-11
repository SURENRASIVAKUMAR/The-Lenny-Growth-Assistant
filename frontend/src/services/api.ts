import type {
  Session,
  Message,
  Artifact,
  KnowledgeSource,
  ConfigStatus,
  ChatResponsePayload,
  Ship30Config,
} from '../types';

const BASE_URL = '/api';

export async function fetchConfigStatus(): Promise<ConfigStatus> {
  const res = await fetch(`${BASE_URL}/config/status`);
  if (!res.ok) throw new Error(`Failed to fetch config status: ${res.statusText}`);
  return res.json();
}

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch(`${BASE_URL}/sessions`);
  if (!res.ok) throw new Error(`Failed to fetch sessions: ${res.statusText}`);
  return res.json();
}

export async function createSession(title?: string): Promise<Session> {
  const res = await fetch(`${BASE_URL}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: title || 'New Conversation' }),
  });
  if (!res.ok) throw new Error(`Failed to create session: ${res.statusText}`);
  return res.json();
}

export async function renameSession(sessionId: string, title: string): Promise<Session> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`Failed to rename session: ${res.statusText}`);
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete session: ${res.statusText}`);
}

export async function fetchMessages(sessionId: string): Promise<Message[]> {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/messages`);
  if (!res.ok) throw new Error(`Failed to fetch messages: ${res.statusText}`);
  return res.json();
}

export async function sendChatMessage(params: {
  sessionId?: string;
  message: string;
  mode?: 'standard' | 'ship30';
  ship30Params?: Partial<Ship30Config>;
  provider?: string;
  model?: string;
}): Promise<ChatResponsePayload> {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: params.sessionId,
      message: params.message,
      mode: params.mode || 'standard',
      ship30_params: params.ship30Params,
      provider: params.provider,
      model: params.model,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat request failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchArtifacts(sessionId?: string): Promise<Artifact[]> {
  const url = sessionId ? `${BASE_URL}/artifacts?session_id=${sessionId}` : `${BASE_URL}/artifacts`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch artifacts: ${res.statusText}`);
  return res.json();
}

export async function fetchArtifact(artifactId: string): Promise<Artifact> {
  const res = await fetch(`${BASE_URL}/artifacts/${artifactId}`);
  if (!res.ok) throw new Error(`Failed to fetch artifact: ${res.statusText}`);
  return res.json();
}

export async function updateArtifact(
  artifactId: string,
  payload: { title?: string; content?: string }
): Promise<Artifact> {
  const res = await fetch(`${BASE_URL}/artifacts/${artifactId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to update artifact: ${res.statusText}`);
  return res.json();
}

export async function deleteArtifact(artifactId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/artifacts/${artifactId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete artifact: ${res.statusText}`);
}

export async function fetchKnowledgeSources(): Promise<KnowledgeSource[]> {
  const res = await fetch(`${BASE_URL}/knowledge/sources`);
  if (!res.ok) throw new Error(`Failed to fetch knowledge sources: ${res.statusText}`);
  return res.json();
}

export async function ingestDocument(payload: {
  title: string;
  content: string;
  source_type?: string;
  url?: string;
  author_or_guest?: string;
  summary?: string;
}): Promise<any> {
  const res = await fetch(`${BASE_URL}/knowledge/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to ingest document');
  }
  return res.json();
}

export async function refreshKnowledge(): Promise<any> {
  const res = await fetch(`${BASE_URL}/knowledge/refresh`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to refresh knowledge base');
  return res.json();
}
