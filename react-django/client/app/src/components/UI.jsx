import { useRef, useState } from "react";
import { useChat } from "../hooks/useChat";

export function UI({ setAvatarLook, hidden, ...props }) {
  const input = useRef();
  const { chat, loading, message } = useChat();

  const sendMessage = () => {
    const text = input.current.value;
    if (!loading && !message) {
      chat(text, avatarName);
      input.current.value = "";
    }
  };
  if (hidden) {
    return null;
  }

  // Hook that stores avatar name that is being selected
  const [avatarName, setAvatarName] = useState("Helen");

  return (
    <>
      <div className="fixed top-0 left-0 right-0 bottom-0 z-10 flex justify-between p-4 flex-col pointer-events-none">
        <div className="self-start backdrop-blur-md bg-white bg-opacity-50 p-4 rounded-lg">
          <h1 className="font-black text-xl">AI Chatbot</h1>
          <p>BZA Capstone Project</p>
        </div>
        <div className="w-full flex flex-col items-end justify-center gap-4">
          <div className="bg-white bg-opacity-80 shadow-lg rounded-lg p-6 max-w-md">
            <h2 className="text-l font-semibold mb-2 text-center">Settings</h2>
            <hr className="border-gray-500 mb-4" />
            <div className="pointer-events-auto mb-4">
              <label className="block text-gray-700 mb-2 text-sm">
                Background
              </label>
              <select
                defaultValue="avatar_bg"
                onChange={(e) => {
                  const body = document.querySelector("body");
                  body.classList = "";
                  body.classList.add(e.target.value);
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
              <label className="block text-gray-700 text-sm mb-2">Avatar</label>
              <select
                defaultValue="Helen"
                onChange={(e) => {
                  setAvatarLook(e.target.value);
                  setAvatarName(e.target.value); // Set avatar name locally in this file so that data can be passed to Django backend for correct voice to be generated
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
        <div className="flex items-center gap-2 pointer-events-auto max-w-screen-sm w-full mx-auto">
          <input
            className="w-full placeholder:text-gray-800 placeholder:italic p-4 rounded-md bg-opacity-50 bg-white backdrop-blur-md"
            placeholder="Type a message..."
            ref={input}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage();
              }
            }}
          />
          <button
            disabled={loading || message}
            onClick={sendMessage}
            className={`bg-blue-500 hover:bg-blue-600 text-white p-4 px-10 font-semibold uppercase rounded-md ${
              loading || message ? "cursor-not-allowed opacity-30" : ""
            }`}
          >
            Send
          </button>
        </div>
      </div>
    </>
  );
}
