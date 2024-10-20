import { createContext, useContext, useEffect, useState } from "react";

const ChatContext = createContext(); 

export const ChatProvider = ({ children }) => {
  const chat = async (message, avatarName) => {
    setLoading(true); 
    const data = await fetch("http://127.0.0.1:8000/api/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message, avatarName }),
    });
    const resp = await data.json().then((json) => {
      return json.messages;
    });
    setMessages((messages) => {
      return [...messages, ...resp];
    });
    setLoading(false);
  };
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState();
  const [loading, setLoading] = useState(false);
  const [cameraZoomed, setCameraZoomed] = useState(true);
  const onMessagePlayed = () => {
    setMessages((messages) => messages.slice(1));
  };

  useEffect(() => {
    if (messages.length > 0) {
      setMessage(messages[0]);
    } else {
      setMessage(null);
    }
  }, [messages]);

  return (
    <ChatContext.Provider
      value={{
        chat,
        message,
        onMessagePlayed,
        loading,
        cameraZoomed,
        setCameraZoomed,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) { 
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
 