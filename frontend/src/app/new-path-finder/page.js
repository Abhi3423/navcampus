'use client'
import React from 'react'
import { useEffect } from 'react';
import Map from '../../components/Map'
import DynamicMapComponent from '@/components/OutsideMap/DynamicMapComponent';
import { EXTERNAL_PATH_URL } from '@/utils/constants/const';
import PathfindingClient from '../../components/indoor-path-finder/IndoorPathFinding';
import dynamic from "next/dynamic";
import useMapStore from '@/utils/store/useMapStore';
import useMapActions from '@/utils/hooks/useMapActions';

const NewDisplay = dynamic(() => import("@/components/ThreeD/newdisplay"), { ssr: false });

function Pathfinder() {
    const {
        formData,
        setFormData,

        showAdvanced,
        setShowAdvanced,

        mapHtml,
        setMapHtml,

        info,
        setInfo,

        sourcedataPoints,
        destinationdataPoints,
 
        display,

        setStartFloor,
        setEndFloor,
        setStartPosition,
        setEndPosition,

        sourceFloor,
        setSourceFloor,

        targetFloor,
        setTargetFloor,

        setSourcePosition,
        setTargetPosition,

        floorView,
        setFloorView,

        setOutdoorMap,
        setLandmark,

        buildings

    } = useMapStore();

    const { fetchDataPoints, fetchLandmarks } = useMapActions();

    // Function to handle changes in form inputs
    const handleInputChange = (e) => {
        const { id, value } = e.target;
        setFormData({ [id]: value });

        if (id === "source" || id === "target") {
            fetchDataPoints(id, value);
        }
    };


    // Function to handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (formData.source === formData.target) {
            setStartFloor(formData.Formsourcefloor);
            setEndFloor(formData.FormEndFloor);
            setStartPosition(formData.FormStartPosition);
            setEndPosition(formData.FormEndPosition);
            setLandmark(formData.source);
            setFloorView(true);
            setOutdoorMap(false);
        } else {
            try {
                console.log(formData)
                const response = await fetch(`${EXTERNAL_PATH_URL}/api/distance`, {
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                console.log(formData)
                const responseData = await response.json();
                setMapHtml(responseData.html_content);
                setInfo(responseData.info)
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
    }


    useEffect(() => {
        let isMounted = false;

        fetchLandmarks();
        isMounted = true;

        return () => {
            isMounted = true;
        };
    }, []);



    const labelCSS = 'block mb-2 text-sm font-medium text-gray-900 dark:text-white'
    const selectCSS = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'

    return (
        <div className='flex flex-col md:flex-row  w-[100%] md:h-[100vh]'>
            <div className='flex flex-col md:flex-row  w-[100%] md:h-[100vh]'>
                <div className='overflow-y-scroll flex flex-col gap-3 items-center text-center p-2 rounded-r-lg bg-white drop-shadow-lg shadow-lg w-[100%] md:w-[20%]'>
                    <div className='w-full rounded-md text-white font-bold text-2xl py-3 font-sans bg-blue'>Path Finder</div>
                    <div className='bg-blue py-3 text-white rounded-md w-full'>
                        <form onSubmit={handleSubmit} className="max-w-sm mx-auto px-4 py-2 flex flex-col gap-3">
                            <div>
                                <label htmlFor="source" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                    Select Source
                                </label>
                                <select id="source" onChange={handleInputChange} className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    <option >Choose a source</option>
                                    {buildings.map((building, index) => (
                                        <option key={index} value={building}>
                                            {building}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label htmlFor="target" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                    Select Destination
                                </label>
                                <select id="target" onChange={handleInputChange} className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    <option >Choose a destination</option>
                                    {buildings.map((building, index) => (
                                        <option key={index} value={building}>
                                            {building}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex justify-around gap-2">
                                <div className='flex-1'>
                                    <label htmlFor="Formsourcefloor" className={`${labelCSS}`}>Source <br /> Floor</label>
                                    <select
                                        className={`${selectCSS}`}
                                        onChange={(e) => {
                                            handleInputChange(e);
                                            setSourceFloor(e.target.value);
                                        }}
                                        id="Formsourcefloor"
                                    >
                                        <option value="">Select</option>
                                        {Object.keys(sourcedataPoints).map((floor) => (
                                            <option key={floor} value={floor}>
                                                Floor {floor}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className='flex-1'>
                                    <label htmlFor="FormStartPosition" className={`${labelCSS}`}>Source <br /> Position</label>
                                    <select
                                        className={`${selectCSS}`}
                                        onChange={(e) => {
                                            handleInputChange(e);
                                            setSourcePosition(e.target.value);
                                        }}
                                        id="FormStartPosition"
                                    >
                                        <option value="">Select</option>
                                        {sourcedataPoints[sourceFloor] && Object.keys(sourcedataPoints[sourceFloor]).map((node) => (
                                            <option key={node} value={node}>
                                                {node}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                            <div className="flex justify-around gap-2">
                                <div className='flex-1'>
                                    <label htmlFor="FormEndFloor" className={`${labelCSS}`}>Destination <br /> Floor</label>
                                    <select
                                        className={`${selectCSS}`}
                                        onChange={(e) => {
                                            handleInputChange(e);
                                            setTargetFloor(e.target.value);
                                        }}
                                        id="FormEndFloor"
                                    >
                                        <option value="">Select</option>
                                        {Object.keys(destinationdataPoints).map((floor) => (
                                            <option key={floor} value={floor}>
                                                Floor {floor}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className='flex-1'>
                                    <label htmlFor="FormEndPosition" className={`${labelCSS}`}>Destination <br /> Position</label>
                                    <select
                                        className={`${selectCSS}`}
                                        onChange={(e) => {
                                            handleInputChange(e);
                                            setTargetPosition(e.target.value);
                                        }}
                                        id="FormEndPosition"
                                    >
                                        <option value="">Select</option>
                                        {destinationdataPoints[targetFloor] && Object.keys(destinationdataPoints[targetFloor]).map((node) => (
                                            <option key={node} value={node}>
                                                {node}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="flex items-center space-x-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        name="advancedOptions"
                                        value="enabled"
                                        checked={showAdvanced}
                                        onChange={() => setShowAdvanced(!showAdvanced)}
                                        className="w-4 h-4 rounded-md"
                                    />
                                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                                        Advanced Options
                                    </span>
                                </label>
                            </div>

                            {showAdvanced && (
                                <div className="space-y-2">
                                    <div>
                                        <label htmlFor="mode" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                            Mode
                                        </label>
                                        <select id="mode" onChange={handleInputChange} className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                            <option >Choose a mode</option>
                                            <option value="walk">Walk</option>
                                            <option value="bike">Bike</option>
                                            <option value="drive">Drive</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label htmlFor="optimizer" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                            Optimizer
                                        </label>
                                        <select id="optimizer" onChange={handleInputChange} className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                            <option >Choose a optimizer</option>
                                            <option value="length">Length</option>
                                            <option value="time">Time</option>
                                        </select>
                                    </div>

                                </div>
                            )}

                            <div>
                                <button type="submit" className="text-white bg-gradient-to-r from-green-400 via-green-500 to-green-600 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-green-300 dark:focus:ring-green-800 font-medium rounded-lg text-sm px-10 py-3 text-center me-2 my-2">Find Path</button>
                            </div>
                        </form>
                    </div>
                    <div>
                        {
                            info == "" ? <div>Please Select Your Source and Target</div> : <div>{info}</div>
                        }
                    </div>
                </div>
                <div className='md:w-[80%] h-[50vh] md:h-[100vh]'>
                    {
                        !floorView ? (
                            mapHtml === '' ? (
                                <Map />
                            ) : (
                                <DynamicMapComponent
                                    source={formData.source}
                                    target={formData.target}
                                />
                            )
                        ) : display ? (
                            <NewDisplay />
                        ) : (
                            <PathfindingClient />
                        )
                    }
                </div>
            </div>

        </div>
    )
}

export default Pathfinder
