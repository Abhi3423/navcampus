'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.awesome-markers/dist/leaflet.awesome-markers.css';
import L from 'leaflet';
import 'leaflet.awesome-markers';
import { motion } from "framer-motion";
import useMapStore from "@/utils/store/useMapStore";

const MapComponent = ({
  source, target
}) => {

  const {
    mapHtml, setFloorView, setLandmark, setStartFloor, setEndFloor, setStartPosition, setEndPosition,
    sourceFloor, targetFloor, sourcePosition, targetPosition
  } = useMapStore();


  const [markers, setMarkers] = useState([]);
  const [polylines, setPolylines] = useState([]);
  const [bounds, setBounds] = useState(null);
  const [mapCenter, setMapCenter] = useState([12.823835016257402, 80.04490741001594]);
  const [showPosition, setShowPosition] = useState({});
  const [tooltipContent, settooltipContent] = useState();

  useEffect(() => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(mapHtml, 'text/html');

    const extractedMarkers = [];
    const extractedPolylines = [];
    const extractedPolylineNames = [];
    const extractedTooltips = [];
    let extractedBounds = null;

    const mapScriptContent = Array.from(doc.querySelectorAll('script')).map(script => script.textContent).join('');

    // Extract markers
    const markerMatches = mapScriptContent.match(/L\.marker\((.*?)\)\.addTo\(.*?\.bindPopup\((.*?)\);/gs);

    if (markerMatches) {
      markerMatches.forEach((match, idx) => {
        const positionMatch = match.match(/L\.marker\s*\(\s*\[(.*?)\]/);
        const setContentMatch = match.match(/\.setContent\((.*?)\)/);
        const iconOptionsMatch = match.match(/L.AwesomeMarkers.icon\((.*?)\)/s);
        const tooltipContentMatch = match.match(/\.bindTooltip\((.*?)\)/s);

        if (positionMatch && setContentMatch && iconOptionsMatch && tooltipContentMatch) {
          const position = positionMatch[1].split(',').map(parseFloat);
          const variableName = setContentMatch[1].trim(); // Get the variable name (e.g., i_frame_xyz)

          // Extract the iframe definition associated with the variable
          const iframeDefinitionRegex = new RegExp(
            `var\\s+${variableName}\\s*=\\s*\\$\\(\`<iframe(.*?)>\\\`\\)\\[0\\];`,
            's'
          );

          const iframeMatch = mapScriptContent.match(iframeDefinitionRegex);

          let iframeSrc = '';

          if (iframeMatch) {
            const iframeContent = iframeMatch[1];
            const srcMatch = iframeContent.match(/src=["']([^"']*)["']/); // Extract the src attribute
            iframeSrc = srcMatch ? srcMatch[1] : '';

          }

          let iconOptions = {};
          try {
            const iconOptionsString = iconOptionsMatch[1];

            iconOptions = JSON.stringify(iconOptionsString);
          } catch (error) {
            console.error('Error parsing icon options:', error);
          }

          const tooltipHtmlMatch = tooltipContentMatch[1].match(/<div>\s*([\s\S]*?)\s*<\/div>/);
          const tooltipHtml = tooltipHtmlMatch ? tooltipHtmlMatch[1].trim() : null;


          extractedMarkers.push({
            id: idx,
            position,
            popupHtml: iframeSrc,
            iconOptions,
            tooltipHtml
          });
        }
      });
    }


    // Step 1: Extract polylines and their variable names
    const polylineMatches = mapScriptContent.match(/var (\w+) = L\.polyline\(\s*\[(.*?)\],\s*\{(.*?)\}\s*\)\.addTo\(.*?\);/gs);

    if (polylineMatches) {
      polylineMatches.forEach((match) => {
        // Extract polyline variable name
        const variableMatch = match.match(/var (\w+) =/);
        // Extract coordinates
        const coordinatesMatch = match.match(/\[\s*\[.*?\]\s*\]/);
        if (variableMatch && coordinatesMatch) {
          const polylineVar = variableMatch[1]; // Example: poly_line_0007da1872ec32b85297ee7761e9ffb4
          const coordinates = JSON.parse(coordinatesMatch[0]);
          extractedPolylines.push(coordinates);
          extractedPolylineNames.push({ name: polylineVar })
        }
      });

      // Step 2: Extract tooltips using the variable names
      extractedPolylineNames.forEach(({ name }) => {
        const tooltipRegex = new RegExp(`${name}\\.bindTooltip\\(\\s*\\\`<div>\\s*([\\s\\S]*?)\\s*<\\/div>\\\``, 's');
        const tooltipMatch = mapScriptContent.match(tooltipRegex);

        if (tooltipMatch) {
          const rawTooltip = tooltipMatch[1].trim();

          // Step 1: Decode HTML entities
          let decodedTooltip = new DOMParser().parseFromString(rawTooltip, "text/html").body.textContent;

          // Step 2: Ensure proper UTF-8 handling (fix malformed characters)
          extractedTooltips.push(decodedTooltip);

        } else {
          extractedTooltips.push(""); // Default empty tooltip if not found
        }
      });
    }

    // Extract bounds
    const boundsMatch = Array.from(doc.querySelectorAll('script')).map(script => script.textContent).join('').match(/map_.*?\.fitBounds\(\[(.*?)\],.*?\);/);

    if (boundsMatch) {
      extractedBounds = JSON.parse(boundsMatch[1]);
    }

    setMarkers(extractedMarkers);
    setPolylines(extractedPolylines);
    settooltipContent(extractedTooltips);
    setBounds(extractedBounds);
  }, [mapHtml]);


  const createAwesomeMarkerIcon = (options) => {

    try {
      let cleanedOptions = options
        .replace(/\\n/g, "") // Remove all newline escape sequences
        .replace(/\\t/g, "") // Remove all tab escape sequences
        .replace(/\\"/g, '"') // Convert escaped quotes to actual double quotes (ensure JSON format)
        .trim() // Remove leading and trailing spaces
        .replace(/\s+/g, " ") // Collapse multiple spaces into one
        .replace(/,\s*(}|\])/g, "$1"); // Remove trailing commas before closing braces or brackets

      // Replace only the starting and ending double quotes with single quotes
      cleanedOptions = cleanedOptions.replace(/^"/, " ").replace(/"$/, " ");

      // Parse the cleaned string into an object
      const parsedOptions = JSON.parse(cleanedOptions);

      return L.AwesomeMarkers.icon({
        ...parsedOptions
      });
    } catch (error) {
      console.error('Error parsing options:', error);
      return null; // Handle error gracefully
    }
  };

  const settingValues = (landmarkName) => {
    let name = landmarkName;

    if (typeof landmarkName === "string" && landmarkName.includes("<div")) {
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = landmarkName;
      name = tempDiv.innerText.trim(); // Extracts the inner text
    }

    if (name == source) {
      setStartFloor(sourceFloor);
      setStartPosition(sourcePosition);
      setEndFloor("0");
      setEndPosition("Gate");

    } else if (name == target) {
      setStartFloor("0");
      setStartPosition("Gate");
      setEndFloor(targetFloor);
      setEndPosition(targetPosition);

    } else {
      // Handle other cases
    }
    setLandmark(name);
    setFloorView(true);
  };


  const togglePosition = (id) => {
    setShowPosition((prev) => ({ ...prev, [id]: !prev[id] }));
  };


  return (
    <MapContainer center={mapCenter} zoom={18} style={{ width: '100%', height: '100vh' }} bounds={[[12.8230452, 80.0448063], [12.8244558, 80.0451824]]}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='Data by <a href="http://openstreetmap.org">OpenStreetMap</a>'
      />
      {markers.map((marker, idx) => (
        <Marker
          key={idx}
          position={marker.position}
          icon={createAwesomeMarkerIcon(marker.iconOptions)}
        >
          <Popup style={{ 'width': '400px' }}>
            <div className='flex flex-col gap-2 items-center'>

              {/* Info button in top-left corner */}
              <button
                className='absolute top-1 left-1 bg-gray-300 text-black rounded-full w-6 h-6 flex items-center justify-center'
                onClick={() => togglePosition(marker.id)}
              >
                i
              </button>

              {/* Animated position display */}
              {showPosition[marker.id] && (
                <motion.div
                  className="ml-4 text-blue"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -50 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className='flex flex-col gap-1'>
                    <div>Coordinates</div>
                    <div>{marker.position.join(", ")}</div>
                  </div>
                </motion.div>
              )}

              {marker.popupHtml && (
                <iframe
                  src={marker.popupHtml}
                  width="270px"
                  height="220px"
                  style={{ border: 'none' }}
                ></iframe>
              )}

              <button className='w-40 h-10 rounded-md bg-blue text-white' onClick={() => { settingValues(marker.tooltipHtml) }}>Floor View</button>

            </div>

          </Popup>
          <Tooltip>
            <div dangerouslySetInnerHTML={{ __html: marker.tooltipHtml }} />
          </Tooltip>
        </Marker>
      ))}
      {polylines.map((polyline, idx) => (
        <Polyline key={idx} positions={polyline} color="blue">
          <Tooltip sticky>
            <div style={{ fontSize: "12px" }} dangerouslySetInnerHTML={{ __html: tooltipContent[idx] }} />
          </Tooltip>
        </Polyline>
      ))}
    </MapContainer>
  );
};

export default MapComponent;
