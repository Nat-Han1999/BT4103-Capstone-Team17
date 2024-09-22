import { Canvas } from "@react-three/fiber";
import { Experience } from "./components/Experience";
import { BackgroundDropdown } from "./components/BackgroundDropdown";
import { Html } from "@react-three/drei";
import { useState, useEffect } from "react";

function App() {
  // Hooks for BG change
  const [avatarBG, setAvatarBG] = useState("avatar_bg");
  useEffect(() => {
    setAvatarBG("avatar_bg");
  }, []);

  // Hooks for avatar change
  const [avatarLook, setAvatarLook] = useState("avatar_chinese_lady");
  useEffect(() => {
    setAvatarLook("avatar_chinese_lady");
  }, []);

  return (
    <Canvas shadows camera={{ position: [0, 0, 8], fov: 42 }}>
      <color attach="background" args={["#ececec"]} />
      <Html
        style={{
          top: "-200px", // Distance from the top
          left: "400px", // Distance from the left
          pointerEvents: "auto", // Allow pointer events
        }}
      >
        <select
          value={avatarBG}
          onChange={(e) => {
            setAvatarBG(e.target.value);
          }}
        >
          <option value="avatar_bg">Default</option>
          <option value="avatar_bg2">Seaside</option>
        </select>

        <select
          value={avatarLook}
          onChange={(e) => {
            setAvatarLook(e.target.value);
          }}
        >
          <option value="avatar_chinese_lady">Chinese Lady</option>
          <option value="avatar_indian_man">Indian Man</option>
        </select>
      </Html>
      <color attach="background" args={["#ececec"]} />
      <Experience chosen_bg={avatarBG} chosen_avatar={avatarLook} />
    </Canvas>
  );
}

export default App;
