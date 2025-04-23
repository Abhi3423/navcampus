// store/useMapStore.js
import { create } from 'zustand';

const useMapStore = create((set) => ({
    formData: {
        source: '',
        target: '',
        Formsourcefloor: '',
        FormEndFloor: '',
        FormStartPosition: '',
        FormEndPosition: '',
        mode: 'walk',
        optimizer: 'length',
    },
    showAdvanced: false,
    mapHtml: '',
    info: '',
    sourcedataPoints: {},
    destinationdataPoints: {},
    ladmarks: {},
    display: false,
    modelData: undefined,
    startmodelData: undefined,
    endmodelData: undefined,
    nodes: undefined,

    // FloorView clicked values
    startFloor: '',
    endFloor: '',
    startPosition: '',
    endPosition: '',

    // Fixed values
    sourceFloor: '',
    targetFloor: '',
    sourcePosition: '',
    targetPosition: '',

    floorView: false,
    outdoorMap: true,
    landmark: '',
    buildings: [],


    // Indoor Map states
    mapImage: null,
    currentFloor: 'start',
    floorHeader: '',
    startFloorData: null,
    endFloorData: null,
    hasFetchedPath: false,

    // Setters
    setFormData: (newData) =>
        set((state) => ({
            formData: {
                ...state.formData,
                ...newData
            }
        })),
    setShowAdvanced: (showAdvanced) => set({ showAdvanced }),
    setMapHtml: (mapHtml) => set({ mapHtml }),
    setInfo: (info) => set({ info }),
    setSourceDataPoints: (sourcedataPoints) => set({ sourcedataPoints }),
    setDestinationDataPoints: (destinationdataPoints) => set({ destinationdataPoints }),
    setLandmarks: (ladmarks) => set({ ladmarks }),
    setDisplay: (display) => set({ display }),
    setModelData: (modelData) => set({ modelData }),
    setStartModelData: (startmodelData) => set({ startmodelData }),
    setEndModelData: (endmodelData) => set({ endmodelData }),
    setNodes: (nodes) => set({ nodes }),

    setStartFloor: (startFloor) => set({ startFloor }),
    setEndFloor: (endFloor) => set({ endFloor }),
    setStartPosition: (startPosition) => set({ startPosition }),
    setEndPosition: (endPosition) => set({ endPosition }),

    setSourceFloor: (sourceFloor) => set({ sourceFloor }),
    setTargetFloor: (targetFloor) => set({ targetFloor }),
    setSourcePosition: (sourcePosition) => set({ sourcePosition }),
    setTargetPosition: (targetPosition) => set({ targetPosition }),

    setFloorView: (floorView) => set({ floorView }),
    setOutdoorMap: (outdoorMap) => set({ outdoorMap }),
    setLandmark: (landmark) => set({ landmark }),
    setBuildings: (buildings) => set({ buildings }),

    setMapImage: (mapImage) => set({ mapImage }),
    setCurrentFloor: (currentFloor) => set({ currentFloor }),
    setFloorHeader: (floorHeader) => set({ floorHeader }),
    setStartFloorData: (startFloorData) => set({ startFloorData }),
    setEndFloorData: (endFloorData) => set({ endFloorData }),
    setHasFetchedPath: (value) => set({ hasFetchedPath: value }),
}));

export default useMapStore;
