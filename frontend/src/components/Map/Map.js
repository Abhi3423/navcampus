'use client';

import React, { useState } from "react";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";

function Map() {
    const [position, setPosition] = useState(null);

    const HandleMouseMovement = () => {
        useMapEvents({
            mousemove(e) {
                setPosition([e.latlng.lat, e.latlng.lng]);
                // console.log(e.latlng)
            },
        });
        return null;
    };

    

    return (
        <MapContainer style={{ height: "100%", width: "100%" }} center={[12.8197145, 80.0368125]} zoom={15} scrollWheelZoom={true}>
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <HandleMouseMovement />
            {/* {position && (
                <Marker position={position}>
                    <Popup>
                        Latitude: {position[0].toFixed(5)} <br /> Longitude: {position[1].toFixed(5)}
                    </Popup>
                </Marker>
            )} */}
        </MapContainer>
    );
}

export default Map;
