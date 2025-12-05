import React, { useState } from 'react';
import { Navbar } from './components/common/Navbar';
import { ImageUpload } from './components/detector/ImageUpload';
import { DetectionResult } from './components/detector/DetectionResult';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { HistoryView } from './components/history/HistoryView';
// 1. IMPORT COMPONENT DASHBOARD
import { AnalyticsDashboard } from './components/AnalyticsDashboard'; 
import { api } from './api';
import { Camera } from 'lucide-react';
import './App.css';

const App = () => {
  // Thêm 'dashboard' vào danh sách các tab có thể active
  const [activeTab, setActiveTab] = useState('detect');
  const [processing, setProcessing] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState(null);

  const handleImageUpload = async (file, objectUrl) => {
    setProcessing(true);
    setUploadedFile(file);
    setPreviewUrl(objectUrl);
    setDetectionResult(null);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('image', file);
      
      const result = await api.detect(formData);
      
      if (result.success) {
        setDetectionResult(result);
      } else {
        setError('Không thể nhận diện xe trong ảnh này');
      }
    } catch (err) {
      console.error("Detection error:", err);
      setError(err.message || 'Lỗi khi nhận diện. Vui lòng thử lại.');
    } finally {
      setProcessing(false);
    }
  };

  const handleReset = () => {
    setDetectionResult(null);
    setUploadedFile(null);
    setPreviewUrl(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-900">
      {/* Navbar nhận props để điều khiển tab */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="container mx-auto px-4 py-8">
        {/* TAB: DETECT */}
        {activeTab === 'detect' && (
          <div className="max-w-6xl mx-auto space-y-8">
            <div className="text-center space-y-2 mb-8">
              <h1 className="text-3xl font-extrabold text-gray-900">
                Hệ thống Nhận diện & Tra cứu Xe Toyota
              </h1>
              <p className="text-gray-500">
                Tự động phân tích hình ảnh và cung cấp thông số kỹ thuật chi tiết
              </p>
            </div>

            {!detectionResult && (
              <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-sm">
                <ImageUpload 
                  onImageSelected={handleImageUpload} 
                  isProcessing={processing} 
                />
                {error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800 text-sm">{error}</p>
                  </div>
                )}
              </div>
            )}

            {detectionResult && (
              <div className="animate-fade-in-up">
                <DetectionResult 
                  result={detectionResult} 
                  filename={uploadedFile?.name} 
                  originalPreview={previewUrl} 
                  onReset={handleReset} 
                />
                <div className="mt-8 flex justify-center pb-8">
                  <button 
                    onClick={handleReset} 
                    className="flex items-center space-x-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-full shadow-lg font-medium transition-transform hover:scale-105"
                  >
                    <Camera size={20} />
                    <span>Nhận diện ảnh khác</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB: HISTORY */}
        {activeTab === 'history' && (
          <div className="max-w-5xl mx-auto">
            <HistoryView />
          </div>
        )}

        {/* --- 2. THÊM TAB MỚI: DASHBOARD --- */}
        {activeTab === 'dashboard' && (
          <div className="max-w-7xl mx-auto">
             <AnalyticsDashboard />
          </div>
        )}

        {/* TAB: ADMIN */}
        {activeTab === 'admin' && (
          <div className="max-w-6xl mx-auto">
            <AdminDashboard />
          </div>
        )}
      </main>

      <footer className="bg-gray-800 text-gray-400 py-6 text-center text-sm border-t border-gray-700">
        <p>© 2025 Toyota Computer Vision Project. Powered by YOLOv8 & FastAPI</p>
      </footer>
    </div>
  );
};

export default App;