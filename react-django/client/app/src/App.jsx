import { Loader } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Leva } from "leva";
import { Experience } from "./components/Experience";
import { UI } from "./components/UI";
import {  useState, useEffect } from "react";

function App() {
  // Hook for avatar change
  const [avatarLook, setAvatarLook] = useState("Helen");

  return (
    <>
      <Loader />
      <Leva hidden/>
      <UI setAvatarLook = {setAvatarLook}/>
      <Canvas camera={{ position: [0, 0, 1], fov: 50 }}>
        <Experience avatarLook = {avatarLook}/>
      </Canvas>
    </>
  );
}

export default App;
