import React, { useState, useEffect } from 'react';
import { ArrowRight, AlertCircle, Plus, RefreshCw, Calendar, ChevronDown, ChevronRight, GitCompare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ColumnChange {
    column: string;
    old_value: string;
    new_value: string;
}

interface FullComparisonItem {
    INR: string;
    "Project Name": string;
    County: string;
    change_count: number;
    changes: ColumnChange[];
}

interface ComparisonData {
    base_period: string;
    target_period: string;
    added_projects: any[];
    flagged_changes: any[];
    full_comparison: FullComparisonItem[];
}

// Fuel colors matching QuarterReport
const FUEL_COLORS: Record<string, string> = {
    'Solar': '#FDB813',
    'Wind': '#4169E1',
    'Battery': '#32CD32',
    'Gas': '#A9A9A9',
    'Other': '#808080'
};

const ComparisonView: React.FC = () => {
    const [years, setYears] = useState<string[]>([]);
    const [months, setMonths] = useState<{ value: string; label: string }[]>([]);

    const [baseYear, setBaseYear] = useState<string>('');
    const [baseMonth, setBaseMonth] = useState<string>('');
    const [targetYear, setTargetYear] = useState<string>('');
    const [targetMonth, setTargetMonth] = useState<string>('');

    const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<'added' | 'flagged' | 'all'>('added');
    const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

    useEffect(() => {
        fetchYears();
    }, []);

    useEffect(() => {
        if (baseYear) fetchMonths(baseYear);
    }, [baseYear]);

    useEffect(() => {
        if (targetYear) fetchMonths(targetYear);
    }, [targetYear]);

    const fetchYears = async () => {
        try {
            const response = await fetch('/api/years');
            const data = await response.json();
            setYears(data.years);
            if (data.years.length > 0) {
                setBaseYear(data.years[0]);
                setTargetYear(data.years[0]);
            }
        } catch (err) {
            console.error('Error fetching years:', err);
        }
    };

    const fetchMonths = async (year: string) => {
        try {
            const response = await fetch(`/api/months?year=${year}`);
            const data = await response.json();
            setMonths(data.months);
        } catch (err) {
            console.error('Error fetching months:', err);
        }
    };

    const handleCompare = async () => {
        if (!baseYear || !baseMonth || !targetYear || !targetMonth) {
            setError('Please select both base and target periods.');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(
                `/api/comparison-data?base_year=${baseYear}&base_month=${baseMonth}&target_year=${targetYear}&target_month=${targetMonth}`
            );

            if (!response.ok) {
                throw new Error('Failed to fetch comparison data');
            }

            const data = await response.json();
            setComparisonData(data);
        } catch (err) {
            setError('Error generating comparison report. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6 md:p-12">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <RefreshCw className="w-8 h-8 text-blue-600" />
                        Project Comparison Report
                    </h1>
                    <p className="text-gray-600 mt-2">Compare two different report periods to identify added projects and updates.</p>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
                    <div className="grid grid-cols-1 md:grid-cols-11 gap-6 items-end">
                        {/* Base Period */}
                        <div className="md:col-span-4 space-y-4">
                            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                                <Calendar className="w-4 h-4" /> Base Period (Older)
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                                    <select
                                        value={baseYear}
                                        onChange={(e) => setBaseYear(e.target.value)}
                                        className="w-full rounded-lg border-gray-300 border p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                                    >
                                        {years.map((y) => (
                                            <option key={y} value={y}>{y}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
                                    <select
                                        value={baseMonth}
                                        onChange={(e) => setBaseMonth(e.target.value)}
                                        className="w-full rounded-lg border-gray-300 border p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                                    >
                                        <option value="">Select Month</option>
                                        {months.map((m) => (
                                            <option key={m.value} value={m.value}>{m.label}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* VS Divider */}
                        <div className="md:col-span-1 flex justify-center pb-3">
                            <div className="bg-gray-100 rounded-full p-2">
                                <ArrowRight className="w-6 h-6 text-gray-400" />
                            </div>
                        </div>

                        {/* Target Period */}
                        <div className="md:col-span-4 space-y-4">
                            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                                <Calendar className="w-4 h-4" /> Target Period (Newer)
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                                    <select
                                        value={targetYear}
                                        onChange={(e) => setTargetYear(e.target.value)}
                                        className="w-full rounded-lg border-gray-300 border p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                                    >
                                        {years.map((y) => (
                                            <option key={y} value={y}>{y}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
                                    <select
                                        value={targetMonth}
                                        onChange={(e) => setTargetMonth(e.target.value)}
                                        className="w-full rounded-lg border-gray-300 border p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                                    >
                                        <option value="">Select Month</option>
                                        {months.map((m) => (
                                            <option key={m.value} value={m.value}>{m.label}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Action Button */}
                        <div className="md:col-span-2 pb-1">
                            <button
                                onClick={handleCompare}
                                disabled={loading}
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-lg shadow-md transition-colors flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {loading ? (
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <>Compare</>
                                )}
                            </button>
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-r-lg flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {comparisonData && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="space-y-6"
                    >
                        {/* Tab Navigation */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="flex border-b border-gray-200">
                                <button
                                    onClick={() => setActiveTab('added')}
                                    className={`flex-1 py-4 px-6 text-sm font-semibold transition-colors flex items-center justify-center gap-2 ${activeTab === 'added'
                                        ? 'bg-green-50 text-green-700 border-b-2 border-green-600'
                                        : 'text-gray-500 hover:bg-gray-50'
                                        }`}
                                >
                                    <Plus className="w-4 h-4" />
                                    Added Projects
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${activeTab === 'added' ? 'bg-green-200 text-green-800' : 'bg-gray-200 text-gray-600'
                                        }`}>
                                        {comparisonData.added_projects.length}
                                    </span>
                                </button>
                                <button
                                    onClick={() => setActiveTab('flagged')}
                                    className={`flex-1 py-4 px-6 text-sm font-semibold transition-colors flex items-center justify-center gap-2 ${activeTab === 'flagged'
                                        ? 'bg-amber-50 text-amber-700 border-b-2 border-amber-600'
                                        : 'text-gray-500 hover:bg-gray-50'
                                        }`}
                                >
                                    <RefreshCw className="w-4 h-4" />
                                    Flagged Changes
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${activeTab === 'flagged' ? 'bg-amber-200 text-amber-800' : 'bg-gray-200 text-gray-600'
                                        }`}>
                                        {comparisonData.flagged_changes.length}
                                    </span>
                                </button>
                                <button
                                    onClick={() => setActiveTab('all')}
                                    className={`flex-1 py-4 px-6 text-sm font-semibold transition-colors flex items-center justify-center gap-2 ${activeTab === 'all'
                                        ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-600'
                                        : 'text-gray-500 hover:bg-gray-50'
                                        }`}
                                >
                                    <GitCompare className="w-4 h-4" />
                                    All Changes
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${activeTab === 'all' ? 'bg-blue-200 text-blue-800' : 'bg-gray-200 text-gray-600'
                                        }`}>
                                        {comparisonData.full_comparison?.length || 0}
                                    </span>
                                </button>
                            </div>

                            {/* Tab Content */}
                            {activeTab === 'added' && (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left text-sm text-gray-600">
                                        <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500">
                                            <tr>
                                                <th className="px-6 py-3">INR</th>
                                                <th className="px-6 py-3">Project Name</th>
                                                <th className="px-6 py-3">County</th>
                                                <th className="px-6 py-3">MW</th>
                                                <th className="px-6 py-3">Fuel Type</th>
                                                <th className="px-6 py-3">COD</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100">
                                            {comparisonData.added_projects.length === 0 ? (
                                                <tr>
                                                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500 italic">
                                                        No new projects found in this period.
                                                    </td>
                                                </tr>
                                            ) : (
                                                comparisonData.added_projects.map((proj: any) => (
                                                    <tr key={proj.INR} className="hover:bg-gray-50 transition-colors">
                                                        <td className="px-6 py-3 font-medium text-gray-900">{proj.INR}</td>
                                                        <td className="px-6 py-3">{proj['Project Name']}</td>
                                                        <td className="px-6 py-3">{proj.County}</td>
                                                        <td className="px-6 py-3">{proj['Capacity (MW)']}</td>
                                                        <td className="px-6 py-3">
                                                            <span
                                                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                                                                style={{ backgroundColor: FUEL_COLORS[proj['Fuel Type']] || FUEL_COLORS['Other'] }}
                                                            >
                                                                {proj['Fuel Type']}
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-3">{proj['Projected COD']}</td>
                                                    </tr>
                                                ))
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {activeTab === 'flagged' && (
                                <div className="overflow-x-auto">
                                    <div className="p-4 bg-amber-50 border-b border-amber-100 text-sm text-amber-800">
                                        <strong>Note:</strong> These are changes flagged in the <strong>{comparisonData.target_period}</strong> report.
                                    </div>
                                    <table className="w-full text-left text-sm text-gray-600">
                                        <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500">
                                            <tr>
                                                <th className="px-6 py-3">INR</th>
                                                <th className="px-6 py-3">Project Name</th>
                                                <th className="px-6 py-3">County</th>
                                                <th className="px-6 py-3">Change Flag</th>
                                                <th className="px-6 py-3">New Value</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100">
                                            {comparisonData.flagged_changes.length === 0 ? (
                                                <tr>
                                                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500 italic">
                                                        No changes flagged in the target report.
                                                    </td>
                                                </tr>
                                            ) : (
                                                comparisonData.flagged_changes.map((item: any) => (
                                                    <tr key={item.INR} className="hover:bg-gray-50 transition-colors">
                                                        <td className="px-6 py-3 font-medium text-gray-900">{item.INR}</td>
                                                        <td className="px-6 py-3">{item['Project Name']}</td>
                                                        <td className="px-6 py-3">{item.County}</td>
                                                        <td className="px-6 py-3">
                                                            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
                                                                {item.change_flag}
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-3">
                                                            <div className="flex flex-wrap gap-1">
                                                                {item.new_values && item.new_values.length > 0 ? (
                                                                    item.new_values.map((val: string, idx: number) => (
                                                                        <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                                                            {val}
                                                                        </span>
                                                                    ))
                                                                ) : (
                                                                    <span className="text-gray-400 italic">—</span>
                                                                )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                ))
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            {activeTab === 'all' && (
                                <div className="overflow-x-auto">
                                    <div className="p-4 bg-blue-50 border-b border-blue-100 text-sm text-blue-800">
                                        <strong>Note:</strong> Full comparison of all columns between <strong>{comparisonData.base_period}</strong> and <strong>{comparisonData.target_period}</strong>.
                                    </div>
                                    {comparisonData.full_comparison?.length === 0 ? (
                                        <div className="px-6 py-8 text-center text-gray-500 italic">
                                            No field differences found between the two periods.
                                        </div>
                                    ) : (
                                        <div className="divide-y divide-gray-100">
                                            {comparisonData.full_comparison?.map((item: FullComparisonItem) => {
                                                const isExpanded = expandedRows.has(item.INR);
                                                const toggleExpand = () => {
                                                    const newSet = new Set(expandedRows);
                                                    if (isExpanded) {
                                                        newSet.delete(item.INR);
                                                    } else {
                                                        newSet.add(item.INR);
                                                    }
                                                    setExpandedRows(newSet);
                                                };

                                                return (
                                                    <div key={item.INR}>
                                                        <div
                                                            onClick={toggleExpand}
                                                            className="flex items-center px-6 py-4 cursor-pointer hover:bg-gray-50 transition-colors"
                                                        >
                                                            <div className="mr-3">
                                                                {isExpanded ? (
                                                                    <ChevronDown className="w-5 h-5 text-gray-400" />
                                                                ) : (
                                                                    <ChevronRight className="w-5 h-5 text-gray-400" />
                                                                )}
                                                            </div>
                                                            <div className="flex-1 grid grid-cols-4 gap-4 text-sm">
                                                                <div className="font-medium text-gray-900">{item.INR}</div>
                                                                <div className="text-gray-600">{item["Project Name"]}</div>
                                                                <div className="text-gray-600">{item.County}</div>
                                                                <div>
                                                                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                                        {item.change_count} change{item.change_count !== 1 ? 's' : ''}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <AnimatePresence>
                                                            {isExpanded && (
                                                                <motion.div
                                                                    initial={{ height: 0, opacity: 0 }}
                                                                    animate={{ height: 'auto', opacity: 1 }}
                                                                    exit={{ height: 0, opacity: 0 }}
                                                                    transition={{ duration: 0.2 }}
                                                                    className="overflow-hidden"
                                                                >
                                                                    <div className="px-6 pb-4 pl-14">
                                                                        <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
                                                                            <thead className="bg-gray-100">
                                                                                <tr>
                                                                                    <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Column</th>
                                                                                    <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">Old Value</th>
                                                                                    <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase">New Value</th>
                                                                                </tr>
                                                                            </thead>
                                                                            <tbody className="divide-y divide-gray-200">
                                                                                {item.changes.map((change, idx) => (
                                                                                    <tr key={idx} className="hover:bg-gray-50">
                                                                                        <td className="px-4 py-2 font-medium text-gray-700">{change.column}</td>
                                                                                        <td className="px-4 py-2 text-red-600">{change.old_value}</td>
                                                                                        <td className="px-4 py-2 text-green-600">{change.new_value}</td>
                                                                                    </tr>
                                                                                ))}
                                                                            </tbody>
                                                                        </table>
                                                                    </div>
                                                                </motion.div>
                                                            )}
                                                        </AnimatePresence>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default ComparisonView;
