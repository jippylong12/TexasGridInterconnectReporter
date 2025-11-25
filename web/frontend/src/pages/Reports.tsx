import React, { useState } from 'react';
import axios from 'axios';
import { Download, RefreshCw, ArrowLeft, ChevronDown, ChevronUp, FileBarChart, Zap, Calendar, Map } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

interface ReportConfig {
    id: string;
    title: string;
    description: string;
    icon: React.ReactNode;
}

const REPORTS: ReportConfig[] = [
    {
        id: 'county',
        title: 'County MW Breakdown',
        description: 'Horizontal bar chart showing total MW capacity by county.',
        icon: <Map className="w-5 h-5 text-blue-500" />
    },
    {
        id: 'cod',
        title: 'COD Quarterly Buckets',
        description: 'Vertical bar chart showing project count by projected COD quarter.',
        icon: <Calendar className="w-5 h-5 text-purple-500" />
    },
    {
        id: 'fuel',
        title: 'Fuel Type Breakdown',
        description: 'Pie chart and table showing distribution by fuel type.',
        icon: <Zap className="w-5 h-5 text-yellow-500" />
    },
    {
        id: 'technology',
        title: 'Technology Type Breakdown',
        description: 'Pie chart and table showing distribution by technology type.',
        icon: <FileBarChart className="w-5 h-5 text-green-500" />
    }
];

const Reports: React.FC = () => {
    // State to track expanded accordion items
    const [expanded, setExpanded] = useState<string | null>(null);

    // State to track data for each report: { [reportId]: imageUrl }
    const [reportImages, setReportImages] = useState<Record<string, string>>({});

    // State to track loading status for each report: { [reportId]: boolean }
    const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});

    // State to track errors
    const [errors, setErrors] = useState<Record<string, string>>({});

    const toggleAccordion = (id: string) => {
        setExpanded(expanded === id ? null : id);
    };

    const generateReport = async (reportId: string) => {
        setLoadingStates(prev => ({ ...prev, [reportId]: true }));
        setErrors(prev => ({ ...prev, [reportId]: '' }));

        try {
            const response = await axios.post('http://localhost:8000/api/generate', {
                report_type: reportId
            });

            if (response.data.images && response.data.images.length > 0) {
                setReportImages(prev => ({
                    ...prev,
                    [reportId]: response.data.images[0]
                }));
            }
        } catch (err: any) {
            setErrors(prev => ({
                ...prev,
                [reportId]: err.response?.data?.detail || 'Failed to generate report.'
            }));
        } finally {
            setLoadingStates(prev => ({ ...prev, [reportId]: false }));
        }
    };

    const downloadAll = () => {
        window.location.href = 'http://localhost:8000/api/download';
    };

    return (
        <div className="min-h-screen bg-gray-50 text-dark">
            <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
                <div className="container mx-auto px-6 py-4 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2 text-gray-600 hover:text-primary transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                        <span className="font-medium">Back to Dashboard</span>
                    </Link>
                    <h1 className="text-xl font-bold text-gray-800">Generated Reports</h1>
                    <button
                        onClick={downloadAll}
                        className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold shadow-sm flex items-center gap-2 transition-all text-sm"
                    >
                        <Download className="w-4 h-4" />
                        Download All
                    </button>
                </div>
            </nav>

            <main className="container mx-auto px-6 py-10 max-w-4xl">
                <div className="space-y-4">
                    {REPORTS.map((report) => (
                        <div
                            key={report.id}
                            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition-all duration-200 hover:shadow-md"
                        >
                            <button
                                onClick={() => toggleAccordion(report.id)}
                                className="w-full px-6 py-4 flex items-center justify-between bg-white hover:bg-gray-50 transition-colors text-left"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-2 bg-gray-100 rounded-lg">
                                        {report.icon}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-800 text-lg">{report.title}</h3>
                                        <p className="text-gray-500 text-sm">{report.description}</p>
                                    </div>
                                </div>
                                {expanded === report.id ? (
                                    <ChevronUp className="w-5 h-5 text-gray-400" />
                                ) : (
                                    <ChevronDown className="w-5 h-5 text-gray-400" />
                                )}
                            </button>

                            <AnimatePresence>
                                {expanded === report.id && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        transition={{ duration: 0.2 }}
                                        className="border-t border-gray-100"
                                    >
                                        <div className="p-6 bg-gray-50/50">
                                            {/* Action Bar */}
                                            <div className="flex items-center justify-between mb-6">
                                                <div className="text-sm text-gray-500">
                                                    {reportImages[report.id] ? (
                                                        <span className="text-green-600 font-medium flex items-center gap-1">
                                                            Report Generated
                                                        </span>
                                                    ) : (
                                                        <span>Ready to generate</span>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={() => generateReport(report.id)}
                                                    disabled={loadingStates[report.id]}
                                                    className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-all ${loadingStates[report.id]
                                                            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                                                            : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 shadow-sm'
                                                        }`}
                                                >
                                                    {loadingStates[report.id] ? (
                                                        <>
                                                            <RefreshCw className="w-4 h-4 animate-spin" />
                                                            Generating...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <RefreshCw className="w-4 h-4" />
                                                            {reportImages[report.id] ? 'Regenerate' : 'Generate Report'}
                                                        </>
                                                    )}
                                                </button>
                                            </div>

                                            {/* Error Message */}
                                            {errors[report.id] && (
                                                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                                                    {errors[report.id]}
                                                </div>
                                            )}

                                            {/* Content Area */}
                                            <div className="min-h-[200px] flex items-center justify-center bg-white rounded-xl border border-gray-200 shadow-inner">
                                                {loadingStates[report.id] ? (
                                                    <div className="flex flex-col items-center gap-3 py-10">
                                                        <motion.div
                                                            animate={{ rotate: 360 }}
                                                            transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                                                        >
                                                            <RefreshCw className="w-8 h-8 text-primary/50" />
                                                        </motion.div>
                                                        <p className="text-gray-400 text-sm animate-pulse">Generating visualization...</p>
                                                    </div>
                                                ) : reportImages[report.id] ? (
                                                    <div className="w-full p-2">
                                                        <div className="relative group">
                                                            <img
                                                                src={`http://localhost:8000${reportImages[report.id]}`}
                                                                alt={report.title}
                                                                className="w-full h-auto rounded-lg"
                                                            />
                                                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100">
                                                                <a
                                                                    href={`http://localhost:8000${reportImages[report.id]}`}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="px-4 py-2 bg-white text-gray-800 rounded-full shadow-lg font-medium transform translate-y-2 group-hover:translate-y-0 transition-all"
                                                                >
                                                                    View Full Size
                                                                </a>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <div className="text-center py-10 text-gray-400">
                                                        <FileBarChart className="w-12 h-12 mx-auto mb-2 opacity-20" />
                                                        <p>Click "Generate Report" to view this visualization</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
};

export default Reports;
