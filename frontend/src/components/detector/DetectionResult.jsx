import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, AlertCircle, Maximize2, X, ExternalLink,
  ThumbsUp, ThumbsDown, Send, MessageSquarePlus 
} from 'lucide-react';
import { api } from '../../api';

export const DetectionResult = ({ result, filename, onReset }) => {
  const [carsDB, setCarsDB] = useState([]);
  const [selectedCarInfo, setSelectedCarInfo] = useState(null); 
  const [selectedVersion, setSelectedVersion] = useState(null); 
  const [showFullImage, setShowFullImage] = useState(false);

  // --- STATE CHO FEEDBACK ---
  const [feedbackStatus, setFeedbackStatus] = useState('idle'); // 'idle', 'submitting', 'sent'
  const [showCorrectionInput, setShowCorrectionInput] = useState(false);
  const [correctionValue, setCorrectionValue] = useState('');

  const bestDetection = result.detections?.[0];
  const resultImage = result.result_image_url || result.original_image_url;

  useEffect(() => {
    const fetchCars = async () => {
      try {
        const data = await api.getCars();
        setCarsDB(data);
        if (bestDetection) {
          handleAutoSelect(bestDetection.class_name, data);
        }
      } catch (error) {
        console.error("Lỗi tải database xe:", error);
      }
    };
    fetchCars();
  }, [result]);

  // --- LOGIC TÌM XE & PHIÊN BẢN (GIỮ NGUYÊN) ---
  const findCarInfo = (detectedName, database) => {
    if (!detectedName || !database || database.length === 0) return null;
    
    const normalizedDetected = detectedName.toLowerCase().replace(/_/g, ' ').trim();

    // 1. Tìm trong yolo_labels
    let found = database.find(car => {
      if (!car.yolo_labels || !Array.isArray(car.yolo_labels)) return false;
      return car.yolo_labels.some(label => label.toLowerCase() === detectedName.toLowerCase());
    });
    if (found) return found;

    // 2. Tìm chính xác tên
    found = database.find(c => c.name.toLowerCase() === normalizedDetected);
    if (found) return found;

    // 3. Tìm từ khóa
    const keywords = normalizedDetected.split(' ').filter(k => !['toyota', 'suv', 'sedan', 'mpv', 'hatchback', 'pickup'].includes(k));
    if (keywords.length > 0) {
      found = database.find(c => {
        const dbName = c.name.toLowerCase();
        return keywords.every(k => dbName.includes(k));
      });
      if (found) return found;
    }

    // 4. Tìm tương đối
    found = database.find(c => c.name.toLowerCase().includes(normalizedDetected) || normalizedDetected.includes(c.name.toLowerCase()));
    if (found) return found;

    return null;
  };

  const findMatchingVersion = (detectedName, carInfo) => {
    if (!carInfo || !carInfo.versions || carInfo.versions.length === 0) return null;
    const nameLower = detectedName.toLowerCase();

    const keywordMap = [
      { key: 'hybrid', target: ['hv', 'hybrid'] },          
      { key: 'cross', target: ['cross', 'top'] },           
      { key: 'xse', target: ['xse', 'sport'] },             
      { key: 'gr', target: ['gr', 'sport', 'rs'] },               
      { key: 'limousine', target: ['limousine', 'vip'] },
      { key: 'vios_e', target: ['e cvt', 'e mt'] },
      { key: 'vios_g', target: ['g cvt'] },        
    ];

    for (const map of keywordMap) {
      if (nameLower.includes(map.key)) {
        const match = carInfo.versions.find(v => map.target.some(t => v.name.toLowerCase().includes(t)));
        if (match) return match;
      }
    }

    const parts = nameLower.split(/[ _]/);
    if (parts.length > 1) {
      const suffix = parts[parts.length - 1]; 
      const matchSuffix = carInfo.versions.find(v => v.name.toLowerCase().includes(suffix));
      if (matchSuffix) return matchSuffix;
    }

    return carInfo.versions[0];
  };

  const handleAutoSelect = (className, db) => {
    const car = findCarInfo(className, db);
    setSelectedCarInfo(car);
    if (car) {
      const ver = findMatchingVersion(className, car);
      setSelectedVersion(ver);
    } else {
      setSelectedVersion(null);
    }
  };

  const handleCarClick = (className) => {
    handleAutoSelect(className, carsDB);
  };

  const getSpec = (field, altField = null) => {
    if (!selectedVersion || !selectedVersion.specs) return null;
    let val = selectedVersion.specs[field] || selectedVersion.specs[altField];
    if (!val && selectedCarInfo && selectedCarInfo.specs) {
        val = selectedCarInfo.specs[field] || selectedCarInfo.specs[altField];
    }
    return val;
  };

  // --- LOGIC GỬI FEEDBACK  ---
  const handleSubmitFeedback = async (isCorrect, actualLabel = null) => {
    if (!bestDetection) return;
    
    setFeedbackStatus('submitting');
    
    // Tạo payload gửi đi
    const payload = {
      image_url: resultImage, // Url ảnh từ cloudinary
      predicted_label: bestDetection.class_name,
      actual_label: isCorrect ? bestDetection.class_name : actualLabel,
      confidence: bestDetection.confidence,
      is_correct: isCorrect,
      timestamp: new Date().toISOString()
    };

    try {
      console.log(" Đang gửi feedback về server...", payload);
      
      //  GỌI API THẬT (KHÔNG ĐƯỢC COMMENT DÒNG NÀY)
      await api.sendFeedback(payload); 
      
      console.log(" Gửi thành công!");
      setFeedbackStatus('sent');
      setShowCorrectionInput(false);
    } catch (error) {
      console.error(" Lỗi gửi feedback:", error);
      alert("Có lỗi xảy ra khi gửi phản hồi: " + (error.message || "Vui lòng thử lại."));
      setFeedbackStatus('idle');
    }
  };

  if (!bestDetection) return null;

  return (
    <div className="flex flex-col lg:flex-row gap-8 animate-fade-in-up">
      
      {/* CỘT TRÁI: ẢNH & FEEDBACK */}
      <div className="lg:w-5/12 space-y-4">
        
        {/* KHỐI HIỂN THỊ ẢNH */}
        <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
           <div className="bg-gray-900 text-white px-4 py-2 flex justify-between items-center">
             <span className="text-sm font-bold flex items-center">
               <CheckCircle size={14} className="text-green-400 mr-2"/> Kết quả nhận diện
             </span>
             <button onClick={onReset} className="hover:text-red-400"><X size={16}/></button>
           </div>
           
           <div className="relative group bg-gray-100 flex items-center justify-center min-h-[300px]">
             <img 
               src={resultImage} 
               alt="Result" 
               className="max-w-full max-h-[400px] object-contain cursor-zoom-in"
               onClick={() => setShowFullImage(true)}
             />
             <button onClick={() => setShowFullImage(true)} className="absolute bottom-2 right-2 bg-black/60 text-white p-1 rounded opacity-0 group-hover:opacity-100 transition">
               <Maximize2 size={16} />
             </button>
           </div>

           <div className="p-3 bg-gray-50 border-t space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase">Các xe tìm thấy:</p>
              {result.detections.map((det, idx) => {
                const isActive = selectedCarInfo && findCarInfo(det.class_name, carsDB)?.name === selectedCarInfo.name;
                return (
                  <div 
                    key={idx} 
                    onClick={() => handleCarClick(det.class_name)}
                    className={`flex justify-between items-center p-2 rounded cursor-pointer border ${
                      isActive ? 'bg-red-50 border-red-400 ring-1 ring-red-400' : 'bg-white border-gray-200 hover:border-red-300'
                    }`}
                  >
                    <div>
                      <div className="font-bold text-sm text-gray-800">{det.class_name}</div>
                      <div className="text-xs text-gray-500">
                        {findCarInfo(det.class_name, carsDB)?.name || 'Chưa có dữ liệu'}
                      </div>
                    </div>
                    <span className="text-xs font-bold bg-gray-200 text-gray-700 px-2 py-1 rounded">
                      {(det.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                )
              })}
           </div>
        </div>

        {/* --- KHỐI FEEDBACK (SỬA LỖI NHẬN DIỆN) --- */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 shadow-sm transition-all duration-300">
          {feedbackStatus === 'sent' ? (
            <div className="text-center text-green-700 py-2 animate-fade-in">
              <CheckCircle className="mx-auto mb-2" size={32} />
              <p className="font-bold">Cảm ơn đóng góp của bạn!</p>
              <p className="text-xs opacity-80">Dữ liệu này sẽ giúp hệ thống AI thông minh hơn.</p>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-2 mb-3">
                <MessageSquarePlus size={20} className="text-blue-600"/>
                <h4 className="font-bold text-gray-800 text-sm">Kết quả này có đúng không?</h4>
              </div>

              {!showCorrectionInput ? (
                <div className="flex gap-3">
                  <button 
                    onClick={() => handleSubmitFeedback(true)}
                    disabled={feedbackStatus === 'submitting'}
                    className="flex-1 flex items-center justify-center gap-2 bg-white border border-green-500 text-green-700 hover:bg-green-50 py-2 rounded transition font-medium text-sm shadow-sm"
                  >
                    <ThumbsUp size={16} />
                    Đúng
                  </button>
                  <button 
                    onClick={() => setShowCorrectionInput(true)}
                    disabled={feedbackStatus === 'submitting'}
                    className="flex-1 flex items-center justify-center gap-2 bg-white border border-red-400 text-red-600 hover:bg-red-50 py-2 rounded transition font-medium text-sm shadow-sm"
                  >
                    <ThumbsDown size={16} />
                    Sai
                  </button>
                </div>
              ) : (
                <div className="space-y-3 animate-fade-in">
                  <p className="text-xs text-gray-600 font-medium">Vui lòng chọn dòng xe đúng:</p>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <select 
                        className="w-full p-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-400 outline-none bg-white appearance-none"
                        value={correctionValue}
                        onChange={(e) => setCorrectionValue(e.target.value)}
                      >
                        <option value="">-- Chọn tên xe --</option>
                        {carsDB.map((car, idx) => (
                          <option key={idx} value={car.name}>{car.name}</option>
                        ))}
                      </select>
                      {/* Mũi tên custom cho select */}
                      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                      </div>
                    </div>
                    
                    <button 
                      onClick={() => handleSubmitFeedback(false, correctionValue)}
                      disabled={!correctionValue || feedbackStatus === 'submitting'}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 rounded flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed shadow-sm transition-colors"
                    >
                      {feedbackStatus === 'submitting' ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      ) : (
                        <Send size={16}/>
                      )}
                    </button>
                  </div>
                  <button 
                    onClick={() => setShowCorrectionInput(false)}
                    className="text-xs text-gray-500 hover:text-gray-800 hover:underline w-full text-center transition-colors"
                  >
                    Quay lại
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* CỘT PHẢI: BẢNG THÔNG SỐ (GIỮ NGUYÊN) */}
      <div className="lg:w-7/12">
        {selectedCarInfo ? (
          <div className="bg-white shadow-lg rounded-lg overflow-hidden border border-gray-200">
            
            {/* HEADER ĐỎ */}
            <div className="bg-red-700 text-white p-5">
              <div className="flex flex-col">
                 <h2 className="text-xl font-bold uppercase tracking-wide">
                   THÔNG SỐ {selectedCarInfo.name}
                 </h2>
                 
                 {selectedCarInfo.description && (
                   <p className="text-sm text-white/90 mt-1 italic font-medium leading-relaxed">
                     "{selectedCarInfo.description}"
                   </p>
                 )}
                 
                 <div className="mt-3 flex flex-wrap gap-2">
                   <span className="text-red-200 text-sm py-1">Phiên bản:</span>
                   {selectedCarInfo.versions?.map((ver, idx) => (
                      <button
                        key={idx}
                        onClick={() => setSelectedVersion(ver)}
                        className={`px-3 py-0.5 rounded text-sm font-medium border transition-all ${
                          selectedVersion?.name === ver.name
                            ? 'bg-white text-red-700 border-white shadow-md' 
                            : 'bg-red-800/50 text-white border-red-500 hover:bg-red-600'
                        }`}
                      >
                        {ver.name}
                      </button>
                   ))}
                 </div>
              </div>
            </div>

            {/* BODY BẢNG TRẮNG */}
            <div className="p-6">
               {selectedVersion ? (
                 <div className="space-y-6">
                    <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                       <span className="text-gray-600 font-medium">Giá niêm yết</span>
                       <span className="text-2xl font-bold text-red-600">
                         {selectedVersion.price}
                       </span>
                    </div>

                    <table className="w-full text-sm mt-4">
                      <tbody className="divide-y divide-gray-100">
                        <TableRow label="Số chỗ ngồi" value={getSpec('seats')} />
                        <TableRow label="Kiểu xe" value={getSpec('type') || selectedCarInfo.type} />
                        <TableRow label="Xuất xứ" value={getSpec('origin')} />
                        <TableRow label="Kích thước DxRxC" value={getSpec('dimensions')} />
                        <TableRow label="Chiều dài cơ sở" value={getSpec('wheelbase')} />
                        <TableRow label="Khoảng sáng gầm" value={getSpec('ground_clearance')} />
                        <TableRow label="Cỡ mâm" value={getSpec('wheels') || getSpec('tire')} />
                        <TableRow label="Động cơ" value={getSpec('engine')} />
                        <TableRow label="Loại nhiên liệu" value={getSpec('fuel')} />
                        <TableRow label="Dung tích bình" value={getSpec('fuel_tank')} />
                        <TableRow label="Công suất" value={getSpec('power', 'max_power')} />
                        <TableRow label="Mô-men xoắn" value={getSpec('torque', 'max_torque')} />
                        <TableRow label="Hộp số" value={getSpec('transmission', 'gearbox')} />
                        <TableRow label="Hệ dẫn động" value={getSpec('drivetrain')} />
                        <TableRow label="Treo trước/sau" value={getSpec('suspension')} />
                        <TableRow label="Phanh trước/sau" value={getSpec('brakes')} />
                        <TableRow label="Trợ lực lái" value={getSpec('steering')} />
                      </tbody>
                    </table>

                    <div className="mt-4 pt-4 border-t text-center">
                       <p className="text-xs text-gray-400 italic">
                         * Thông số mang tính chất tham khảo.
                       </p>
                    </div>
                 </div>
               ) : (
                 <div className="text-center py-12 text-gray-500">
                   <AlertCircle size={40} className="mx-auto mb-2 text-gray-300"/>
                   <p>Không tìm thấy thông tin phiên bản phù hợp.</p>
                 </div>
               )}
            </div>
         </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-10 text-center border border-gray-200">
             <AlertCircle size={48} className="mx-auto mb-4 text-gray-300"/>
             <h3 className="text-lg font-bold text-gray-700">Chưa có dữ liệu</h3>
             <p className="text-gray-500">Dòng xe này chưa được cập nhật thông số.</p>
          </div>
        )}
      </div>

      {showFullImage && (
        <div className="fixed inset-0 z-[9999] bg-black/90 flex items-center justify-center p-4" onClick={() => setShowFullImage(false)}>
          <button className="absolute top-4 right-4 text-white p-2 hover:text-red-500"><X size={32}/></button>
          <img src={resultImage} alt="Full" className="max-w-full max-h-[95vh] object-contain rounded"/>
        </div>
      )}
    </div>
  );
};

const TableRow = ({ label, value }) => (
  <tr>
    <td className="py-3 text-gray-600 font-medium w-1/3">{label}</td>
    <td className="py-3 text-gray-900 font-semibold">{value || <span className="text-gray-400 italic">Đang cập nhật...</span>}</td>
  </tr>
);