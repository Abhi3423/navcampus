"use client";

import React from 'react'
import { Button, Card } from 'flowbite-react';

function Information() {
    return (
        <div className="p-4 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-6">📍 Hybrid Campus Navigation System Overview</h1>

            <Card className="mb-4 shadow-xl rounded-2xl">
                <div className="p-6">
                    <h2 className="text-xl font-semibold mb-2">🎯 What is this system?</h2>
                    <p className="text-base text-gray-700">
                        This system provides seamless navigation across both indoor and outdoor campus environments. It integrates openstreet for outdoor map paths and indoor positioning. The core pathfinding logic is powered by a hybrid RRT-Connect + Dijkstra’s algorithm.
                    </p>
                </div>
            </Card>

            <Card className="mb-4 shadow-xl rounded-2xl">
                <div className="p-6">
                    <h2 className="text-xl font-semibold mb-2">👥 Who uses this system?</h2>
                    <p className="text-base text-gray-700">
                        - <strong>Students/Visitors:</strong> Navigate across buildings and floors in real-time.<br />
                        - <strong>Admins:</strong> Maintain and update maps, nodes, and paths with a dedicated Python GUI Desktop.
                    </p>
                </div>
            </Card>

            <Card className="mb-4 shadow-xl rounded-2xl">
                <div className="p-6">
                    <h2 className="text-xl font-semibold mb-2">⚙️ How does it work?</h2>
                    <ul className="list-disc ml-6 text-base text-gray-700">
                        <li>Admin creates and updates maps using a GUI.</li>
                        <li>RRT-Connect finds multiple edges between nodes in parallel.</li>
                        <li>Dijkstra’s algorithm computes the shortest path dynamically.</li>
                        <li>Next.js frontend visualizes the route in both 2D and 3D.</li>
                        <li>3D models are rendered via Three.js from GLB files generated using Trimesh.</li>
                        <li>Floor transitions, landmarks, and obstacles are clearly visualized in 3D.</li>
                    </ul>
                </div>
            </Card>

            <Card className="mb-4 shadow-xl rounded-2xl">
                <div className="p-6">
                    <h2 className="text-xl font-semibold mb-2">👥 User Manual</h2>
                    <ul className="list-disc ml-6 text-base text-gray-700">
                        <li>Select the source and destination Landmarks.</li>
                        <li>Select the source and destination floor and positions.</li>
                        <li>Advanced Options like Mode and Optimizer can be selected to know more info.</li>
                        <li>Outdoor Path is shown, click over the locator icon to view the image of landmark and source coordinates.</li>
                        <li>Click Floor View to view indoor positioning and 3d view button to view 3d structure of floors.</li>
                    </ul>
                </div>
            </Card>

            <Card className="mb-4 shadow-xl rounded-2xl">
                <div className="p-6">
                    <h2 className="text-xl font-semibold mb-2">🛠️ Admin Dashboard</h2>
                    <p className="text-base text-gray-700">
                        The admin panel built with Python and Tkinter allows loading base maps, overlaying a grid, defining nodes, saving paths, and managing data via CRUD operations. The paths are optimized and stored in the supabase database.
                    </p>
                </div>
            </Card>

            <Card className="mb-6 shadow-xl rounded-2xl">
                <div className="p-6">
                    <h2 className="text-xl font-semibold mb-2">🔬 Research & Algorithms</h2>
                    <p className="text-base text-gray-700 mb-4">
                        The system's innovation lies in combining RRT-Connect for exploration with Dijkstra’s for optimization, achieving superior performance in dynamic and complex spaces.
                    </p>
                    <div className='flex gap-4'>
                        <Button
                            onClick={() => window.open("https://ieeexplore.ieee.org/document/10894337", "_blank")}
                        >
                            View IEEE Research Paper
                        </Button>
                        <Button
                            onClick={() => window.open("https://github.com/Abhi3423/navcampus", "_blank")}
                        >
                            View Github
                        </Button>
                    </div>

                </div>
            </Card>
        </div>
    );
}

export default Information
