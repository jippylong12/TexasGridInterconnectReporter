import React, { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
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

// Texas counties GeoJSON URL (using public data)
const TEXAS_TOPO_JSON = "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json";

const TexasCountyMap: React.FC<TexasCountyMapProps> = ({ data, onCountyClick }) => {
    const [hoveredCounty, setHoveredCounty] = useState<CountyData | null>(null);
    const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

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
        <div className="relative w-full">
            <ComposableMap
                projection="geoAlbers"
                projectionConfig={{
                    scale: 2500,
                    center: [-99, 31.5],
                }}
                className="w-full h-auto bg-gray-900/30 rounded-2xl"
                style={{ maxHeight: '500px' }}
            >
                <Geographies geography={TEXAS_TOPO_JSON}>
                    {({ geographies }) =>
                        geographies
                            .filter((geo) => geo.id.startsWith('48')) // Texas FIPS code starts with 48
                            .map((geo) => (
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
                                    onMouseEnter={(event) => handleCountyMouseEnter(geo, event)}
                                    onMouseMove={handleCountyMouseMove}
                                    onMouseLeave={handleCountyMouseLeave}
                                    onClick={() => handleCountyClick(geo)}
                                />
                            ))
                    }
                </Geographies>
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
            <div className="mt-4 flex items-center justify-center gap-4">
                <span className="text-sm text-gray-400">Low MW</span>
                <div className="flex h-4 w-48 rounded-full overflow-hidden border border-gray-700">
                    <div className="flex-1" style={{ background: 'linear-gradient(to right, #10b981, #fbbf24, #ef4444)' }} />
                </div>
                <span className="text-sm text-gray-400">High MW</span>
            </div>
        </div>
    );
};

export default TexasCountyMap;
