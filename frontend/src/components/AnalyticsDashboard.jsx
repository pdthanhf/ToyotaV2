import React, { useState, useEffect } from 'react';
import { 
  BarChart2, TrendingUp, Car, Eye, RefreshCw, Download, Calendar 
} from 'lucide-react';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Area, AreaChart
} from 'recharts';
import { api } from '../api';

export const AnalyticsDashboard = () => {
  const [stats, setStats] = useState({
    total_cars: 0,
    total_versions: 0,
    total_detections: 0,
    avg_confidence: 0,
    popular_cars: [],
    detections_timeline: [],
    detection_by_hour: [],
    price_range_distribution: [] 
  });
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7days');

  useEffect(() => {
    loadAllStats();
  }, [timeRange]);

  const loadAllStats = async () => {
    setLoading(true);
    try {
      const [carsData, dashboardStats] = await Promise.all([
        api.getCars(),
        api.getDashboardStats()
      ]);

      const totalVersions = carsData.reduce((sum, car) => 
        sum + (car.versions?.length || 0), 0
      );

      setStats({
        total_cars: carsData.length,
        total_versions: totalVersions,
        total_detections: dashboardStats.total_detections || 0,
        avg_confidence: dashboardStats.avg_confidence || 0,
        popular_cars: dashboardStats.popular_cars || [],
        detections_timeline: dashboardStats.detections_timeline || [],
        detection_by_hour: dashboardStats.detection_by_hour || [],
        price_range_distribution: dashboardStats.price_range_distribution || [],
      });

    } catch (error) {
      console.error('Error loading stats:', error);
    }
    setLoading(false);
  };

  const exportData = () => {
    const dataStr = JSON.stringify(stats, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in-up pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center">
            <BarChart2 className="mr-2 text-red-600" /> Dashboard Thống kê
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Tổng quan hoạt động hệ thống
          </p>
        </div>
        
        <div className="flex gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="7days">7 ngày</option>
            <option value="30days">30 ngày</option>
          </select>
          
          <button
            onClick={loadAllStats}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm flex items-center gap-2"
          >
            <RefreshCw size={16} /> Làm mới
          </button>
          
          <button
            onClick={exportData}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm flex items-center gap-2"
          >
            <Download size={16} /> Tải dữ liệu
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Tổng số dòng xe"
          value={stats.total_cars}
          icon={<Car className="text-blue-500" size={24} />}
          color="blue"
          trend="+5%"
        />
        <StatCard
          title="Tổng phiên bản"
          value={stats.total_versions}
          icon={<Car className="text-green-500" size={24} />}
          color="green"
          trend="+12%"
        />
        <StatCard
          title="Lượt nhận diện"
          value={stats.total_detections}
          subtitle="Toàn thời gian"
          icon={<Eye className="text-purple-500" size={24} />}
          color="purple"
          trend="+8%"
        />
        <StatCard
          title="Độ chính xác TB"
          value={`${(stats.avg_confidence * 100).toFixed(1)}%`}
          icon={<TrendingUp className="text-orange-500" size={24} />}
          color="orange"
          trend="+2.3%"
        />
      </div>

      {/* HÀNG 1: Timeline & Top Cars */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">
              Lượt nhận diện theo thời gian
            </h3>
            <Calendar size={20} className="text-gray-400" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={stats.detections_timeline}>
              <defs>
                <linearGradient id="colorDetections" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <Tooltip contentStyle={{ borderRadius: '8px' }} />
              {/* Thêm name="Lượt nhận diện" */}
              <Area type="monotone" dataKey="detections" name="Lượt nhận diện" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorDetections)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">
            Top 5 xe phổ biến
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.popular_cars} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <YAxis type="category" dataKey="car_name" width={100} tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <Tooltip contentStyle={{ borderRadius: '8px' }} />
              {/* Thêm name="Số lượng" */}
              <Bar dataKey="count" name="Số lượng" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* HÀNG 2: Hoạt động theo giờ & Phân bổ giá */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Biểu đồ Hoạt động theo giờ */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">
            Hoạt động theo giờ
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats.detection_by_hour}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="hour" tick={{ fontSize: 10 }} interval={2} stroke="#9ca3af" />
              <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <Tooltip contentStyle={{ borderRadius: '8px' }} />
              {/* Thêm name="Lượt nhận diện" */}
              <Line type="monotone" dataKey="count" name="Lượt nhận diện" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Biểu đồ Phân bổ giá */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">
            Phân bổ theo mức giá
          </h3>
          {stats.price_range_distribution && stats.price_range_distribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.price_range_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
                <Tooltip contentStyle={{ borderRadius: '8px' }} />
                {/* Thêm name="Số lượng xe" */}
                <Bar dataKey="value" name="Số lượng xe" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-400">
              Chưa có dữ liệu giá
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

// Sub-component
const StatCard = ({ title, value, subtitle, icon, color, trend }) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    purple: 'bg-purple-50 border-purple-200',
    orange: 'bg-orange-50 border-orange-200',
  };
  return (
    <div className={`${colorClasses[color]} border rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600">{title}</span>
        {icon}
      </div>
      <div className="flex items-baseline justify-between">
        <div className="text-2xl font-bold text-gray-800">{value}</div>
        {trend && (
          <span className="text-xs font-semibold text-green-600 flex items-center">
            <TrendingUp size={12} className="mr-1" />
            {trend}
          </span>
        )}
      </div>
      {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
    </div>
  );
};