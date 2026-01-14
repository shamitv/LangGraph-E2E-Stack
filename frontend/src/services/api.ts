import axios from 'axios';
import { ChatRequest, ChatResponse, Agent } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat/chat', request);
    return response.data;
  },

  listAgents: async (): Promise<Record<string, Agent>> => {
    const response = await api.get<{ agents: Record<string, Agent> }>('/chat/agents');
    return response.data.agents;
  },
};

export default api;
