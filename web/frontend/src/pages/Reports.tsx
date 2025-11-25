import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Download, RefreshCw, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

interface GenerateResponse {
    status: string;
    message: string;
    images: string[];
    source_file: string;
}

const Reports: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<GenerateResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const generateReports = async () => {
        setLoading(true);
        setError(null);
        try {
            // In a real app, we might upload a file here.
            // For now, we trigger generation on the default file.
            const response = await axios.post('http://localhost:8000/api/generate');
            setData(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to generate reports. Ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    // Auto-generate on mount? Or wait for user?
    // Let's wait for user or auto-start if they came from dashboard with intent.
    // For now, let's just show a "Start Generation" state or auto-start.
    // Let's auto-start for better UX.
    useEffect(() => {
        generateReports();
    }, []);

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
                    <div className="w-24"></div> {/* Spacer for centering */}
                </div>
            </nav>

            <main className="container mx-auto px-6 py-10">
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700"
                    >
                        <AlertCircle className="w-5 h-5" />
                        {error}
                        <button onClick={generateReports} className="ml-auto text-sm font-semibold underline">Retry</button>
                    </motion.div>
                )}

                {loading && (
                    <div className="flex flex-col items-center justify-center h-96">
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                        >
                            <RefreshCw className="w-12 h-12 text-primary" />
                        </motion.div>
                        <p className="mt-4 text-gray-500 font-medium animate-pulse">Processing data and generating visualizations...</p>
                    </div>
                )}

                {!loading && data && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <div className="flex flex-col md:flex-row items-center justify-between mb-8 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                            <div>
                                <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                                    <CheckCircle className="w-5 h-5 text-green-500" />
                                    Generation Complete
                                </h2>
                                <p className="text-gray-500 text-sm mt-1">Source: {data.source_file}</p>
                            </div>
                            <button
                                onClick={downloadAll}
                                className="mt-4 md:mt-0 px-6 py-3 bg-primary hover:bg-primary/90 text-white rounded-lg font-semibold shadow-md flex items-center gap-2 transition-all"
                            >
                                <Download className="w-5 h-5" />
                                Download All Reports
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            {data.images.map((imgUrl, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
                                >
                                    <div className="p-4 border-b border-gray-50 flex justify-between items-center">
                                        <h3 className="font-semibold text-gray-700">
                                            {imgUrl.split('/').pop()?.replace('.png', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                        </h3>
                                        <a href={`http://localhost:8000${imgUrl}`} target="_blank" rel="noopener noreferrer" className="text-primary text-sm hover:underline">
                                            View Full
                                        </a>
                                    </div>
                                    <div className="aspect-video bg-gray-50 flex items-center justify-center overflow-hidden">
                                        <img
                                            src={`http://localhost:8000${imgUrl}`}
                                            alt="Report Chart"
                                            className="w-full h-full object-contain hover:scale-105 transition-transform duration-500"
                                        />
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </main>
        </div>
    );
};

export default Reports;
