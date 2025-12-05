import React, { useState, useEffect } from 'react';
import { X, Plus, Copy, Save, Layers } from 'lucide-react';

export const CarModal = ({ isOpen, onClose, car, onSave }) => {
  // 1. STATE
  const [formData, setFormData] = useState({
    name: '',
    yolo_labels: '',
    description: ''
  });

  const [versions, setVersions] = useState([]);
  const [activeTab, setActiveTab] = useState(0); 

  // 2. INIT DATA
  useEffect(() => {
    if (isOpen) {
      if (car) {
        setFormData({
          name: car.name || '',
          yolo_labels: car.yolo_labels?.join(', ') || '',
          description: car.description || ''
        });
        setVersions(car.versions || []);
      } else {
        setFormData({ name: '', yolo_labels: '', description: '' });
        setVersions([createEmptyVersion('Phiên bản 1')]); 
      }
      setActiveTab(0);
    }
  }, [isOpen, car]);

  const createEmptyVersion = (name) => ({
    name: name,
    price: '',
    specs: {
      seats: '', type: '', origin: '',
      engine: '', transmission: '', power: '', torque: '',
      fuel: '', fuel_tank: '',
      dimensions: '', wheelbase: '', ground_clearance: '',
      suspension: '', brakes: '', wheels: '', drivetrain: ''
    }
  });

  // --- 3. ACTIONS ---

  const handleAddVersion = () => {
    const newVer = createEmptyVersion(`Phiên bản ${versions.length + 1}`);
    const updatedVersions = [...versions, newVer];
    setVersions(updatedVersions);
    setActiveTab(updatedVersions.length - 1);
  };

  const handleDeleteVersion = (e, index) => {
    e.stopPropagation(); 
    if (versions.length === 1) return alert("Phải giữ lại ít nhất 1 phiên bản!");
    
    if (window.confirm("Xóa phiên bản này?")) {
      const updatedVersions = versions.filter((_, i) => i !== index);
      setVersions(updatedVersions);
      if (activeTab >= updatedVersions.length) {
        setActiveTab(updatedVersions.length - 1);
      }
    }
  };

  const handleCopyVersion = () => {
    const currentVer = versions[activeTab];
    const newVer = JSON.parse(JSON.stringify(currentVer));
    newVer.name = `${currentVer.name} (Copy)`;
    
    const updatedVersions = [...versions, newVer];
    setVersions(updatedVersions);
    setActiveTab(updatedVersions.length - 1);
  };

  // --- 4. UPDATES ---

  // Hàm cập nhật tên phiên bản theo index (Dùng cho ô nhập trên Tab)
  const updateVersionName = (index, newName) => {
    const updatedVersions = versions.map((ver, i) => {
      if (i === index) return { ...ver, name: newName };
      return ver;
    });
    setVersions(updatedVersions);
  };

  // Hàm cập nhật thông số (Dùng cho form bên dưới)
  const updateCurrentVersion = (field, value) => {
    const updatedVersions = versions.map((ver, idx) => {
      if (idx === activeTab) return { ...ver, [field]: value };
      return ver;
    });
    setVersions(updatedVersions);
  };

  const updateCurrentSpecs = (field, value) => {
    const updatedVersions = [...versions];
    if (!updatedVersions[activeTab].specs) updatedVersions[activeTab].specs = {};
    updatedVersions[activeTab].specs[field] = value;
    setVersions(updatedVersions);
  };

  // --- 5. SAVE ---
  const handleSubmit = () => {
    if (!formData.name.trim()) return alert("Chưa nhập tên dòng xe!");
    
    const payload = {
      ...formData,
      yolo_labels: formData.yolo_labels.split(',').map(s => s.trim()).filter(Boolean),
      versions: versions
    };
    onSave(payload);
  };

  if (!isOpen) return null;
  const currentVer = versions[activeTab] || createEmptyVersion('');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[95vh] flex flex-col overflow-hidden">
        
        {/* HEADER */}
        <div className="flex justify-between items-center p-4 bg-gray-50 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            {car ? <><span className="text-blue-600">✎</span> Sửa xe</> : <><span className="text-green-600">✚</span> Thêm xe mới</>}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-red-100 hover:text-red-600 rounded-full transition">
            <X size={24} />
          </button>
        </div>

        {/* BODY */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-white">
          
          {/* THÔNG TIN CHUNG */}
          <div className="bg-blue-50 p-5 rounded-lg border border-blue-100">
            <h3 className="text-sm font-bold text-blue-800 uppercase mb-3 flex items-center">
              <Layers size={16} className="mr-2"/> Thông tin chung
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tên dòng xe <span className="text-red-500">*</span></label>
                <input 
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Ví dụ: Toyota Vios"
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">YOLO Labels</label>
                <input 
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Cách nhau dấu phẩy..."
                  value={formData.yolo_labels}
                  onChange={e => setFormData({...formData, yolo_labels: e.target.value})}
                />
              </div>
            </div>
          </div>

          {/* QUẢN LÝ PHIÊN BẢN */}
          <div>
            <div className="flex justify-between items-end mb-2">
              <h3 className="text-sm font-bold text-gray-700 uppercase">Danh sách phiên bản</h3>
              <button onClick={handleAddVersion} className="flex items-center gap-1 bg-green-600 text-white px-3 py-1.5 rounded-lg hover:bg-green-700 text-sm font-medium shadow-sm active:scale-95 transition">
                <Plus size={16} /> Thêm phiên bản
              </button>
            </div>

            {/* ✅ TAB HEADERS - CHỈNH SỬA TRỰC TIẾP TẠI ĐÂY */}
            <div className="flex overflow-x-auto gap-2 border-b-2 border-gray-100 pb-1">
              {versions.map((ver, idx) => (
                <div 
                  key={idx}
                  onClick={() => setActiveTab(idx)}
                  className={`relative group flex items-center gap-2 px-4 py-2 rounded-t-lg border-t border-l border-r cursor-pointer min-w-[150px] transition-all select-none ${
                    activeTab === idx 
                      ? 'bg-white border-gray-300 border-b-white z-10 shadow-sm' 
                      : 'bg-gray-100 border-transparent hover:bg-gray-200'
                  }`}
                >
                  {/* LOGIC MỚI: NẾU ĐANG CHỌN THÌ HIỆN INPUT, KHÔNG THÌ HIỆN TEXT */}
                  {activeTab === idx ? (
                    <input 
                      className="bg-transparent text-red-600 font-bold outline-none border-b border-dashed border-red-300 w-full min-w-[100px]"
                      value={ver.name}
                      onChange={(e) => updateVersionName(idx, e.target.value)}
                      onClick={(e) => e.stopPropagation()} // Chặn click để không bị conflict
                      placeholder="Nhập tên..."
                      autoFocus
                    />
                  ) : (
                    <span className="truncate max-w-[120px] text-gray-600 font-medium">{ver.name || 'Chưa đặt tên'}</span>
                  )}

                  {versions.length > 1 && (
                    <X size={14} className="hover:text-red-600 hover:bg-red-200 rounded p-0.5" onClick={(e) => handleDeleteVersion(e, idx)} />
                  )}
                </div>
              ))}
            </div>

            {/* TAB CONTENT */}
            <div className="bg-white border border-gray-200 rounded-b-lg rounded-tr-lg p-6 shadow-sm space-y-6">
              
              {/* Toolbar Giá */}
              <div className="flex flex-wrap gap-4 items-end bg-gray-50 p-4 rounded-lg border border-gray-100">
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Giá niêm yết</label>
                  <input 
                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500 outline-none text-red-600 font-bold text-lg"
                    placeholder="VD: 592.000.000 VNĐ"
                    value={currentVer.price}
                    onChange={e => updateCurrentVersion('price', e.target.value)}
                  />
                </div>
                <div className="pb-1">
                   <button onClick={handleCopyVersion} className="p-2 bg-white border border-gray-300 rounded hover:bg-gray-100 text-gray-600" title="Nhân bản">
                     <Copy size={20} />
                   </button>
                </div>
              </div>

              {/* Grid Thông số */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-8 gap-y-5">
                <SectionHeader title="1. Thông số cơ bản" />
                <SpecInput label="Số chỗ ngồi" field="seats" val={currentVer.specs?.seats} onChange={updateCurrentSpecs} />
                <SpecInput label="Kiểu xe" field="type" val={currentVer.specs?.type} onChange={updateCurrentSpecs} />
                <SpecInput label="Xuất xứ" field="origin" val={currentVer.specs?.origin} onChange={updateCurrentSpecs} />
                
                <SectionHeader title="2. Kích thước & Khung gầm" />
                <SpecInput label="Kích thước" field="dimensions" val={currentVer.specs?.dimensions} onChange={updateCurrentSpecs} />
                <SpecInput label="Chiều dài cơ sở" field="wheelbase" val={currentVer.specs?.wheelbase} onChange={updateCurrentSpecs} />
                <SpecInput label="Khoảng sáng gầm" field="ground_clearance" val={currentVer.specs?.ground_clearance} onChange={updateCurrentSpecs} />
                <SpecInput label="Cỡ mâm" field="wheels" val={currentVer.specs?.wheels} onChange={updateCurrentSpecs} />

                <SectionHeader title="3. Động cơ & Vận hành" />
                <SpecInput label="Động cơ" field="engine" val={currentVer.specs?.engine} onChange={updateCurrentSpecs} />
                <SpecInput label="Hộp số" field="transmission" val={currentVer.specs?.transmission} onChange={updateCurrentSpecs} />
                <SpecInput label="Công suất" field="power" val={currentVer.specs?.power} onChange={updateCurrentSpecs} />
                <SpecInput label="Mô-men xoắn" field="torque" val={currentVer.specs?.torque} onChange={updateCurrentSpecs} />
                <SpecInput label="Nhiên liệu" field="fuel" val={currentVer.specs?.fuel} onChange={updateCurrentSpecs} />
                <SpecInput label="Dung tích bình" field="fuel_tank" val={currentVer.specs?.fuel_tank} onChange={updateCurrentSpecs} />
                <SpecInput label="Hệ dẫn động" field="drivetrain" val={currentVer.specs?.drivetrain} onChange={updateCurrentSpecs} />
                <SpecInput label="Treo trước/sau" field="suspension" val={currentVer.specs?.suspension} onChange={updateCurrentSpecs} />
                <SpecInput label="Phanh trước/sau" field="brakes" val={currentVer.specs?.brakes} onChange={updateCurrentSpecs} />
              </div>
            </div>
          </div>
        </div>

        {/* FOOTER */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
          <button onClick={onClose} className="px-6 py-2.5 rounded-lg text-gray-600 bg-white border border-gray-300 hover:bg-gray-100 font-medium">Hủy bỏ</button>
          <button onClick={handleSubmit} className="px-8 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 font-bold flex items-center gap-2 shadow-lg active:scale-95 transition">
            <Save size={20} /> Lưu thay đổi
          </button>
        </div>

      </div>
    </div>
  );
};

const SectionHeader = ({ title }) => (
  <div className="col-span-full border-b border-gray-200 pb-1 mt-2">
    <h4 className="font-bold text-gray-800">{title}</h4>
  </div>
);

const SpecInput = ({ label, field, val, onChange }) => (
  <div className="flex items-center gap-3">
    <label className="w-1/3 text-sm text-gray-600 font-medium text-right">{label}:</label>
    <input 
      className="flex-1 p-2 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none transition text-sm"
      value={val || ''}
      onChange={(e) => onChange(field, e.target.value)}
      placeholder="---"
    />
  </div>
);