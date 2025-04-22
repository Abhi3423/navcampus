import { useEffect, useState } from "react";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import * as THREE from "three";

function Model({ modelData, scale = 1, position = [0, 0, 0] }) {
  const [scene, setScene] = useState(null);
  const MIN_SCALE = 0.1;

  useEffect(() => {
    if (!modelData) return;

    const loadModel = async () => {
      try {
        let base64String = modelData.includes(",")
          ? modelData.split(",")[1]
          : modelData;
        base64String = base64String.trim().replace(/\s/g, "");
        while (base64String.length % 4 !== 0) {
          base64String += "=";
        }

        const byteCharacters = atob(base64String);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "model/gltf-binary" });
        const url = URL.createObjectURL(blob);

        const loader = new GLTFLoader();
        loader.load(
          url,
          (gltf) => {
            const modelScene = gltf.scene;
            const clampedScale = Math.max(scale, MIN_SCALE);
            modelScene.scale.set(clampedScale, clampedScale, clampedScale);
            modelScene.updateMatrixWorld(true);

            // Center the model: calculate its bounding box center
            const box = new THREE.Box3().setFromObject(modelScene);
            const center = new THREE.Vector3();
            box.getCenter(center);
            // Re-center the model so that its center is at the origin, then offset it by the provided position
            const offset = new THREE.Vector3(...position);
            modelScene.position.sub(center).add(offset);

            modelScene.traverse((child) => {
              if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
              }
            });

            setScene(modelScene);
            URL.revokeObjectURL(url);
          },
          undefined,
          (error) => console.error("Error loading GLTF model:", error)
        );
      } catch (error) {
        console.error("Error processing Base64 GLTF model:", error);
      }
    };

    loadModel();
  }, [modelData, scale, position]);

  if (!scene) return null;
  return <primitive object={scene} />;
}

export default Model;
