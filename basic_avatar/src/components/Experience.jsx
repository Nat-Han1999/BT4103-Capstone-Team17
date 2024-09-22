import { Environment, OrbitControls, useTexture } from "@react-three/drei";
import { Avatar_Chinese_Lady } from "./Avatar_Chinese_Lady";
import { Avatar_Indian_Man } from "./Avatar_Indian_Man";
import { useThree } from "@react-three/fiber";

export function Experience({ chosen_bg, chosen_avatar, chosen_script }) {
  const texture = useTexture(`textures/${chosen_bg}.jpg`);
  const viewport = useThree((state) => state.viewport);

  // Conditional for avatar output
  let avatarOutput;

  if (chosen_avatar == "avatar_chinese_lady") {
    avatarOutput = (
      <Avatar_Chinese_Lady
        position={[0, -3, 5]}
        chosen_script={chosen_script}
        scale={2}
      />
    );
  } else if (chosen_avatar == "avatar_indian_man") {
    avatarOutput = (
      <Avatar_Indian_Man
        position={[0, -3, 5]}
        chosen_script={chosen_script}
        scale={2}
      />
    );
  } else {
    avatarOutput = (
      <Avatar_Indian_Man
        position={[0, -3, 5]}
        chosen_script={chosen_script}
        scale={2}
      />
    );
  }

  return (
    <>
      <OrbitControls />
      {avatarOutput}
      <Environment preset="sunset" />
      <mesh>
        <planeGeometry args={[viewport.width, viewport.height]} />
        <meshBasicMaterial map={texture} />
      </mesh>
    </>
  );
}
