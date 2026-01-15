export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  steps?: StepInfo[];
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

export type StepStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface StepInfo {
  id: string;
  description: string;
  status: StepStatus;
  details?: string;
}

export interface PlanEvent {
  type: 'plan';
  steps: StepInfo[];
}

export interface StatusEvent {
  type: 'status';
  step_id: string;
  status: StepStatus;
  details?: string;
}

export interface MessageEvent {
  type: 'message';
  content: string;
  is_final: boolean;
}

export interface ErrorEvent {
  type: 'error';
  error: string;
}

export type StreamEvent = PlanEvent | StatusEvent | MessageEvent | ErrorEvent;
