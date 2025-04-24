import { INTERNAL_PATH_URL } from "../constants/const";
import useMapStore from "../store/useMapStore";

const useMapActions = () => {
  const {
    setSourceDataPoints,
    setDestinationDataPoints,
    setBuildings,
    startFloorData,
    endFloorData,
    mapImage,
    setStartModelData,
    setEndModelData,
    hasFetchedModel,
    setHasFetchedModel,
    setDisplay,
    setLoading3d,
    landmark
  } = useMapStore();


  //   Fetch Source and Target Floors on selecting building name
  const fetchDataPoints = async (id, landmark) => {
    try {
      const response = await fetch(`${INTERNAL_PATH_URL}/api/nodes?landmark=${encodeURIComponent(landmark)}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();
      console.log(data);

      if (id === "source") setSourceDataPoints(data);
      else if (id === "target") setDestinationDataPoints(data);
    } catch (error) {
      console.error("Error fetching data points:", error);
    }
  };



  // Fetch Source and Target Building on Loading of Page
  const fetchLandmarks = async () => {
    try {
      const response = await fetch(`${INTERNAL_PATH_URL}/api/get_landmarks`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();
      console.log(data.landmarks);
      setBuildings(data.landmarks);
    } catch (error) {
      console.error("Error fetching landmarks:", error);
    }
  };



  // Converting 2d Image data into 3d model
  const Get3dModel = async () => {

    if (hasFetchedModel) {
      setDisplay(true);
      return;
    }
    

    try {
      
      setLoading3d(true);

      // Prepare the payload from start and end floor data
      var payload = {}
      if (endFloorData == null) {
        payload = {
          "1": {"floor": startFloorData?.floor, "image": startFloorData?.image, "landmark": landmark}
        };
      } else {
        payload = {
          "1": {"floor": startFloorData?.floor, "image": startFloorData?.image, "landmark": landmark},
          "2": {"floor": endFloorData?.floor, "image": endFloorData?.image, "landmark": landmark}
        };
      }

      const response = await fetch(`${INTERNAL_PATH_URL}/api/get_model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }

      const responseData = await response.json();

      if (responseData) {
        
        setLoading3d(false);
        setHasFetchedModel(true);
        setDisplay(true);

        if (startFloorData == null) {
          setStartModelData(`data:model/gltf-binary;base64,${responseData[1]}`);
        }
        else {
          const startFloorNumber = Number(startFloorData.floor);
          const endFloorNumber = Number(endFloorData.floor);

          if (startFloorNumber > endFloorNumber) {
            setStartModelData(`data:model/gltf-binary;base64,${responseData[1]}`);
            setEndModelData(`data:model/gltf-binary;base64,${responseData[2]}`);
          } else {
            setStartModelData(`data:model/gltf-binary;base64,${responseData[2]}`);
            setEndModelData(`data:model/gltf-binary;base64,${responseData[1]}`);
          }
        }
      }

    } catch (error) {
      console.error("Error fetching 3D model:", error);
    }
  };



  return {
    fetchDataPoints,
    fetchLandmarks,
    Get3dModel
  };
};

export default useMapActions;
