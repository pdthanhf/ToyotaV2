import React, { useState } from 'react';
import { Navbar } from '../components/common/Navbar';
import { ImageUpload } from '../components/detector/ImageUpload';
import { DetectionResult } from '../components/detector/DetectionResult';
// ❌ ĐÃ XÓA: import { AdminDashboard } ... để bảo mật
import { HistoryView } from '../components/history/HistoryView';
import { AnalyticsDashboard } from '../components/AnalyticsDashboard';
import { api } from '../api';
import { Camera } from 'lucide-react';
import { Navigate } from 'react-router-dom'; // ✅ Thêm cái này để chuyển trang

const HomePage = () => {
  // Quản lý Tab hiển thị
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
    <div className="min-h-screen bg-gray-100 font-sans text-gray-900 flex flex-col">
      {/* Navbar nhận props để điều khiển tab */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="container mx-auto px-4 py-8 flex-grow">
        
        {/* TAB: DETECT (MẶC ĐỊNH) */}
        {activeTab === 'detect' && (
          <div className="max-w-6xl mx-auto space-y-8 animate-fade-in-up">
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
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-pulse">
                    <p className="text-red-800 text-sm font-medium">{error}</p>
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
          <div className="max-w-5xl mx-auto animate-fade-in">
            <HistoryView />
          </div>
        )}

        {/* TAB: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div className="max-w-7xl mx-auto animate-fade-in">
             <AnalyticsDashboard />
          </div>
        )}

        {/* TAB: ADMIN - CHUYỂN HƯỚNG TỰ ĐỘNG */}
        {/* Nếu người dùng lỡ bấm vào tab Admin trên Navbar cũ, hệ thống sẽ tự chuyển sang trang /admin */}
        {activeTab === 'admin' && (
           <Navigate to="/admin" replace={true} />
        )}

      </main>

      <footer className="bg-gray-800 text-gray-400 py-6 text-center text-sm border-t border-gray-700 mt-auto">
        <p>© 2025 Toyota Computer Vision Project. Powered by YOLOv8 & FastAPI</p>
      </footer>
    </div>
  );
};

export default HomePage;