import { INTERNAL_PATH_URL } from "../constants/const";
import useMapStore from "../store/useMapStore";

const useMapActions = () => {
  const {
    setSourceDataPoints,
    setDestinationDataPoints,
    setBuildings,
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


  return {
    fetchDataPoints,
    fetchLandmarks,
  };
};

export default useMapActions;
