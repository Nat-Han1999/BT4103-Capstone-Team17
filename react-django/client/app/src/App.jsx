import { Loader } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Leva } from "leva";
import { Experience } from "./components/Experience";
import { UI } from "./components/UI";
import {  useState, useEffect } from "react";

function App() {
  // Hooks for avatar change
  const [avatarLook, setAvatarLook] = useState("Helen");
  // useEffect(() => {
  //   setAvatarLook("Helen");
  // }, []);

  return (
    <>
      <Loader />
      <Leva />
      <UI setAvatarLook = {setAvatarLook}/>
      <Canvas camera={{ position: [0, 0, 1], fov: 50 }}>
        <Experience avatarLook = {avatarLook}/>
      </Canvas>
    </>
  );
}

export default App;
