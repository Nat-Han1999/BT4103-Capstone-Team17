import { useRef, useState, useEffect } from "react";
import { useChat } from "../hooks/useChat";
import { Canvas } from "@react-three/fiber";
import { Experience } from "./Experience.jsx";
import "./Chat_Components.css";
import { MessageItem } from "./Message_Item.jsx";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";

export function UI({ hidden, ...props }) {
  const input = useRef();
  const { chat, loading, message, botReply } = useChat();

  // Create a hook to store all messages in the chat
  const [uiMessages, setUIMessages] = useState([]);

  // Create a hook to store the unique user ID associated with the user's chat session
  const [userID, setUserID] = useState(localStorage.getItem("userID") || null);

  // Create a hook to store the typing indictor when the bot is loading
  const [botTyping, setBotTyping] = useState(false);

  // CHECK WHETHER USERID IS STORED PROPERLY IN LOCAL STORAGE EACH TIME COMPONENT MOUNTS
  useEffect(() => {
    if (userID) {
      axios
        .get(`http://127.0.0.1:8000/api/get-messages/${userID}/`)
        .then((res) => {
          const msgs = res.data.messages.map((msg) => ({
            id: msg.id,
            text: msg.text,
            isUser: msg.sender === "User",
            feedbackGiven: msg.feedback ? true : false,
          }));
          setUIMessages(msgs);
        });
      // Get avatar selected
      axios
        .get(`http://127.0.0.1:8000/api/get-avatar/${userID}/`)
        .then((res) => {
          const name = res.data.avatar_selected;
          setAvatarName(name);
        });
      // Get BG selected
      axios.get(`http://127.0.0.1:8000/api/get-bg/${userID}/`).then((res) => {
        const bg = res.data.bg_selected;
        const body = document.querySelector("body");
        body.classList = "";
        body.classList.add(bg);
        setBackgroundName(bg);
      });
    }
  }, []);

  // Create a useEffect to track the state of the messages
  useEffect(() => {
    if (!botReply) {
      //console.log("nothing");
    } else {
      let botMessage = { text: botReply, isUser: false };
      setUIMessages((prev) => [...prev, botMessage]);
      //console.log("botreply");
      //console.log(botReply);
    }
  }, [botReply]);

  // Create a useEffect hook to track whether the LLM is loading
  useEffect(() => {
    if (loading) {
      setBotTyping(true);
    } else {
      setBotTyping(false);
    }
  }, [loading]);

  const sendMessage = () => {
    const text = input.current.value;
    const isUser = true;

    // Generate userID if it does not exist
    if (!userID) {
      const id = generateUniqueUUID();
      setUserID(id);
      localStorage.setItem("userID", id);
      chat(text, avatarName, backgroundName, id, isUser);
    } else if (!loading && text) {
      chat(text, avatarName, backgroundName, userID, isUser);
    }
    // Clear input and update messages
    input.current.value = "";
    if (text) {
      setUIMessages((prev) => [...prev, { id: userID, text, isUser }]);
    }
  };

  if (hidden) {
    return null;
  }

  // Hook that stores avatar name that is being selected
  const [avatarName, setAvatarName] = useState("Helen");

  // Hook that stores background that is being selected
  const [backgroundName, setBackgroundName] = useState("avatar_bg");

  // Hook to track voice recording functionality
  const [isRecording, setIsRecording] = useState(false);
  // Use useRef to store the recognition instance
  const recognitionRef = useRef(null);

  // Voice Input Functions
  const handleVoiceInput = () => {
    if (
      !("SpeechRecognition" in window || "webkitSpeechRecognition" in window)
    ) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    if (isRecording) {
      // Stop recording
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      input.current.value = ""; // Clear text input field before any recording is made
      // Start recording
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      recognition.onresult = (event) => {
        const voiceInput = event.results[0][0].transcript;
        input.current.value = voiceInput;
        setIsRecording(false);
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
      setIsRecording(true);
    }
  };

  // Functions to handle sending of message
  const generateUniqueUUID = () => {
    return uuidv4();
  };

  // Reference that ensures the most recent message is shown in the chat
  const messageEndRef = useRef(null);

  const scrollToBottom = () => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollTop = messageEndRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom(); 
    const handleResize = () => {
      scrollToBottom(); 
    };
    // Ensures that chat scrolls to bottom when page is resized 
    window.addEventListener("resize", handleResize); 
    return () => {
      window.removeEventListener("resize", handleResize); 
    };
  }, [uiMessages]);

  return (
    <>
      <div className="fixed top-0 left-0 right-0 bottom-0 z-10 flex flex-col lg:flex-row pointer-events-none">
        <div className="flex flex-row w-screen h-screen lg:w-4/6">
          <div className="w-1/6 h-full pt-10 pl-3">
            <div className="self-start backdrop-blur-md bg-white bg-opacity-50 p-3 rounded-lg max-w-xs max-h-[150px] mx-auto">
              <h1 className="font-black text-xl">AI Chatbot</h1>
              <p>BZA Capstone Project</p>
            </div>
          </div>
          <div className="flex-grow w-4/6 h-full flex items-center justify-center">
            <Canvas camera={{ position: [0, 0, 1], fov: 50 }}>
              <Experience avatarLook={avatarName} />
            </Canvas>
          </div>
          <div className="flex-grow w-1/6 h-full flex items-center justify-center">
            <div className="flex flex-col items-end justify-start gap-4">
              <div className="bg-white bg-opacity-80 shadow-lg rounded-lg p-6 max-w-md">
                <h2 className="text-l font-semibold mb-2 text-center">
                  Settings
                </h2>
                <hr className="border-gray-500 mb-4" />
                <div className="pointer-events-auto mb-4">
                  <label className="block text-gray-700 mb-2 text-sm">
                    Background
                  </label>
                  <select
                    // Change this default variable to something changeable
                    defaultValue="avatar_bg"
                    value={backgroundName}
                    onChange={(e) => {
                      const body = document.querySelector("body");
                      body.classList = "";
                      body.classList.add(e.target.value);
                      setBackgroundName(e.target.value);
                      // Update the BG selection in the DB
                      if (userID) {
                        axios
                          .patch(
                            `http://127.0.0.1:8000/api/update-bg/${userID}/${e.target.value}/`
                          )
                          .then((response) => {
                            if (response.data.success) {
                              console.log(response.data.message);
                            } else {
                              console.error("Error:", response.data.error);
                            }
                          });
                      }
                    }}
                    className="bg-blue-500 hover:bg-blue-600 text-white text-sm p-2 w-full rounded-md"
                  >
                    <option value="avatar_bg">Default</option>
                    <option value="avatar_bg2">Seaside</option>
                    <option value="avatar_bg3">Desert</option>
                    <option value="avatar_bg4">Space</option>
                  </select>
                </div>
                <div className="pointer-events-auto mb-4">
                  <label className="block text-gray-700 text-sm mb-2">
                    Avatar
                  </label>
                  <select
                    defaultValue="Helen"
                    value={avatarName}
                    onChange={(e) => {
                      // Update avatarName that has been selected in the backend
                      setAvatarName(e.target.value);
                      // Only update avatar if user has chatted with the bot, otherwise there will be no ChatSession to store the name under
                      if (userID) {
                        axios
                          .patch(
                            `http://127.0.0.1:8000/api/update-avatar/${userID}/${e.target.value}/`
                          )
                          .then((response) => {
                            if (response.data.success) {
                              console.log(response.data.message);
                            } else {
                              console.error("Error:", response.data.error);
                            }
                          });
                      }
                    }}
                    className="bg-blue-500 hover:bg-blue-600 text-white text-sm p-2 w-full rounded-md"
                  >
                    <option value={"Helen"}>Helen</option>
                    <option value={"Aisha"}>Aisha</option>
                    <option value={"Niraj"}>Niraj</option>
                    <option value={"Carter"}>Carter</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          ref={messageEndRef}
          className="flex flex-col w-screen h-screen lg:w-2/6 items-center justify-between lg:mt-0 lg:h-auto h-[25vh] m-0 p-1 bg-white overflow-auto"
        >
          <div
            className="max-w-screen-sm w-full flex flex-col h-full bg-blue-200 overflow:auto"
            style={{ maxHeight: "calc(100% - 150px)" }}
          >
            {uiMessages.map((msg, idx) => (
              <MessageItem key={idx} message={msg} />
            ))}
            {botTyping && (
              <div className="typing-indicator">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            )}

            <div className=""></div>

            <div className="flex items-center gap-2 pointer-events-auto max-w-screen-sm w-full mx-auto mt-3 bg-red-200">
              <textarea
                wrap="soft"
                className="flex-grow h-13 placeholder:text-gray-800 placeholder:italic p-4 rounded-md bg-white-200 backdrop-blur-md resize-none border border-gray-400 focus:border-gray-600"
                placeholder="Type a message..."
                ref={input}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
              />
              <button
                disabled={loading || message}
                onClick={sendMessage}
                className={`bg-blue-500 hover:bg-blue-600 text-white p-2 font-semibold uppercase rounded-md ${
                  loading || message ? "cursor-not-allowed opacity-30" : ""
                }`}
              >
                Send
              </button>
              <button
                onClick={handleVoiceInput}
                className={`voice-button ${
                  isRecording ? "recording" : ""
                } w-10 h-10 bg-black hover:bg-red-600 rounded-full flex items-center justify-center`}
              >
                {!isRecording ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    fill="white"
                    className="bi bi-mic-fill"
                    viewBox="0 0 16 16"
                  >
                    <path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0z" />
                    <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5" />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    fill="white"
                    className="bi bi-stop-fill"
                    viewBox="0 0 16 16"
                  >
                    <path d="M5 3.5h6A1.5 1.5 0 0 1 12.5 5v6a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 11V5A1.5 1.5 0 0 1 5 3.5" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
