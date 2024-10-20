import { createContext, useContext, useEffect, useState } from "react";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const chat = async (message, avatarName, id, isUser) => {
    setLoading(true);
    const data = await fetch("http://127.0.0.1:8000/api/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message, avatarName, id, isUser }),
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
  const [botReply, setBotReply] = useState();
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

  useEffect(() => {
    // This will only run once when the component mounts
    if (messages.length > 0) {
      setBotReply(messages.map((message) => message.text).join(""));
    } else {
      setBotReply(null);
    }
  }, [loading]);

  return (
    <ChatContext.Provider
      value={{
        chat,
        message,
        botReply, // Return all of bot's messages in the JSON for concatentation into 1 single line
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
