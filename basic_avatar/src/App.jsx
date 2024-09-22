import { Canvas } from "@react-three/fiber";
import { Experience } from "./components/Experience";
import { BackgroundDropdown } from "./components/BackgroundDropdown";
import {
  Box,
  Stack,
  InputLabel,
  FormControl,
  NativeSelect,
  formHelperTextClasses,
} from "@mui/material";
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

  // Hooks for voice change
  const [avatarScript, setAvatarScript] = useState("hello");
  useEffect(() => {
    setAvatarScript("hello");
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
        <Box
          p={3}
          sx={{
            width: 150,
            height: 150,
            borderRadius: 2,
            display: "flex",
            bgcolor: "white",
            justifyContent: "center",
            alignItems: "center",
            color: "white",
          }}
        >
          <Stack spacing={3}>
            <FormControl fullWidth>
              <InputLabel variant="standard">Background Image</InputLabel>
              <NativeSelect
                defaultValue={"avatar_bg"}
                onChange={(e) => {
                  setAvatarBG(e.target.value);
                }}
              >
                <option value={"avatar_bg"}>Default</option>
                <option value={"avatar_bg2"}>Seaside</option>
                <option value={"avatar_bg3"}>Desert</option>
                <option value={"avatar_bg4"}>Space</option>
              </NativeSelect>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel variant="standard">Avatar</InputLabel>
              <NativeSelect
                defaultValue={"avatar_chinese_lady"}
                onChange={(e) => {
                  setAvatarLook(e.target.value);
                  if (e.target.value == "avatar_chinese_lady") {
                    setAvatarScript("hello");
                  } else if (e.target.value == "avatar_indian_man") {
                    setAvatarScript("niraj");
                  } else {
                    setAvatarScript("hello");
                  }
                }}
              >
                <option value={"avatar_chinese_lady"}>Chinese Lady</option>
                <option value={"avatar_indian_man"}>Indian Man</option>
              </NativeSelect>
            </FormControl>
          </Stack>
        </Box>
      </Html>
      <color attach="background" args={["#ececec"]} />
      <Experience
        chosen_bg={avatarBG}
        chosen_avatar={avatarLook}
        chosen_script={avatarScript}
      />
    </Canvas>
  );
}

export default App;
