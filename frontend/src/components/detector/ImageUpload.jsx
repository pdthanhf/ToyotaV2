import React, { useState, useRef } from 'react';
import { Upload, RefreshCw } from 'lucide-react';

export const ImageUpload = ({ onImageSelected, isProcessing }) => {
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const objectUrl = URL.createObjectURL(file);
      setPreview(objectUrl);
      onImageSelected(file, objectUrl);
    }
  };

  return (
    <div className="w-full">
      <div 
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer bg-white shadow-sm ${
          preview ? 'border-red-500 bg-red-50' : 'border-gray-300 hover:border-red-400 hover:bg-gray-50'
        }`}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept="image/*" 
          onChange={handleFileChange} 
        />
        
        {preview ? (
          <div className="relative">
            <img 
              src={preview} 
              alt="Preview" 
              className="max-h-64 mx-auto rounded-lg shadow-md object-contain" 
            />
            <div className="mt-4 text-sm text-gray-500 bg-white/80 inline-block px-3 py-1 rounded-full">
              Nhấn để chọn ảnh khác
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="bg-red-100 p-4 rounded-full mb-4">
              <Upload size={32} className="text-red-600" />
            </div>
            <p className="text-lg font-medium text-gray-700">Tải ảnh xe lên</p>
            <p className="text-sm text-gray-500 mt-2">
              Hệ thống sẽ tự động nhận diện và hiển thị thông số kỹ thuật
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Định dạng: JPG, JPEG, PNG, WEBP (Tối đa 10MB)
            </p>
          </div>
        )}
      </div>
      
      {isProcessing && (
        <div className="mt-6 flex items-center justify-center space-x-2 text-red-600 animate-pulse">
          <RefreshCw className="animate-spin" />
          <span className="font-medium">
            Đang phân tích và tra cứu dữ liệu...
          </span>
        </div>
      )}
    </div>
  );
};