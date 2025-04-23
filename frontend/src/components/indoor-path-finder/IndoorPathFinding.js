'use client';

import { useState, useEffect, useCallback } from "react";
import { INTERNAL_PATH_URL } from "@/utils/constants/const";
import ImageWithOverlay from "../IndoorLocator/IndoorLocator";
import Loader from "@/UI/loader";
import useMapStore from "@/utils/store/useMapStore";

export default function PathfindingClient() {

    const {
        landmark,
        startFloor,
        endFloor,
        startPosition,
        endPosition,
        setFloorView,
        outdoorMap,
        setDisplay,
        setModelData,
        nodes,
        setNodes,
        setStartModelData,
        setEndModelData,
        mapImage,
        setMapImage,
        currentFloor,
        setCurrentFloor,
        floorHeader,
        setFloorHeader,
        startFloorData,
        setStartFloorData,
        endFloorData,
        setEndFloorData,
        hasFetchedPath,
        setHasFetchedPath
    } = useMapStore();


    const displayFloor = useCallback((floorData) => {
        setMapImage(`data:image/png;base64,${floorData.image}`);
        setFloorHeader(`Floor ${floorData.floor}`);
        setNodes(floorData.node);
        setModelData(`data:model/gltf-binary;base64,${floorData.modelData}`);
    }, [setMapImage, setFloorHeader, setNodes, setModelData]);


    const showNextFloor = () => {
        if (currentFloor === "start" && endFloorData) {
            displayFloor(endFloorData);
            setCurrentFloor("end");
        }
    };

    const showPrevFloor = () => {
        if (currentFloor === "end" && startFloorData) {
            displayFloor(startFloorData);
            setCurrentFloor("start");
        }
    };

    useEffect(() => {

        console.log(startFloor);
        if (hasFetchedPath) return;

        
        const fetchData = async () => {
            if (startFloor && endFloor && startPosition && endPosition) {
                try {
                    const response = await fetch(`${INTERNAL_PATH_URL}/api/path`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            start: startPosition,
                            end: endPosition,
                            start_floor: startFloor,
                            end_floor: endFloor,
                            landmark: landmark,
                            get3d: true
                        }),
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }

                    const result = await response.json();

                    console.log(result);

                    if (result) {
                        setHasFetchedPath(true);
                        if (result.start_floor && result.end_floor) {
                            setStartFloorData(result.start_floor);
                            setEndFloorData(result.end_floor);
                            displayFloor(result.start_floor);
                            setNodes(result.start_floor.node);
                            setModelData(`data:model/gltf-binary;base64,${result.start_floor.modelData}`);

                            const startFloorNumber = Number(result.start_floor.floor);
                            const endFloorNumber = Number(result.end_floor.floor);

                            if (startFloorNumber > endFloorNumber) {
                                setStartModelData(`data:model/gltf-binary;base64,${result.start_floor.modelData}`);
                                setEndModelData(`data:model/gltf-binary;base64,${result.end_floor.modelData}`);
                            } else {
                                setStartModelData(`data:model/gltf-binary;base64,${result.end_floor.modelData}`);
                                setEndModelData(`data:model/gltf-binary;base64,${result.start_floor.modelData}`);
                            }
                            setCurrentFloor("start");
                        } else if (result.start_end_floor) {
                            setNodes(result.start_end_floor.node);
                            setMapImage(`data:image/png;base64,${result.start_end_floor.image}`);
                            setFloorHeader(`Floor ${result.start_end_floor.floor}`);
                            setModelData(result.start_end_floor.modelData);
                        }
                    } else {
                        alert(result.error || "Path not found.");
                    }
                } catch (error) {
                    console.error("Error running Dijkstra:", error);
                }
            }
        };

        fetchData();

    }, [landmark]);


    return (
        <div className="flex flex-col w-[100%] h-[100vh] overflow-hidden p-2">
            <div className="flex flex-row gap-10">
                {
                    outdoorMap ? (
                        <button
                            className="bg-black text-white px-4 py-2 m-2 w-60 rounded-md"
                            onClick={() => setFloorView(false)}
                        >
                            ←  Back to Outdoor Map
                        </button>
                    ) : <div />
                }

                <button
                    className="bg-black text-white px-4 py-2 m-2 w-60 rounded-md"
                    onClick={() => setDisplay(true)}
                >
                    Show 3d View
                </button>
            </div>

            {
                mapImage ? (
                    <div className="flex flex-row h-[50vh] md:h-[90%] items-center justify-center">
                        <div className="p-3 cursor-pointer text-4xl font-bold hover:text-green-500" onClick={showPrevFloor}>
                            &#8592;
                        </div>
                        <div className="flex flex-col gap-2 text-center justify-center items-center relative w-full h-full">
                            <div className="text-3xl font-bold mb-4">{floorHeader}</div>
                            {mapImage && <ImageWithOverlay key={currentFloor} mapImage={mapImage} />}
                        </div>
                        <div className="p-3 cursor-pointer text-4xl font-bold hover:text-green-500" onClick={showNextFloor}>
                            &#8594;
                        </div>
                    </div>
                ) :
                    <div className="flex w-full h-full items-center justify-center">
                        <Loader />
                    </div>
            }
        </div>
    );
}
