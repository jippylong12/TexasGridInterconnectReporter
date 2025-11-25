import React, { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

const TestMap: React.FC = () => {
  const [projection, setProjection] = useState<string>("geoAlbers");
  const [scale, setScale] = useState<number>(1200);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-4 text-blue-400">Simple Map Render Test</h1>

      <div className="mb-4 flex gap-4">
        <button
          onClick={() => setProjection(p => p === "geoAlbers" ? "geoMercator" : "geoAlbers")}
          className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500"
        >
          Toggle Projection: {projection}
        </button>
        <button
          onClick={() => setScale(s => s === 1200 ? 2000 : 1200)}
          className="px-4 py-2 bg-green-600 rounded hover:bg-green-500"
        >
          Toggle Scale: {scale}
        </button>
      </div>

      <div className="w-full max-w-4xl h-[600px] bg-gray-800 rounded-xl border-2 border-white p-4">
        <ComposableMap
          projection={projection as any}
          projectionConfig={{
            scale: scale,
            center: [-99, 31.5] // Center of Texas
          }}
          style={{ width: "100%", height: "100%" }}
          // Force a large standard viewBox as requested
          viewBox="0 0 1000 800"
        >
          <Geographies geography="/data/counties-10m.json">
            {({ geographies }) => {
              // Filter for Texas (ID starts with 48)
              const texasGeos = geographies.filter((geo: any) => geo.id && geo.id.toString().startsWith('48'));

              return texasGeos.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill="#10b981"
                  stroke="#000000"
                  strokeWidth={0.5}
                />
              ));
            }}
          </Geographies>
        </ComposableMap>
      </div>

      <div className="mt-4 text-gray-400 text-sm">
        <p>Rendering with explicit viewBox="0 0 1000 800"</p>
        <p>Data Source: /data/counties-10m.json</p>
      </div>
    </div>
  );
};

export default TestMap;
