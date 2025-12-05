import React, { useState, useEffect } from 'react';
import { History, Search, Trash2, ExternalLink, Eye } from 'lucide-react';
import { api } from '../../api';

export const HistoryView = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadHistory();
    loadStats();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    const result = await api.getHistory();
    setData(result);
    setLoading(false);
  };

  const loadStats = async () => {
    try {
      const result = await api.getHistoryStats();
      setStats(result);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Xóa lịch sử này? Ảnh trên Cloudinary cũng sẽ bị xóa.')) {
      try {
        await api.deleteHistory(id);
        setData(data.filter(item => item._id !== id));
      } catch (error) {
        alert('Lỗi khi xóa: ' + error.message);
      }
    }
  };

  if (loading) return <div className="text-center py-10">Đang tải lịch sử...</div>;

  return (
    <div className="bg-white rounded-xl shadow p-6">
      {/* Header với thống kê */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center">
            <History className="mr-2" /> Lịch sử nhận diện
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Tất cả ảnh được lưu trữ trên Cloudinary
          </p>
        </div>
        
        {stats && (
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.total_detections}</div>
              <div className="text-xs text-gray-600">Tổng số</div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.today}</div>
              <div className="text-xs text-gray-600">Hôm nay</div>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{stats.last_7_days}</div>
              <div className="text-xs text-gray-600">7 ngày</div>
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-100 uppercase font-medium text-gray-500">
            <tr>
              <th className="px-6 py-3">Ảnh</th>
              <th className="px-6 py-3">Thời gian</th>
              <th className="px-6 py-3">File</th>
              <th className="px-6 py-3">Số xe</th>
              <th className="px-6 py-3 text-center">Hành động</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((item) => (
              <tr key={item._id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <img 
                    src={item.thumbnail_url || item.original_image_url}
                    alt="Thumbnail"
                    className="w-20 h-20 object-cover rounded shadow-sm"
                    loading="lazy"
                  />
                </td>
                <td className="px-6 py-4">
                  {new Date(item.timestamp).toLocaleString('vi-VN')}
                </td>
                <td className="px-6 py-4 font-medium">{item.filename}</td>
                <td className="px-6 py-4">
                  <span className="bg-blue-100 text-blue-800 py-1 px-3 rounded-full text-xs font-bold">
                    {item.detections.length}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex justify-center space-x-2">
                    <a 
                      href={item.result_image_url || item.original_image_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 bg-blue-100 text-blue-600 rounded hover:bg-blue-200"
                      title="Xem ảnh"
                    >
                      <ExternalLink size={16} />
                    </a>
                    <button 
                      onClick={() => handleDelete(item._id)}
                      className="p-2 bg-red-100 text-red-600 rounded hover:bg-red-200"
                      title="Xóa"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.length === 0 && (
        <div className="text-center py-10 text-gray-500">
          Chưa có lịch sử nhận diện nào
        </div>
      )}
    </div>
  );
};