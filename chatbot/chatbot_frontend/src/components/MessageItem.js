// src/components/MessageItem.js

import React from 'react';
import '../styles/MessageItem.css';

const MessageItem = ({ message, onFeedback }) => (
  <div className={`message-item ${message.isUser ? 'user' : 'bot'}`}>
    <p>{message.text}</p>

    {!message.isUser && (
      <>
        {!message.feedbackGiven ? (
          <div className="feedback-buttons">
            <button
              className="feedback-button like-button"
              onClick={() => onFeedback(message, 'like')}
            >
              👍
            </button>
            <button
              className="feedback-button dislike-button"
              onClick={() => onFeedback(message, 'dislike')}
            >
              👎
            </button>
          </div>
        ) : (
          <div className="feedback-thanks">
            <span>Thank you for your feedback!</span>
          </div>
        )}
      </>
    )}
  </div>
);

export default MessageItem;