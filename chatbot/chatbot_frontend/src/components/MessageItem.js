// src/components/MessageItem.js
import React from 'react';
import '../styles/MessageItem.css';

function MessageItem({ message }) {
  const messageClass = message.isUser ? 'user-message' : 'bot-message';

  return (
    <div className={`message-item ${messageClass}`}>
      {message.text}
    </div>
  );
}

export default MessageItem;
