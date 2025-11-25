import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, BarChart2, FileText, ArrowRight } from 'lucide-react';
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
                        Visualize and analyze ERCOT Generator Interconnection Status Reports with premium insights and automated reporting.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/reports')}
                            className="px-8 py-4 bg-primary hover:bg-primary/90 text-white rounded-xl font-semibold text-lg shadow-lg shadow-primary/25 flex items-center justify-center gap-2 transition-all"
                        >
                            <BarChart2 className="w-5 h-5" />
                            Generate Reports
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white rounded-xl font-semibold text-lg backdrop-blur-md border border-white/10 flex items-center justify-center gap-2 transition-all"
                        >
                            <FileText className="w-5 h-5" />
                            Documentation
                        </motion.button>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 1 }}
                    className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-5xl"
                >
                    {[
                        { title: 'County Analysis', desc: 'Breakdown of MW capacity by county location.' },
                        { title: 'COD Timeline', desc: 'Projected Commercial Operation Dates by quarter.' },
                        { title: 'Fuel & Tech Mix', desc: 'Detailed distribution of fuel and technology types.' },
                    ].map((item, i) => (
                        <div key={i} className="p-6 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors">
                            <h3 className="text-xl font-semibold mb-2 text-primary">{item.title}</h3>
                            <p className="text-gray-400">{item.desc}</p>
                        </div>
                    ))}
                </motion.div>
            </div>
        </div>
    );
};

export default Dashboard;
