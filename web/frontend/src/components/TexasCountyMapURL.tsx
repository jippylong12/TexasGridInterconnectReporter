import React from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

const TexasCountyMapURL: React.FC = () => {
    // Use URL directly - react-simple-maps should handle TopoJSON conversion
    const geoUrl = "/data/counties-10m.json";

    return (
        <div className="relative w-full h-[500px] bg-gray-900/30 rounded-2xl overflow-hidden border border-blue-500">
            <div className="text-xs text-white bg-blue-500/50 p-2 absolute top-0 left-0 z-10">
                URL-based approach: {geoUrl}
            </div>

            <ComposableMap
                projection="geoAlbers"
                projectionConfig={{
                    scale: 2500,
                    center: [-99, 31.5],
                }}
                className="w-full h-full"
            >
                <Geographies geography={geoUrl} parseGeographies={(geos: any) => {
                    console.log("Parsed geographies from URL:", geos);
                    // Filter for Texas counties
                    return geos.filter((geo: any) => geo.id && geo.id.toString().startsWith('48'));
                }}>
                    {({ geographies }) => {
                        console.log("Rendering from URL:", geographies.length, "counties");
                        return geographies.map((geo: any) => (
                            <Geography
                                key={geo.rsmKey}
                                geography={geo}
                                fill="#ef4444"
                                stroke="#ffffff"
                                strokeWidth={0.5}
                                style={{
                                    default: { outline: 'none' },
                                    hover: { fill: '#fbbf24', outline: 'none' },
                                    pressed: { outline: 'none' }
                                }}
                            />
                        ));
                    }}
                </Geographies>
            </ComposableMap>
        </div>
    );
};

export default TexasCountyMapURL;
