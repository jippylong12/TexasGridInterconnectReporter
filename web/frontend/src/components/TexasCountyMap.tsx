import React, { useState } from 'react';
import { ComposableMap, Geographies, Geography, ZoomableGroup } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';
import { motion, AnimatePresence } from 'framer-motion';

interface CountyData {
    county: string;
    total_mw: number;
    project_count: number;
    fuel_summary: string;
}

interface TexasCountyMapProps {
    data: CountyData[];
    onCountyClick: (county: string) => void;
}

const TexasCountyMap: React.FC<TexasCountyMapProps> = ({ data, onCountyClick }) => {
    const [hoveredCounty, setHoveredCounty] = useState<CountyData | null>(null);
    const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

    // Use URL directly - react-simple-maps handles TopoJSON conversion
    const geoUrl = "/data/counties-10m.json";

    // Create a map of county name to data
    const countyDataMap = new Map(
        data.map(d => [d.county.toUpperCase().replace(' COUNTY', ''), d])
    );

    // Calculate color scale
    const maxMW = Math.max(...data.map(d => d.total_mw), 1);
    const colorScale = scaleLinear<string>()
        .domain([0, maxMW / 2, maxMW])
        .range(['#10b981', '#fbbf24', '#ef4444']); // green -> yellow -> red


    const getCountyColor = (geo: any): string => {
        const countyName = geo.properties.name?.toUpperCase();
        const countyData = countyDataMap.get(countyName);
        if (!countyData) return '#374151'; // gray-700 for no data
        return colorScale(countyData.total_mw);
    };

    const handleCountyMouseEnter = (geo: any, event: React.MouseEvent) => {
        const countyName = geo.properties.name?.toUpperCase();
        const countyData = countyDataMap.get(countyName);
        if (countyData) {
            setHoveredCounty(countyData);
            setTooltipPos({
                x: event.clientX,
                y: event.clientY
            });
        }
    };

    const handleCountyMouseMove = (event: React.MouseEvent) => {
        setTooltipPos({
            x: event.clientX,
            y: event.clientY
        });
    };

    const handleCountyMouseLeave = () => {
        setHoveredCounty(null);
    };

    const handleCountyClick = (geo: any) => {
        const countyName = geo.properties.name?.toUpperCase();
        const countyData = countyDataMap.get(countyName);
        if (countyData) {
            onCountyClick(countyData.county);
        }
    };


    return (
        <div className="w-full h-[600px] bg-gray-100 rounded-xl overflow-hidden border border-gray-200 relative">
            <ComposableMap
                projection="geoMercator"
                projectionConfig={{
                    scale: 4000,
                    center: [-99.5, 31.5]
                }}
                className="w-full h-full"
                // Explicit large viewbox to ensure map visibility
                viewBox="0 0 1000 800"
            >
                <ZoomableGroup center={[-100, 31]} zoom={1} minZoom={0.8} maxZoom={4}>
                    <Geographies
                        geography={geoUrl}
                    >
                        {({ geographies }: { geographies: any[] }) => {
                            // Filter for Texas counties (FIPS code starts with 48)
                            const texasGeos = geographies.filter((geo: any) => geo.id && geo.id.toString().startsWith('48'));
                            return texasGeos.map((geo: any) => (
                                <Geography
                                    key={geo.rsmKey}
                                    geography={geo}
                                    fill={getCountyColor(geo)}
                                    stroke="#1f2937"
                                    strokeWidth={0.5}
                                    style={{
                                        default: { outline: 'none' },
                                        hover: {
                                            fill: getCountyColor(geo),
                                            opacity: 0.8,
                                            outline: 'none',
                                            cursor: 'pointer'
                                        },
                                        pressed: { outline: 'none' }
                                    }}
                                    onMouseEnter={(event: React.MouseEvent) => handleCountyMouseEnter(geo, event)}
                                    onMouseMove={(event: React.MouseEvent) => handleCountyMouseMove(event)}
                                    onMouseLeave={handleCountyMouseLeave}
                                    onClick={() => handleCountyClick(geo)}
                                />
                            ));
                        }}
                    </Geographies>
                </ZoomableGroup>
            </ComposableMap>


            {/* Tooltip */}
            <AnimatePresence>
                {hoveredCounty && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="fixed z-50 pointer-events-none"
                        style={{
                            left: tooltipPos.x + 10,
                            top: tooltipPos.y + 10,
                        }}
                    >
                        <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-3 max-w-xs">
                            <h4 className="font-bold text-white mb-1">{hoveredCounty.county} County</h4>
                            <div className="text-sm space-y-1">
                                <p className="text-gray-300">
                                    <span className="text-primary font-semibold">{hoveredCounty.total_mw} MW</span>
                                </p>
                                <p className="text-gray-400">{hoveredCounty.project_count} projects</p>
                                <p className="text-gray-400 text-xs">{hoveredCounty.fuel_summary}</p>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Legend */}
            <div className="absolute bottom-4 left-0 right-0 flex items-center justify-center gap-4 pointer-events-none">
                <div className="bg-gray-900/80 backdrop-blur-sm p-2 rounded-full flex items-center gap-4 border border-gray-700">
                    <span className="text-xs text-gray-400">Low MW</span>
                    <div className="flex h-2 w-32 rounded-full overflow-hidden">
                        <div className="flex-1" style={{ background: 'linear-gradient(to right, #10b981, #fbbf24, #ef4444)' }} />
                    </div>
                    <span className="text-xs text-gray-400">High MW</span>
                </div>
            </div>
        </div>
    );
};

export default TexasCountyMap;
