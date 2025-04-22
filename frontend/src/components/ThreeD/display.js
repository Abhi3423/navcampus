import React, { useState, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import {
  FaArrowCircleUp,
  FaArrowCircleDown,
  FaChevronDown,
  FaChevronUp,
} from "react-icons/fa";
import Model from "./model";

export default function Display({ setDisplay, modelData }) {
  const [scale, setScale] = useState(1);
  const controlsRef = useRef(null);
  const MIN_SCALE = 0.1;
  const panAmount = 10; // Adjust as needed

  // Default lighting values (as in the original code)
  const [ambientIntensity, setAmbientIntensity] = useState(0.2);
  const [ambientColor, setAmbientColor] = useState("#ffffff");
  const [hemisphereIntensity, setHemisphereIntensity] = useState(0.6);
  const [hemisphereSkyColor, setHemisphereSkyColor] = useState("#ffffff");
  const [hemisphereGroundColor, setHemisphereGroundColor] = useState("#444444");
  const [directionalIntensity1, setDirectionalIntensity1] = useState(1.5);
  const [directionalColor1, setDirectionalColor1] = useState("#ffffff");
  const [directionalPosition1, setDirectionalPosition1] = useState({ x: 100, y: 200, z: 100 });
  const [directionalIntensity2, setDirectionalIntensity2] = useState(1.0);
  const [directionalColor2, setDirectionalColor2] = useState("#ffffff");
  const [directionalPosition2, setDirectionalPosition2] = useState({ x: -100, y: 200, z: -100 });

  // Panel collapse state
  const [lightingPanelOpen, setLightingPanelOpen] = useState(true);

  // Zoom Controls
  const handleDecrease = () => {
    setScale((prev) => {
      const newScale = prev - 0.1;
      return newScale < MIN_SCALE ? MIN_SCALE : newScale;
    });
  };

  const handleIncrease = () => {
    setScale((prev) => prev + 0.1);
  };

  // Pan Controls with reversed directions
  const panLeft = () => {
    if (controlsRef.current) {
      controlsRef.current.target.x += panAmount;
      controlsRef.current.object.position.x += panAmount;
      controlsRef.current.update();
    }
  };

  const panRight = () => {
    if (controlsRef.current) {
      controlsRef.current.target.x -= panAmount;
      controlsRef.current.object.position.x -= panAmount;
      controlsRef.current.update();
    }
  };

  const panForward = () => {
    if (controlsRef.current) {
      controlsRef.current.target.z += panAmount;
      controlsRef.current.object.position.z += panAmount;
      controlsRef.current.update();
    }
  };

  const panBackward = () => {
    if (controlsRef.current) {
      controlsRef.current.target.z -= panAmount;
      controlsRef.current.object.position.z -= panAmount;
      controlsRef.current.update();
    }
  };

  const panYUp = () => {
    if (controlsRef.current) {
      controlsRef.current.target.y -= panAmount;
      controlsRef.current.object.position.y -= panAmount;
      controlsRef.current.update();
    }
  };

  const panYDown = () => {
    if (controlsRef.current) {
      controlsRef.current.target.y += panAmount;
      controlsRef.current.object.position.y += panAmount;
      controlsRef.current.update();
    }
  };

  // Helpers for directional light position sliders
  const updateDirectionalPosition1 = (axis, value) => {
    setDirectionalPosition1((prev) => ({ ...prev, [axis]: parseFloat(value) }));
  };

  const updateDirectionalPosition2 = (axis, value) => {
    setDirectionalPosition2((prev) => ({ ...prev, [axis]: parseFloat(value) }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex justify-center items-center">
      {/* Close Button */}
      <button
        className="absolute top-4 right-4 bg-white text-black p-2 rounded-full text-lg z-10 shadow hover:bg-gray-200"
        onClick={() => setDisplay(false)}
      >
        ✕
      </button>

      {/* Lighting Controls Panel - Positioned at top left */}
      <div className="absolute top-4 left-4 z-50 w-64">
        <div
          className="bg-gray-800 text-white rounded-md p-2 shadow cursor-pointer flex items-center justify-between"
          onClick={() => setLightingPanelOpen(!lightingPanelOpen)}
        >
          <span className="text-sm font-medium">Lighting Controls</span>
          {lightingPanelOpen ? <FaChevronUp /> : <FaChevronDown />}
        </div>
        {lightingPanelOpen && (
          <div className="bg-gray-700 text-white rounded-md p-3 shadow mt-2 text-xs space-y-3">
            {/* Ambient Light Controls */}
            <div>
              <label>Ambient Intensity: {ambientIntensity}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={ambientIntensity}
                onChange={(e) => setAmbientIntensity(parseFloat(e.target.value))}
                className="w-full mt-1"
              />
              <label>Color:</label>
              <input
                type="color"
                value={ambientColor}
                onChange={(e) => setAmbientColor(e.target.value)}
                className="w-full mt-1"
              />
            </div>

            {/* Hemisphere Light Controls */}
            <div>
              <label>Hemisphere Intensity: {hemisphereIntensity}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={hemisphereIntensity}
                onChange={(e) => setHemisphereIntensity(parseFloat(e.target.value))}
                className="w-full mt-1"
              />
              <label>Sky Color:</label>
              <input
                type="color"
                value={hemisphereSkyColor}
                onChange={(e) => setHemisphereSkyColor(e.target.value)}
                className="w-full mt-1"
              />
              <label>Ground Color:</label>
              <input
                type="color"
                value={hemisphereGroundColor}
                onChange={(e) => setHemisphereGroundColor(e.target.value)}
                className="w-full mt-1"
              />
            </div>

            {/* Directional Light 1 Controls */}
            <div>
              <label>Directional 1 Intensity: {directionalIntensity1}</label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={directionalIntensity1}
                onChange={(e) => setDirectionalIntensity1(parseFloat(e.target.value))}
                className="w-full mt-1"
              />
              <label>Color:</label>
              <input
                type="color"
                value={directionalColor1}
                onChange={(e) => setDirectionalColor1(e.target.value)}
                className="w-full mt-1"
              />
              <div className="mt-1">
                <div>
                  <label>X: {directionalPosition1.x}</label>
                  <input
                    type="range"
                    min="-300"
                    max="300"
                    step="1"
                    value={directionalPosition1.x}
                    onChange={(e) => updateDirectionalPosition1("x", e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <label>Y: {directionalPosition1.y}</label>
                  <input
                    type="range"
                    min="0"
                    max="400"
                    step="1"
                    value={directionalPosition1.y}
                    onChange={(e) => updateDirectionalPosition1("y", e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <label>Z: {directionalPosition1.z}</label>
                  <input
                    type="range"
                    min="-300"
                    max="300"
                    step="1"
                    value={directionalPosition1.z}
                    onChange={(e) => updateDirectionalPosition1("z", e.target.value)}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* Directional Light 2 Controls */}
            <div>
              <label>Directional 2 Intensity: {directionalIntensity2}</label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={directionalIntensity2}
                onChange={(e) => setDirectionalIntensity2(parseFloat(e.target.value))}
                className="w-full mt-1"
              />
              <label>Color:</label>
              <input
                type="color"
                value={directionalColor2}
                onChange={(e) => setDirectionalColor2(e.target.value)}
                className="w-full mt-1"
              />
              <div className="mt-1">
                <div>
                  <label>X: {directionalPosition2.x}</label>
                  <input
                    type="range"
                    min="-300"
                    max="300"
                    step="1"
                    value={directionalPosition2.x}
                    onChange={(e) => updateDirectionalPosition2("x", e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <label>Y: {directionalPosition2.y}</label>
                  <input
                    type="range"
                    min="0"
                    max="400"
                    step="1"
                    value={directionalPosition2.y}
                    onChange={(e) => updateDirectionalPosition2("y", e.target.value)}
                    className="w-full"
                  />
                </div>
                <div>
                  <label>Z: {directionalPosition2.z}</label>
                  <input
                    type="range"
                    min="-300"
                    max="300"
                    step="1"
                    value={directionalPosition2.z}
                    onChange={(e) => updateDirectionalPosition2("z", e.target.value)}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 3D Viewer with Background Blur */}
      <div className="relative w-full h-full">
        {/* Background blur layer */}
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: "url('/path/to/your/background.jpg')",
            filter: "blur(8px)",
          }}
        />
        {/* Canvas with transparent background */}
        <Canvas
          shadows
          camera={{ position: [0, 150, 300], fov: 45 }}
          gl={{
            alpha: true,
            toneMapping: THREE.ACESFilmicToneMapping,
            outputEncoding: THREE.sRGBEncoding,
          }}
          className="w-full h-full relative"
          style={{ background: "transparent" }}
        >
          {/* Lighting using state values */}
          <ambientLight intensity={ambientIntensity} color={ambientColor} />
          <hemisphereLight
            skyColor={hemisphereSkyColor}
            groundColor={hemisphereGroundColor}
            intensity={hemisphereIntensity}
          />
          <directionalLight
            castShadow
            position={[
              directionalPosition1.x,
              directionalPosition1.y,
              directionalPosition1.z,
            ]}
            intensity={directionalIntensity1}
            color={directionalColor1}
            shadow-mapSize={{ width: 1024, height: 1024 }}
          />
          <directionalLight
            castShadow
            position={[
              directionalPosition2.x,
              directionalPosition2.y,
              directionalPosition2.z,
            ]}
            intensity={directionalIntensity2}
            color={directionalColor2}
            shadow-mapSize={{ width: 1024, height: 1024 }}
          />

          {/* Load the model with the current scale */}
          <Model modelData={modelData} scale={scale} />

          {/* OrbitControls with zoom disabled */}
          <OrbitControls ref={controlsRef} enableZoom={false} target={[0, 0, 0]} />
        </Canvas>
      </div>

      {/* Zoom Controls */}
      <div className="absolute bottom-4 right-4 flex flex-col space-y-2 z-10">
        <button
          onClick={handleIncrease}
          className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center text-xl"
        >
          +
        </button>
        <button
          onClick={handleDecrease}
          className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center text-xl"
        >
          –
        </button>
      </div>

      {/* X-Z Pan Controls (Diamond Layout) */}
      <div className="absolute bottom-4 left-4 z-10">
        <div className="flex flex-col items-center">
          <button
            onClick={panForward}
            className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center text-xl mb-1"
          >
            ↑
          </button>
          <div className="flex space-x-1">
            <button
              onClick={panLeft}
              className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center text-xl"
            >
              ←
            </button>
            <button
              onClick={panBackward}
              className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center text-xl"
            >
              ↓
            </button>
            <button
              onClick={panRight}
              className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center text-xl"
            >
              →
            </button>
          </div>
        </div>
      </div>

      {/* Y-Axis Pan Controls with Icons */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
        <div className="flex flex-col items-center space-y-2">
          <button
            onClick={panYUp}
            className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center"
          >
            <FaArrowCircleUp className="text-2xl" />
          </button>
          <button
            onClick={panYDown}
            className="w-10 h-10 bg-white rounded-full shadow hover:bg-gray-200 flex items-center justify-center"
          >
            <FaArrowCircleDown className="text-2xl" />
          </button>
        </div>
      </div>
    </div>
  );
}
