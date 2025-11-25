import React, { useState, useEffect } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

const TexasCountyMapTest: React.FC = () => {
    const [geoData, setGeoData] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        console.log("Starting to fetch simple test data...");
        fetch("/data/texas-simple.json")
            .then(response => {
                console.log("Response received:", response.status);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log("Simple GeoJSON loaded:", data);
                setGeoData(data);
            })
            .catch(err => {
                console.error("Failed to load simple data", err);
                setError(`Failed to load: ${err.message}`);
            });
    }, []);

    if (error) {
        return <div className="text-red-500 p-4">Error: {error}</div>;
    }

    if (!geoData) {
        return <div className="text-white p-4">Loading simple test map...</div>;
    }

    return (
        <div className="relative w-full h-[500px] bg-gray-900/30 rounded-2xl overflow-hidden border border-green-500">
            <div className="text-xs text-white bg-green-500/50 p-2 absolute top-0 left-0 z-10">
                TEST MAP: Loaded {geoData.features?.length || 0} features
            </div>

            <ComposableMap
                projection="geoMercator"
                projectionConfig={{
                    center: [-97, 31],
                    scale: 2000
                }}
                className="w-full h-full"
            >
                <Geographies geography={geoData}>
                    {({ geographies }) => {
                        console.log("Rendering geographies:", geographies.length);
                        return geographies.map((geo: any) => {
                            console.log("Rendering county:", geo.properties.name, geo.id);
                            return (
                                <Geography
                                    key={geo.rsmKey}
                                    geography={geo}
                                    fill="#10b981"
                                    stroke="#ffffff"
                                    strokeWidth={2}
                                    style={{
                                        default: { outline: 'none' },
                                        hover: { fill: '#fbbf24', outline: 'none' },
                                        pressed: { outline: 'none' }
                                    }}
                                />
                            );
                        });
                    }}
                </Geographies>
            </ComposableMap>
        </div>
    );
};

export default TexasCountyMapTest;
