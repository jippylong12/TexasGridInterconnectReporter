import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Search, Sun, Wind, Battery, Zap, X, ChevronRight, FileText, BarChart2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie } from 'react-chartjs-2';
import axios from 'axios';
import TexasCountyMap from '../components/TexasCountyMap';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

interface QuarterData {
    summary: {
        total_mw: number;
        total_projects: number;
        top_counties: { county: string; mw: number }[];
    };
    fuel_chart: {
        labels: string[];
        data: number[];
        colors: string[];
    };
    county_data: {
        county: string;
        total_mw: number;
        project_count: number;
        fuel_breakdown: string;
    }[];
}

interface CountyMapData {
    county: string;
    total_mw: number;
    project_count: number;
    fuel_summary: string;
}

interface CountyDetails {
    county: string;
    quarters: string[];
    summary: {
        solar_mw: number;
        wind_mw: number;
        storage_mw: number;
        total_mw: number;
        project_count: number;
    };
    projects: any[];
}

const QuarterReport: React.FC = () => {
    const navigate = useNavigate();
    const [quarters, setQuarters] = useState<string[]>([]);
    const [selectedQuarters, setSelectedQuarters] = useState<string[]>([]);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [data, setData] = useState<QuarterData | null>(null);
    const [selectedCounty, setSelectedCounty] = useState<string | null>(null);
    const [countyDetails, setCountyDetails] = useState<CountyDetails | null>(null);
    const [loadingDetails, setLoadingDetails] = useState<boolean>(false);
    const [mapData, setMapData] = useState<CountyMapData[]>([]);
    const [reportPeriod, setReportPeriod] = useState<string>("");

    // Fetch available quarters on mount
    useEffect(() => {
        const fetchQuarters = async () => {
            try {
                const response = await axios.get('/api/quarters');
                setQuarters(response.data.quarters);
                if (response.data.report_period) {
                    setReportPeriod(response.data.report_period);
                }
                if (response.data.quarters.length > 0) {
                    // Default to latest quarter? Or let user choose.
                    // Let's not auto-select to force user interaction as requested "Quarter selection"
                }
            } catch (error) {
                console.error("Error fetching quarters:", error);
            }
        };
        fetchQuarters();
    }, []);

    // Fetch data when selected quarters change
    useEffect(() => {
        if (selectedQuarters.length === 0) {
            setData(null);
            setMapData([]);
            return;
        }

        const timer = setTimeout(() => {
            const fetchData = async () => {
                setLoading(true);
                try {
                    const params = new URLSearchParams();
                    selectedQuarters.forEach(q => params.append('quarters', q));

                    // Fetch both quarter data and map data
                    const [quarterResponse, mapResponse] = await Promise.all([
                        axios.get(`/api/quarter-data?${params.toString()}`),
                        axios.get(`/api/county-map-data?${params.toString()}`)
                    ]);

                    setData(quarterResponse.data);
                    setMapData(mapResponse.data.counties);
                } catch (error) {
                    console.error("Error fetching quarter data:", error);
                } finally {
                    setLoading(false);
                }
            };
            fetchData();
        }, 1000); // 1 second delay to prevent request spamming

        return () => clearTimeout(timer);
    }, [selectedQuarters]);

    // Fetch county details when county is selected
    useEffect(() => {
        if (!selectedCounty || selectedQuarters.length === 0) return;

        const fetchDetails = async () => {
            setLoadingDetails(true);
            try {
                const params = new URLSearchParams();
                params.append('county', selectedCounty);
                selectedQuarters.forEach(q => params.append('quarters', q));
                const response = await axios.get(`/api/county-details?${params.toString()}`);
                setCountyDetails(response.data);
            } catch (error) {
                console.error("Error fetching county details:", error);
            } finally {
                setLoadingDetails(false);
            }
        };
        fetchDetails();
    }, [selectedCounty, selectedQuarters]);

    const toggleQuarter = (quarter: string) => {
        setSelectedQuarters(prev =>
            prev.includes(quarter)
                ? prev.filter(q => q !== quarter)
                : [...prev, quarter]
        );
        // Clear drill-down if selection changes
        setSelectedCounty(null);
        setCountyDetails(null);
    };

    const removeQuarter = (quarter: string) => {
        setSelectedQuarters(prev => prev.filter(q => q !== quarter));
        setSelectedCounty(null);
        setCountyDetails(null);
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-6 md:p-12">
            {/* Header */}
            <div className="max-w-7xl mx-auto mb-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center text-gray-400 hover:text-white mb-2 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" /> Homepage
                    </button>
                    <h1 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
                        Quarterly Report
                    </h1>
                    {reportPeriod && (
                        <p className="text-gray-400 text-sm mt-1">
                            Report Period: <span className="text-gray-300 font-medium">{reportPeriod}</span>
                        </p>
                    )}
                </div>

                {/* Quarter Selector (Multi-select) */}
                <div className="relative w-full md:w-80">
                    <div
                        className="w-full min-h-[48px] pl-3 pr-10 py-2 bg-gray-800 border border-gray-700 rounded-xl focus-within:ring-2 focus-within:ring-primary focus-within:border-transparent cursor-pointer flex flex-wrap gap-2 items-center"
                        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    >
                        {selectedQuarters.length === 0 && (
                            <span className="text-gray-500 ml-1">Select Quarters...</span>
                        )}
                        {selectedQuarters.length > 0 && selectedQuarters.length === quarters.length ? (
                            <span className="text-white ml-1 font-medium">All Quarters Selected</span>
                        ) : selectedQuarters.length > 3 ? (
                            <span className="text-white ml-1 font-medium">{selectedQuarters.length} Quarters Selected</span>
                        ) : (
                            selectedQuarters.map(q => (
                                <span key={q} className="px-2 py-1 bg-primary/20 text-primary text-sm rounded-md flex items-center gap-1">
                                    {q}
                                    <X
                                        className="w-3 h-3 cursor-pointer hover:text-white"
                                        onClick={(e) => { e.stopPropagation(); removeQuarter(q); }}
                                    />
                                </span>
                            ))
                        )}
                        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                            <Search className="h-5 w-5 text-gray-400" />
                        </div>
                    </div>

                    {/* Dropdown Menu */}
                    {isDropdownOpen && (
                        <div className="absolute top-full left-0 w-full mt-2 bg-gray-800 border border-gray-700 rounded-xl shadow-xl max-h-80 overflow-y-auto z-50">
                            <div className="sticky top-0 bg-gray-800 p-2 border-b border-gray-700 flex gap-2 z-10">
                                <button
                                    onClick={(e) => { e.stopPropagation(); setSelectedQuarters([...quarters]); }}
                                    className="flex-1 px-2 py-1.5 text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 rounded-lg transition-colors"
                                >
                                    Select All
                                </button>
                                <button
                                    onClick={(e) => { e.stopPropagation(); setSelectedQuarters([]); }}
                                    className="flex-1 px-2 py-1.5 text-xs font-medium bg-gray-700 text-gray-300 hover:bg-gray-600 rounded-lg transition-colors"
                                >
                                    Deselect All
                                </button>
                            </div>
                            {quarters.map(q => (
                                <div
                                    key={q}
                                    className={`px-4 py-3 cursor-pointer hover:bg-gray-700 flex items-center gap-3 ${selectedQuarters.includes(q) ? 'bg-gray-700/50' : ''}`}
                                    onClick={() => toggleQuarter(q)}
                                >
                                    <div className={`w-4 h-4 rounded border flex items-center justify-center ${selectedQuarters.includes(q) ? 'bg-primary border-primary' : 'border-gray-500'}`}>
                                        {selectedQuarters.includes(q) && <div className="w-2 h-2 bg-white rounded-sm" />}
                                    </div>
                                    <span className="text-white">{q}</span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Backdrop to close dropdown */}
                    {isDropdownOpen && (
                        <div className="fixed inset-0 z-40" onClick={() => setIsDropdownOpen(false)} />
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto">
                {selectedQuarters.length === 0 ? (
                    <div className="text-center py-20 bg-gray-800/30 rounded-3xl border border-gray-700/50 border-dashed">
                        <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-400">Select one or more quarters to view the report</h3>
                    </div>
                ) : loading ? (
                    <div className="flex justify-center py-20">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    </div>
                ) : data ? (
                    <div className="space-y-8">
                        {/* Dashboard Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-lg"
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-gray-400 text-sm font-medium">Total Capacity</h3>
                                    <Zap className="w-5 h-5 text-yellow-400" />
                                </div>
                                <p className="text-3xl font-bold text-white">{data.summary.total_mw.toFixed(1)} <span className="text-lg text-gray-500 font-normal">MW</span></p>
                            </motion.div>

                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-lg"
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-gray-400 text-sm font-medium">Total Projects</h3>
                                    <FileText className="w-5 h-5 text-blue-400" />
                                </div>
                                <p className="text-3xl font-bold text-white">{data.summary.total_projects}</p>
                            </motion.div>

                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                                className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-lg"
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-gray-400 text-sm font-medium">Top County</h3>
                                    <BarChart2 className="w-5 h-5 text-green-400" />
                                </div>
                                <p className="text-xl font-bold text-white truncate">
                                    {data.summary.top_counties[0]?.county || 'N/A'}
                                </p>
                                <p className="text-sm text-gray-500 mt-1">
                                    {data.summary.top_counties[0]?.mw.toFixed(1) || 0} MW
                                </p>
                            </motion.div>
                        </div>


                        {/* Interactive Texas County Map */}
                        {mapData.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.25 }}
                                className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-lg"
                            >
                                <h3 className="text-lg font-semibold mb-6">Geographic Distribution</h3>
                                <TexasCountyMap
                                    data={mapData}
                                    onCountyClick={(county) => setSelectedCounty(county)}
                                />
                            </motion.div>
                        )}


                        {/* Charts Section */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Fuel Mix Chart */}
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.3 }}
                                className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-lg lg:col-span-1"
                            >
                                <h3 className="text-lg font-semibold mb-6">Fuel Type Distribution</h3>
                                <div className="h-64 flex items-center justify-center">
                                    <Pie
                                        data={{
                                            labels: data.fuel_chart.labels,
                                            datasets: [{
                                                data: data.fuel_chart.data,
                                                backgroundColor: data.fuel_chart.colors,
                                                borderWidth: 0
                                            }]
                                        }}
                                        options={{
                                            plugins: {
                                                legend: {
                                                    position: 'bottom',
                                                    labels: { color: '#9ca3af', usePointStyle: true }
                                                }
                                            }
                                        }}
                                    />
                                </div>
                            </motion.div>

                            {/* Main Table */}
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.4 }}
                                className="bg-gray-800 rounded-2xl border border-gray-700 shadow-lg lg:col-span-2 overflow-hidden flex flex-col"
                            >
                                <div className="p-6 border-b border-gray-700">
                                    <h3 className="text-lg font-semibold">County Breakdown</h3>
                                </div>
                                <div className="overflow-auto flex-1 max-h-[500px]">
                                    <table className="w-full text-left border-collapse">
                                        <thead className="bg-gray-900/50 sticky top-0 z-10 backdrop-blur-sm">
                                            <tr>
                                                <th className="p-4 text-sm font-medium text-gray-400">County</th>
                                                <th className="p-4 text-sm font-medium text-gray-400">Total MW</th>
                                                <th className="p-4 text-sm font-medium text-gray-400">Projects</th>
                                                <th className="p-4 text-sm font-medium text-gray-400">Fuel Mix</th>
                                                <th className="p-4 text-sm font-medium text-gray-400"></th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-700">
                                            {data.county_data.map((row) => (
                                                <tr
                                                    key={row.county}
                                                    onClick={() => setSelectedCounty(row.county)}
                                                    className="hover:bg-gray-700/50 cursor-pointer transition-colors group"
                                                >
                                                    <td className="p-4 font-medium text-white">{row.county}</td>
                                                    <td className="p-4 text-gray-300">{row.total_mw.toFixed(1)}</td>
                                                    <td className="p-4 text-gray-300">{row.project_count}</td>
                                                    <td className="p-4 text-gray-400 text-sm truncate max-w-xs">{row.fuel_breakdown}</td>
                                                    <td className="p-4 text-right">
                                                        <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-primary transition-colors" />
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </motion.div>
                        </div>
                    </div>
                ) : null}
            </div>

            {/* Drill-down Modal */}
            <AnimatePresence>
                {selectedCounty && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center px-4 py-12 md:p-4 bg-black/80 backdrop-blur-sm"
                        onClick={() => setSelectedCounty(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-gray-900 w-full max-w-5xl max-h-[90vh] rounded-3xl border border-gray-700 shadow-2xl overflow-hidden flex flex-col"
                            onClick={e => e.stopPropagation()}
                        >
                            {/* Modal Header */}
                            <div className="p-6 border-b border-gray-800 flex justify-between items-center bg-gray-800/50">
                                <div>
                                    <h2 className="text-2xl font-bold text-white flex flex-col md:flex-row md:items-center gap-3">
                                        <span>{selectedCounty} County</span>
                                        <div className="flex flex-wrap gap-2">
                                            {selectedQuarters.length > 0 && selectedQuarters.length === quarters.length ? (
                                                <span className="text-sm font-normal px-3 py-1 bg-primary/20 text-primary rounded-full border border-primary/20">
                                                    All Quarters Selected
                                                </span>
                                            ) : (
                                                selectedQuarters.map(q => (
                                                    <span key={q} className="text-sm font-normal px-3 py-1 bg-primary/20 text-primary rounded-full border border-primary/20">
                                                        {q}
                                                    </span>
                                                ))
                                            )}
                                        </div>
                                    </h2>
                                </div>
                                <button
                                    onClick={() => setSelectedCounty(null)}
                                    className="p-2 hover:bg-gray-700 rounded-full transition-colors"
                                >
                                    <X className="w-6 h-6 text-gray-400" />
                                </button>
                            </div>

                            {/* Modal Content */}
                            <div className="p-6 overflow-y-auto">
                                {loadingDetails ? (
                                    <div className="flex justify-center py-20">
                                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                                    </div>
                                ) : countyDetails ? (
                                    <div className="space-y-8">
                                        {/* Detail Cards */}
                                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                            <div className="bg-gray-800 p-5 rounded-xl border border-gray-700">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <div className="p-2 bg-yellow-500/10 rounded-lg">
                                                        <Sun className="w-5 h-5 text-yellow-500" />
                                                    </div>
                                                    <span className="text-gray-400 font-medium">Solar</span>
                                                </div>
                                                <p className="text-2xl font-bold">{countyDetails.summary.solar_mw.toFixed(1)} MW</p>
                                            </div>
                                            <div className="bg-gray-800 p-5 rounded-xl border border-gray-700">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <div className="p-2 bg-blue-400/10 rounded-lg">
                                                        <Wind className="w-5 h-5 text-blue-400" />
                                                    </div>
                                                    <span className="text-gray-400 font-medium">Wind</span>
                                                </div>
                                                <p className="text-2xl font-bold">{countyDetails.summary.wind_mw.toFixed(1)} MW</p>
                                            </div>
                                            <div className="bg-gray-800 p-5 rounded-xl border border-gray-700">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <div className="p-2 bg-green-500/10 rounded-lg">
                                                        <Battery className="w-5 h-5 text-green-500" />
                                                    </div>
                                                    <span className="text-gray-400 font-medium">Storage</span>
                                                </div>
                                                <p className="text-2xl font-bold">{countyDetails.summary.storage_mw.toFixed(1)} MW</p>
                                            </div>
                                        </div>

                                        {/* Detailed Table */}
                                        <div>
                                            <h3 className="text-lg font-semibold mb-4">Project Details</h3>
                                            <div className="overflow-x-auto rounded-xl border border-gray-700">
                                                <table className="w-full text-left border-collapse bg-gray-800/50">
                                                    <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wider">
                                                        <tr>
                                                            <th className="p-4">Project Name</th>
                                                            <th className="p-4">INR</th>
                                                            <th className="p-4">Fuel</th>
                                                            <th className="p-4">Capacity (MW)</th>
                                                            <th className="p-4">Entity</th>
                                                            <th className="p-4">POI</th>
                                                            <th className="p-4">COD</th>
                                                            <th className="p-4">Status</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody className="divide-y divide-gray-700 text-sm">
                                                        {countyDetails.projects.map((proj, idx) => (
                                                            <tr key={idx} className="hover:bg-gray-700/30">
                                                                <td className="p-4 font-medium text-white">{proj['Project Name']}</td>
                                                                <td className="p-4 text-gray-400">{proj['INR']}</td>
                                                                <td className="p-4">
                                                                    <span className="px-2 py-1 rounded-md bg-gray-700 text-xs font-medium">
                                                                        {proj['Fuel_Normalized']}
                                                                    </span>
                                                                </td>
                                                                <td className="p-4 text-white">{proj['Capacity (MW)']}</td>
                                                                <td className="p-4 text-gray-400 max-w-xs truncate" title={proj['Interconnecting Entity']}>
                                                                    {proj['Interconnecting Entity']}
                                                                </td>
                                                                <td className="p-4 text-gray-400 max-w-xs truncate" title={proj['POI Location']}>
                                                                    {proj['POI Location']}
                                                                </td>
                                                                <td className="p-4 text-gray-400 whitespace-nowrap">
                                                                    {proj['Projected COD'] ? new Date(proj['Projected COD']).toLocaleDateString() : 'N/A'}
                                                                </td>
                                                                <td className="p-4 text-gray-400 max-w-xs truncate" title={proj['GIM Study Phase']}>
                                                                    {proj['GIM Study Phase']}
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center py-10 text-gray-500">No details available</div>
                                )}
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default QuarterReport;
