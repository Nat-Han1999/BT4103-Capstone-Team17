import {
  CameraControls,
  ContactShadows,
  Environment,
  Text,
} from "@react-three/drei";
import { Suspense, useEffect, useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import { Helen } from "./Helen";
import { Aisha } from "./Aisha";
import { Niraj } from "./Niraj";
import { Carter } from "./Carter";

export function Experience({ avatarLook }) {
  const Dots = (props) => {
    const { loading } = useChat();
    const [loadingText, setLoadingText] = useState("");
    useEffect(() => {
      if (loading) {
        const interval = setInterval(() => {
          setLoadingText((loadingText) => {
            if (loadingText.length > 2) {
              return ".";
            }
            return loadingText + ".";
          });
        }, 800);
        return () => clearInterval(interval);
      } else {
        setLoadingText("");
      }
    }, [loading]);
    if (!loading) return null;
    return (
      <group {...props}>
        <Text fontSize={0.14} anchorX={"left"} anchorY={"bottom"}>
          {loadingText}
          <meshBasicMaterial attach="material" color="black" />
        </Text>
      </group>
    );
  };

  // Conditional for avatar output
  let avatarOutput;
  let xPosition;
  let yPosition; // Set height of loading dot to be different for male and female, since males are taller 

  if (avatarLook == "Helen") {
    avatarOutput = <Helen />;
    xPosition = -0.08;
    yPosition = 1.75;
  } else if (avatarLook == "Aisha") {
    avatarOutput = <Aisha />;
    xPosition = -0.02;
    yPosition = 1.75;
  } else if (avatarLook == "Niraj") {
    avatarOutput = <Niraj />;
    xPosition = -0.02;
    yPosition = 1.88;
  } else {
    avatarOutput = <Carter />;
    xPosition = -0.02;
    yPosition = 1.88;
  }

  const cameraControls = useRef();
  const { cameraZoomed } = useChat();

  useEffect(() => {
    cameraControls.current.setLookAt(0, 2, 5, 0, 1.5, 0);
  }, []);

  useEffect(() => {
    if (cameraZoomed) {
      cameraControls.current.setLookAt(0, 1.5, 1.5, 0, 1.5, 0, true);
    } else {
      cameraControls.current.setLookAt(0, 2.2, 5, 0, 1.0, 0, true);
    }
  }, [cameraZoomed]);
  return (
    <>
      <CameraControls ref={cameraControls} />
      <Environment preset="sunset" />
      {/* Wrapping Dots into Suspense to prevent Blink when Troika/Font is loaded */}
      <Text fontSize={0.14} anchorX={"left"} anchorY={"bottom"}>
        ...
        <meshBasicMaterial attach="material" color="black" />
      </Text>
      <Suspense>
        <Dots position-y={yPosition} position-x={xPosition} />
      </Suspense>
      {avatarOutput}
      <ContactShadows opacity={0.7} />
    </>
  );
}
