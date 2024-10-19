// src/components/ChatContainer.js

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import MessageItem from './MessageItem';
import '../styles/ChatContainer.css';

function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState(
    localStorage.getItem('conversationId') || null
  );
  const [isTyping, setIsTyping] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Use useRef to store the recognition instance
  const recognitionRef = useRef(null);

  const premadePrompts = [
    'Summarize this website',
    'Can you guide me through the steps to file a claim or request assistance?',
    'What services or options are available on this website?',
  ];


  const generateUniqueId = () => {
    return Math.random().toString(36).substr(2, 9);
  };

  // Helper Function: Start a new conversation
  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    localStorage.removeItem('conversationId');
  };

  // Helper Function: Clear the current conversation
  const clearConversation = () => {
    setMessages([]);
    const newConversationId = Math.random().toString(36).substr(2, 9);
    setConversationId(newConversationId);
    localStorage.setItem('conversationId', newConversationId);
  };

  // Helper Function: Auto-scroll to the latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // useEffect to scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Compute whether the send button should be disabled
  const isSendDisabled = isTyping || !input.trim();

  // Event Handler: Handle sending the user message
  const handleSend = async () => {
    const promptText = input; // Store input locally before clearing
    const userMessage = { id: generateUniqueId(), text: promptText, isUser: true };

    setMessages((prev) => [...prev, userMessage]);
    setInput(''); // Now clear the input field
    setIsTyping(true);
    setErrorMessage('');

    try {
      // Use the stored `promptText` instead of `input`
      const res = await axios.post('http://127.0.0.1:8000/generate/', {
        prompt: promptText, // Use promptText here
        conversation_id: conversationId,
      });

      const botResponseText = sanitizeResponse(res.data.response);
      const botMessage = {
        id: generateUniqueId(),
        text: botResponseText,
        isUser: false,
        feedbackGiven: false, // Add this property
      };
      setMessages((prev) => [...prev, botMessage]);
      speak(botMessage.text);
      setIsTyping(false);

      if (!conversationId) {
        setConversationId(res.data.conversation_id);
        localStorage.setItem('conversationId', res.data.conversation_id);
      }
    } catch (error) {
      console.error('Error in Axios request:', error);
      setErrorMessage(
        'An error occurred while fetching the response. Please try again.'
      );
      setIsTyping(false);
    }
  };

  // Helper Function: Handle prompt button clicks
  const handlePromptClick = async (promptText) => {
    setIsTyping(true);

    const userMessage = { text: promptText, isUser: true };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await axios.post('http://127.0.0.1:8000/generate/', {
        prompt: promptText,
        conversation_id: conversationId,
      });

      const botMessage = { text: res.data.response, isUser: false };
      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);

      if (!conversationId) {
        setConversationId(res.data.conversation_id);
        localStorage.setItem('conversationId', res.data.conversation_id);
      }
    } catch (error) {
      console.error('Error in Axios request:', error);
      const errorMessage = {
        text: 'Error: Unable to get response.',
        isUser: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
      setIsTyping(false);
    }
  };

  // Event Handler: Handle Enter key press to send message
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isSendDisabled) {
      handleSend();
    }
  };

  // Voice Input Functions
  const handleVoiceInput = () => {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser.');
      return;
    }

    if (isRecording) {
      // Stop recording
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      // Start recording
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      recognition.onresult = (event) => {
        const voiceInput = event.results[0][0].transcript;
        setInput(voiceInput);
        setIsRecording(false);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
      setIsRecording(true);
    }
  };

  // Voice Output Function
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.speak(utterance);
    }
  };

  // Simple security enhancement: Sanitize bot response
  const sanitizeResponse = (response) => {
    // Implement sanitization logic as needed
    // For example, remove any disallowed content or code
    const sanitized = response.replace(/<[^>]*>?/gm, '');
    return sanitized;
  };

  // useEffect: Fetch existing conversation or start a new one
  useEffect(() => {
    if (conversationId) {
      axios
        .get(`http://127.0.0.1:8000/conversation/${conversationId}/`)
        .then((res) => {
          const msgs = res.data.messages.map((msg) => ({
            id: msg.id || generateUniqueId(),
            text: msg.text,
            isUser: msg.sender === 'User',
            feedbackGiven: msg.feedback ? true : false, // Set to true if feedback exists
          }));
          setMessages(msgs);
        })
        .catch((err) => {
          console.error('Error fetching conversation:', err);
          if (err.response && err.response.status === 404) {
            startNewConversation();
          }
        });
    } else {
      startNewConversation();
    }
  }, [conversationId]); // Trigger this effect when conversationId changes

  

  // Feedback Handler
  const handleFeedback = async (message, feedback) => {
    try {
      await axios.post('http://127.0.0.1:8000/feedback/', {
        conversation_id: conversationId,
        message_id: message.id,
        feedback: feedback,
      });
      console.log('Feedback submitted');
  
      // Update the message's feedbackGiven property
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === message.id ? { ...msg, feedbackGiven: true } : msg
        )
      );
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  // Render Section (JSX)
  return (
    <div className="chat-container">
      {/* Error Message */}
      {errorMessage && <div className="error-message">{errorMessage}</div>}

      {/* Message List */}
      <div className="message-list">
        {messages.map((msg, idx) => (
          <MessageItem
            key={idx}
            message={msg}
            onFeedback={handleFeedback}
          />
        ))}
        {isTyping && (
          <div className="typing-indicator">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Premade Prompts */}
      <div className="premade-prompts">
        <div className="prompt-buttons">
          {premadePrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handlePromptClick(prompt)}
              className="prompt-button"
              disabled={isTyping}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="input-area">
        <button
          onClick={handleVoiceInput}
          className={`voice-button ${isRecording ? 'recording' : ''}`}
          aria-label="Voice input"
        >
          {isRecording ? '🛑 Stop' : '🎤 Record'}
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="input"
          ref={inputRef}
          aria-label="Message input"
          disabled={isTyping}
        />
        <button
          onClick={handleSend}
          className="send-button"
          disabled={isSendDisabled}
          aria-label="Send message"
        >
          Send
        </button>
      </div>

      {/* Clear Conversation Button */}
      <button onClick={clearConversation} className="clear-button">
        Clear Conversation
      </button>
    </div>
  );
}

export default ChatContainer;