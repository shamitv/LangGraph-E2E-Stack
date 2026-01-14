export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  agent_type?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  agent_type: string;
  metadata?: Record<string, any>;
}

export interface Agent {
  name: string;
  description: string;
}
