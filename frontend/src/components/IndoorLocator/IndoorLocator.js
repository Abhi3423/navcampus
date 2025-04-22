'use client';

import { useEffect, useRef, useState, useCallback } from "react";
import * as THREE from "three";
import { CSS2DRenderer, CSS2DObject } from "three/examples/jsm/renderers/CSS2DRenderer";
import Image from "next/image";
import useMapStore from "@/utils/store/useMapStore";

export default function ImageWithOverlay({ mapImage }) {

    const {
        nodes
    } = useMapStore();


    const containerRef = useRef(null);
    const canvasRef = useRef(null);
    const [selectedNode, setSelectedNode] = useState(null);

    const X_OFFSET = -27;
    const Y_OFFSET = -10;

    const transformNodePosition = useCallback((backendX, backendY, imageWidth, imageHeight) => {
        const SCALE_X = imageWidth / 157;
        const SCALE_Y = imageHeight / 89;

        return {
            x: backendX * SCALE_X + X_OFFSET,
            y: imageHeight - (backendY * SCALE_Y + Y_OFFSET),
        };
    }, [X_OFFSET, Y_OFFSET]);

    useEffect(() => {

        if (!containerRef.current || !canvasRef.current) return;

        const container = containerRef.current;
        const width = container.clientWidth;
        const height = container.clientHeight;
        const canvasRefcur = canvasRef.current;

        const transformedNodes = Object.fromEntries(
            Object.entries(nodes).map(([name, [x, y]]) => [
                name,
                transformNodePosition(x, y, width, height),
            ])
        );

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(0, width, height, 0, -10, 10);
        camera.position.set(0, 0, 5);
        camera.lookAt(0, 0, 0);

        const renderer = new THREE.WebGLRenderer({ canvas: canvasRefcur, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(window.devicePixelRatio);

        const labelRenderer = new CSS2DRenderer();
        labelRenderer.setSize(width, height);
        labelRenderer.domElement.style.position = "absolute";
        labelRenderer.domElement.style.top = "0px";
        labelRenderer.domElement.style.pointerEvents = "none";
        container.appendChild(labelRenderer.domElement);

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const objects = [];

        const drawNode = (x, y, label) => {
            const circleGeometry = new THREE.CircleGeometry(5, 32);
            const circleMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const circleMesh = new THREE.Mesh(circleGeometry, circleMaterial);
            circleMesh.position.set(x, y, 0);
            scene.add(circleMesh);
            objects.push({ mesh: circleMesh, label });

            const labelDiv = document.createElement("div");
            labelDiv.className = "node-label";
            labelDiv.textContent = label;
            labelDiv.style.color = "white";
            labelDiv.style.fontSize = "13px";
            labelDiv.style.fontWeight = "bold";
            labelDiv.style.padding = "2px 5px";
            labelDiv.style.background = "rgba(0, 0, 0, 0.7)";
            labelDiv.style.borderRadius = "3px";
            labelDiv.style.whiteSpace = "nowrap";

            const labelObject = new CSS2DObject(labelDiv);
            labelObject.position.set(x - 10, y + 20, 10);
            scene.add(labelObject);
        };

        Object.entries(transformedNodes).forEach(([label, { x, y }]) => {
            drawNode(x, y, label);
        });

        const onClick = (event) => {
            const rect = canvasRef.current.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(objects.map((obj) => obj.mesh));

            if (intersects.length > 0) {
                const clickedNode = objects.find((obj) => obj.mesh === intersects[0].object);
                if (clickedNode) {
                    const worldPosition = new THREE.Vector3();
                    clickedNode.mesh.getWorldPosition(worldPosition);
                    worldPosition.project(camera);

                    const screenX = ((worldPosition.x + 1) / 2) * width;
                    const screenY = ((1 - worldPosition.y) / 2) * height;

                    setSelectedNode({ label: clickedNode.label, screenX, screenY });
                }
            }
        };


        canvasRefcur.addEventListener("click", onClick);

        const animate = () => {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
            labelRenderer.render(scene, camera);
        };
        animate();

        return () => {
            if (canvasRefcur) {
                canvasRefcur.removeEventListener("click", onClick);
            }
            renderer.dispose();
        };

    }, [mapImage, nodes, transformNodePosition]);

    return (
        <div ref={containerRef} className="relative w-full h-[80vh]">
            <Image src={mapImage} alt="Map with Path" layout="fill" className="absolute inset-0 object-cover" />
            <canvas ref={canvasRef} className="absolute inset-0" />

            {selectedNode && (
                <div
                    className="absolute bg-white p-2 rounded shadow-lg z-50"
                    style={{
                        left: `${selectedNode.screenX}px`,
                        top: `${selectedNode.screenY - 50}px`,
                        transform: "translate(-50%, -100%)",
                        width: "150px",
                    }}
                >
                    <div className="flex flex-col gap-2">
                        <div className="flex flex-row gap-1 text-center">
                            <div className="text-sm font-semibold w-full">
                                {selectedNode.label.startsWith("TP") ? "Classroom" : selectedNode.label}
                            </div>
                            <button className="rounded-md border-2 w-6 h-6 border-black text-xs text-black right-0" onClick={() => setSelectedNode(null)}>
                                X
                            </button>
                        </div>
                        <Image
                            src={`/assets/classroom.jpeg`}
                            alt={selectedNode.label}
                            width={150}
                            height={100}
                            className="rounded"
                        />
                    </div>
                </div>
            )}

        </div>
    );
}
