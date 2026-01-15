import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader } from 'lucide-react';
import ChatMessage from './ChatMessage';
import { Message } from '../types';
import { streamService } from '../services/stream';
import './ChatInterface.css';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const generateSessionId = () => {
    if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
      return crypto.randomUUID();
    }
    return Date.now().toString();
  };
  const [sessionId] = useState<string>(() => generateSessionId());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    const assistantMsgId = (Date.now() + 1).toString();
    const initialAssistantMessage: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      steps: []
    };

    setMessages((prev) => [...prev, initialAssistantMessage]);

    // Track state for the current streaming message
    let currentContent = '';
    let currentSteps: any[] = [];

    streamService.streamChat(
      {
        message: inputValue,
        session_id: sessionId,
        agent_type: 'healthcare',
      },
      (event) => {
        if (event.type === 'plan') {
          currentSteps = event.steps;
        } else if (event.type === 'status') {
          currentSteps = currentSteps.map(step =>
            step.id === event.step_id
              ? { ...step, status: event.status, details: event.details }
              : step
          );
        } else if (event.type === 'message') {
          if (event.is_final) {
            if (event.content) {
              currentContent = event.content;
            }
          } else {
            currentContent += event.content;
          }
        }

        // Update message based on event type
        setMessages((prev) => prev.map(msg => {
          if (msg.id !== assistantMsgId) return msg;

          if (event.type === 'plan' || event.type === 'status') {
            return { ...msg, steps: currentSteps };
          } else if (event.type === 'message') {
            return { ...msg, content: currentContent };
          } else if (event.type === 'error') {
            return { ...msg, content: `Error: ${event.error}` };
          }
          return msg;
        }));

        // If it's a message event, setIsLoading might be done if is_final
        if (event.type === 'message' && event.is_final) {
          setIsLoading(false);
        }
      },
      () => {
        // On complete
        setIsLoading(false);
      },
      (error) => {
        console.error('Stream error:', error);
        setMessages((prev) => prev.map(msg =>
          msg.id === assistantMsgId ? { ...msg, content: `Error: ${error}` } : msg
        ));
        setIsLoading(false);
      }
    );
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>AgentOrchestra Stack</h1>
        <p>Agent UI + Data Access</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>👋 Welcome!</h2>
            <p>Start a conversation with our AI agent. Try asking a question or sharing something!</p>
          </div>
        )}
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isLoading && (
          <div className="loading-indicator">
            <Loader className="spinner" size={20} />
            <span>Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={!inputValue.trim() || isLoading}
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
