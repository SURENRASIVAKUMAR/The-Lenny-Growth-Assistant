export interface Citation {
  source_id: string;
  source_title: string;
  chunk_id: string;
  url?: string | null;
  author_or_guest?: string | null;
  snippet: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model_used?: string | null;
  provider_used?: string | null;
  citations?: Citation[];
  created_at: string;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface Artifact {
  id: string;
  session_id?: string | null;
  title: string;
  artifact_type: 'markdown' | 'html' | 'essay' | 'code';
  content: string;
  metadata_json?: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeSource {
  id: string;
  title: string;
  source_type: string;
  url?: string | null;
  author_or_guest?: string | null;
  summary?: string | null;
  status: string;
  error_message?: string | null;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConfigStatus {
  active_provider: string;
  active_model: string;
  openai_configured: boolean;
  openai_model: string;
  ollama_base_url: string;
  ollama_model: string;
  ollama_available: boolean;
  database_status: string;
  database_name: string;
  rag_sources_count: number;
  rag_chunks_count: number;
}

export interface Ship30Config {
  topic: string;
  audience: string;
  tone: string;
  target_length: number;
}

export interface ChatResponsePayload {
  session_id: string;
  message: Message;
  citations: Citation[];
  artifact?: Artifact | null;
  provider_used: string;
  model_used: string;
  rag_used: boolean;
  warning?: string | null;
}
