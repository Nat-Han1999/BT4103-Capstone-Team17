// src/components/ChatContainer.js
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import MessageItem from './MessageItem';
import '../styles/ChatContainer.css';

function ChatContainer() {

  const [selectedModel, setSelectedModel] = useState('gemni');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState(localStorage.getItem('conversationId') || null);
  const [isTyping, setIsTyping] = useState(false);
  const inputRef = useRef(null);
  const premadePrompts = [
    "Summarise this website",
    "Can you guide me through the steps to file a claim or request assistance?",
    "What services or options are available on this website?"
  ];


  useEffect(() => {
    if (conversationId) {
      // Fetch existing conversation
      axios.get(`http://127.0.0.1:8000/conversation/${conversationId}/`)
        .then(res => {
          const msgs = res.data.messages.map(msg => ({
            text: msg.text,
            isUser: msg.sender === 'User'
          }));
          setMessages(msgs);
        })
        .catch(err => {
          console.error('Error fetching conversation:', err);
          // If conversation not found, start a new one
          if (err.response && err.response.status === 404) {
            startNewConversation();
          }
        });
    } else {
      // Start a new conversation
      startNewConversation();
    }
  }, [conversationId]);

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    localStorage.removeItem('conversationId');
  };


  //handleSend FUNCTION
  const handleSend = async () => {
    if (!input.trim()) {
        alert('Please enter a message.');
        return;
      }

    const userMessage = { text: input, isUser: true };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/generate/', {
        prompt: input,
        conversation_id: conversationId,
        model_name: selectedModel,
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
      const errorMessage = { text: 'Error: Unable to get response.', isUser: false };
      setMessages((prev) => [...prev, errorMessage]);
      setIsTyping(false); // Ensure isTyping is reset even if there's an error
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const handlePromptClick = async (promptText) => {
    setIsTyping(true);
  
    const userMessage = { text: promptText, isUser: true };
    setMessages((prev) => [...prev, userMessage]);
  
    try {
      const res = await axios.post('http://127.0.0.1:8000/generate/', {
        prompt: promptText,
        conversation_id: conversationId,
        model_name: selectedModel,
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
      const errorMessage = { text: 'Error: Unable to get response.', isUser: false };
      setMessages((prev) => [...prev, errorMessage]);
      setIsTyping(false);
    }
  };
  

  const clearConversation = () => {
    setMessages([]);
    const newConversationId = Math.random().toString(36).substr(2, 9);
    setConversationId(newConversationId);
    localStorage.setItem('conversationId', newConversationId);
  };

  return (
    <div className="chat-container">
      
      {/* Model Selection Section */}
      <div className="model-selector">
        <label htmlFor="model-select">Choose a model:</label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          <option value="distilgpt2">DistilGPT-2</option>
          <option value="gpt2">GPT-2</option>
          {/* Add more models if desired */}
        </select>
      </div>

  
      <div className="message-list">
        {messages.map((msg, idx) => (
          <MessageItem key={idx} message={msg} />
        ))}
        {isTyping && <div className="typing-indicator">Assistant is typing...</div>}
      </div>


      {/* Premade Prompts Section */}
      <div className="premade-prompts">
        <div className="prompt-buttons">
          {premadePrompts.map((prompt, idx) => (
            <button 
              key={idx} 
              onClick={() => handlePromptClick(prompt)} 
              className="prompt-button"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
  
      {/* Input Area Section */}
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="input"
          ref={inputRef}
          aria-label="Message input"
        />
        <button onClick={handleSend} className="send-button">
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
