import React from 'react';
import { Message } from '../types';
import StepProgress from './StepProgress';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-header">
        <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
        <span className="timestamp">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      <div className="message-content">
        {message.content}
        {message.steps && <StepProgress steps={message.steps} />}
      </div>
    </div>
  );
};

export default ChatMessage;
