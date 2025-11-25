import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, BarChart2 } from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white overflow-hidden relative">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
                <div className="absolute top-[-10%] right-[-5%] w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
                <div className="absolute bottom-[-10%] left-[-5%] w-96 h-96 bg-secondary/20 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 container mx-auto px-6 py-12 flex flex-col items-center justify-center min-h-screen">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="text-center max-w-3xl"
                >
                    <div className="flex items-center justify-center mb-6">
                        <div className="p-4 bg-white/10 rounded-2xl backdrop-blur-lg border border-white/10 shadow-xl">
                            <Zap className="w-12 h-12 text-accent" />
                        </div>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        Texas Grid <br /> Interconnect Reporter
                    </h1>

                    <p className="text-xl text-gray-300 mb-10 leading-relaxed">
                        Visualize and analyze ERCOT Generator Interconnection Status Reports.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/quarter-report')}
                            className="px-8 py-4 bg-accent hover:bg-accent/90 text-white rounded-xl font-semibold text-lg shadow-lg shadow-accent/25 flex items-center justify-center gap-2 transition-all"
                        >
                            <BarChart2 className="w-5 h-5" />
                            Interactive Report
                        </motion.button>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default Dashboard;
