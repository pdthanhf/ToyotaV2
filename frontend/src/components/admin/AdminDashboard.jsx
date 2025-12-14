      import React, { useState, useEffect } from 'react';
      import { 
        Database, Plus, Edit2, Trash2, Save, X, Search, 
        ChevronDown, ChevronUp, MessageSquare, Check, XCircle 
      } from 'lucide-react';
      import { api } from '../../api';

      // --- HÀM TIỆN ÍCH ---
      const formatCurrency = (amount) => {
        if (!amount) return "Liên hệ";
        // Xóa tất cả ký tự không phải số (trừ dấu chấm/phẩy)
        const cleaned = String(amount).replace(/[^\d]/g, ''); 
        if (!cleaned) return "Liên hệ";
        
      // Định dạng lại theo chuẩn Việt Nam
        return new Intl.NumberFormat('vi-VN', { 
      style: 'currency', 
      currency: 'VND', 
      minimumFractionDigits: 0 
      }).format(Number(cleaned));
      };

      export const AdminDashboard = () => {
        // --- STATE CHUNG ---
        const [activeSection, setActiveSection] = useState('cars'); // 'cars' | 'feedback'

        // --- STATE QUẢN LÝ XE  ---
        const [cars, setCars] = useState([]);
        const [filteredCars, setFilteredCars] = useState([]);
        const [loading, setLoading] = useState(true);
        const [showModal, setShowModal] = useState(false);
        const [editingCar, setEditingCar] = useState(null);
        const [searchTerm, setSearchTerm] = useState('');
        const [expandedRows, setExpandedRows] = useState(new Set());
        const [activeTab, setActiveTab] = useState(0);

        // --- STATE QUẢN LÝ FEEDBACK  ---
        const [feedbacks, setFeedbacks] = useState([]);
        const [feedbackLoading, setFeedbackLoading] = useState(false);
      

        // --- FORM INITIAL STATES ---
        const initialVersionState = {
          name: "", price: "",
          specs: {
            seats: "", type: "", origin: "", 
            dimensions: "", wheelbase: "", ground_clearance: "", wheels: "",
            engine: "", fuel: "", fuel_tank: "", fuel_consumption: "",
            max_power: "", max_torque: "", gearbox: "", drivetrain: "",
            suspension: "", brakes: "", steering: ""
          }
        };

        const initialFormState = {
          name: "", description: "", yolo_labels: "", 
          versions: [{ ...initialVersionState }]
        };

        const [formData, setFormData] = useState(initialFormState);
        const [errors, setErrors] = useState({});

        // --- EFFECTS ---
        useEffect(() => { 
          if (activeSection === 'cars') loadCars();
          if (activeSection === 'feedback') loadFeedbacks();
        }, [activeSection]);

        useEffect(() => {
          if (searchTerm) {
            const lower = searchTerm.toLowerCase();
            const filtered = cars.filter(c => c.name.toLowerCase().includes(lower));
            setFilteredCars(filtered);
          } else {
            setFilteredCars(cars);
          }
        }, [searchTerm, cars]);

        // --- API CALLS ---
        const loadCars = async () => {
          setLoading(true);
          try {
            // Thêm header Authorization khi gọi API
            const token = localStorage.getItem('adminToken');
            const data = await api.getCars(token); 
            setCars(data);
            setFilteredCars(data);
          } catch (error) {
            console.error("Lỗi tải xe:", error);
          }
          setLoading(false);
        };

        const loadFeedbacks = async () => {
          setFeedbackLoading(true);
          try {
            const token = localStorage.getItem('adminToken');
            // Chỉ lấy những cái pending để duyệt
            const data = await api.getCorrections('pending', token);
            setFeedbacks(data);
          } catch (error) {
            console.error("Lỗi tải phản hồi:", error);
          }
          setFeedbackLoading(false);
        };

        // --- LOGIC XỬ LÝ FEEDBACK ---
        const handleApproveFeedback = async (id) => {
          if (!window.confirm("Xác nhận duyệt dữ liệu này? Nó sẽ được dùng để train model.")) return;
          try {
            const token = localStorage.getItem('adminToken');
            await api.approveCorrection(id, token);
            setFeedbacks(feedbacks.filter(f => f.id !== id)); // Loại bỏ khỏi danh sách pending
            alert("Đã duyệt thành công!");
          } catch (error) {
            alert("Lỗi khi duyệt: " + error.message);
          }
        };

        const handleRejectFeedback = async (id) => {
          if (!window.confirm("Từ chối phản hồi này?")) return;
          try {
            const token = localStorage.getItem('adminToken');
            await api.rejectCorrection(id, token);
            setFeedbacks(feedbacks.filter(f => f.id !== id));
            alert("Đã từ chối!");
          } catch (error) {
            alert("Lỗi khi từ chối: " + error.message);
          }
        };

        // --- LOGIC XỬ LÝ FORM XE ---
      // *LƯU Ý: Đây là hàm chính để thay đổi dữ liệu trong form modal*
        const handleInputChange = (field, value) => {
          setFormData({ ...formData, [field]: value });
        };

        const handleVersionChange = (field, value, isSpec = false) => {
          const newVersions = [...formData.versions];
          if (isSpec) {
            // Kiểm tra và khởi tạo specs nếu chưa có
            if (!newVersions[activeTab].specs) newVersions[activeTab].specs = {};
            newVersions[activeTab].specs[field] = value;
          } else {
            newVersions[activeTab][field] = value;
          }
          setFormData({ ...formData, versions: newVersions });
        };

        const addVersion = () => {
          // Clone version mặc định hoặc version hiện tại (tạo bản sao sâu)
          const newVer = JSON.parse(JSON.stringify(initialVersionState));
      // Đảm bảo không trùng tên ngay lập tức
          newVer.name = `Phiên bản mới (${formData.versions.length + 1})`; 

          setFormData({ ...formData, versions: [...formData.versions, newVer] });
          setActiveTab(formData.versions.length); 
        };

        const removeVersion = (index, e) => {
          e.stopPropagation();
          if (formData.versions.length === 1) {
            alert("Phải có ít nhất 1 phiên bản!");
            return;
          }
          const newVersions = formData.versions.filter((_, i) => i !== index);
          setFormData({ ...formData, versions: newVersions });
          setActiveTab(0);
        };

        const openModal = (car = null) => {
          setErrors({});
          setActiveTab(0);
          if (car) {
            setEditingCar(car);
            setFormData({
              name: car.name || "",
              description: car.description || "",
              // Xử lý yolo_labels từ Array sang string để hiển thị
              yolo_labels: Array.isArray(car.yolo_labels) ? car.yolo_labels.join(", ") : (car.yolo_labels || ""),
              // Đảm bảo versions là một array hợp lệ
              versions: (car.versions && car.versions.length > 0) 
                ? car.versions 
                : [{ ...initialVersionState, name: "Tiêu chuẩn", price: car.price }]
            });
          } else {
            setEditingCar(null);
            setFormData(initialFormState);
          }
          setShowModal(true);
        };

        const handleSubmit = async (e) => {
          e.preventDefault();
          if (!formData.name.trim()) return setErrors({ name: "Tên xe là bắt buộc" });

          const payload = {
            ...formData,
            // Chuyển yolo_labels từ string sang Array
            yolo_labels: formData.yolo_labels.split(",").map(s => s.trim()).filter(Boolean)
          };

          try {
            const token = localStorage.getItem('adminToken');
            if (editingCar) {
              const id = editingCar.id || editingCar._id;
              const updated = await api.updateCar(id, payload, token);
              setCars(cars.map(c => (c.id === id || c._id === id) ? updated : c));
            } else {
              const newCar = await api.addCar(payload, token);
              setCars([newCar, ...cars]);
            }
            setShowModal(false);
            alert("Lưu thành công!");
            loadCars(); // Tải lại danh sách xe để đảm bảo dữ liệu mới nhất
          } catch (error) {
            alert("Lỗi khi lưu: " + error.message);
          }
        };

        const handleDelete = async (id) => {
          if (window.confirm("Xóa dòng xe này?")) {
            try {
            const token = localStorage.getItem('adminToken');
                await api.deleteCar(id, token);
                setCars(cars.filter(c => (c.id !== id && c._id !== id)));
                alert("Xóa thành công!");
            } catch (error) {
                alert("Lỗi khi xóa: " + error.message);
            }
          }
        };

        const toggleRow = (carId) => {
          const newExpanded = new Set(expandedRows);
          if (newExpanded.has(carId)) newExpanded.delete(carId);
          else newExpanded.add(carId);
          setExpandedRows(newExpanded);
        };

        // --- Component con render Input ---
      // Đã thêm thuộc tính 'name' và 'onChangeHandler' để linh hoạt sử dụng trong form
        const renderInput = (label, value, onChangeHandler, placeholder, name, required = false) => (
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              {label} {required && <span className="text-red-500">*</span>}
            </label>
            <input 
              type="text" 
            name={name}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none"
              value={value || ""}
              onChange={(e) => onChangeHandler(e.target.value)} // Sử dụng onChangeHandler truyền vào
              placeholder={placeholder}
            />
          </div>
        );

        return (
          <div className="bg-gray-50 min-h-screen p-6">
            
            {/* --- HEADER CHUYỂN TAB --- */}
            <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
              <div>
                 <h2 className="text-2xl font-bold text-gray-800 flex items-center">
                   <Database className="mr-2" /> Admin Dashboard
                 </h2>
                 <p className="text-sm text-gray-500">Quản lý dữ liệu xe và phản hồi từ người dùng</p>
              </div>
              
              <div className="bg-white p-1 rounded-lg shadow-sm border flex">
                <button 
                  onClick={() => setActiveSection('cars')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    activeSection === 'cars' ? 'bg-red-600 text-white shadow' : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  Quản lý Xe
                </button>
                <button 
                  onClick={() => setActiveSection('feedback')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center ${
                    activeSection === 'feedback' ? 'bg-red-600 text-white shadow' : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  Duyệt Phản Hồi
                  {feedbacks.length > 0 && (
                    <span className="ml-2 bg-yellow-400 text-yellow-900 text-xs px-1.5 rounded-full font-bold">
                      {feedbacks.length}
                    </span>
                  )}
                </button>
              </div>
            </div>

            {/* ========================================================= */}
            {/* SECTION 1: QUẢN LÝ XE */}
            {/* ========================================================= */}
            {activeSection === 'cars' && (
              <div className="bg-white rounded-xl shadow-lg p-6 animate-fade-in-up">
                <div className="flex justify-between items-center mb-6">
                  <div className="text-sm text-gray-500">Tổng số: <b>{cars.length}</b> dòng xe</div>
                  <div className="flex gap-3">
                    <div className="relative">
                      <input 
                        type="text" placeholder="Tìm kiếm..." 
                        value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
                        className="pl-10 pr-4 py-2 border rounded-lg focus:border-red-500 outline-none"
                      />
                      <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
                    </div>
                    <button onClick={() => openModal()} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                      <Plus size={18} className="mr-2" /> Thêm xe
                    </button>
                  </div>
                </div>

                {loading ? (
                  <div className="text-center py-10">Đang tải danh sách xe...</div>
            ) : (
                  <div className="overflow-x-auto border rounded-lg">
                  <table className="min-w-full text-left">
                    <thead className="bg-gray-100 text-gray-600 text-xs font-bold uppercase">
                      <tr>
                        <th className="p-4 w-10"></th>
                        <th className="p-4">Tên dòng xe</th>
                        <th className="p-4">Số phiên bản</th>
                        <th className="p-4">Giá bán (từ)</th>
                        <th className="p-4 text-center">Hành động</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {filteredCars.map(car => {
                        const carId = car.id || car._id;
                        const isExpanded = expandedRows.has(carId);
                        const versions = car.versions || [];
                        // Tìm giá thấp nhất để hiển thị
                        const minPriceVer = versions.length > 0 ? versions.reduce((min, ver) => {
                              const currentPrice = Number(String(ver.price).replace(/[^\d]/g, '')) || Infinity;
                              const minP = Number(String(min.price).replace(/[^\d]/g, '')) || Infinity;
                              return currentPrice < minP ? ver : min;
                        }, versions[0]) : null;
                        const displayPrice = minPriceVer ? formatCurrency(minPriceVer.price) : "Liên hệ";
                        return (
                          <React.Fragment key={carId}>
                            <tr className="hover:bg-gray-50">
                              <td className="p-4 text-center">
                                {versions.length > 0 && (
                                  <button onClick={() => toggleRow(carId)} className="text-gray-500 hover:text-gray-700">
                                    {isExpanded ? <ChevronUp size={16}/> : <ChevronDown size={16}/>}
                                  </button>
                                )}
                              </td>
                              <td className="p-4 font-medium text-gray-900">{car.name}</td>
                              <td className="p-4"><span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">{versions.length} phiên bản</span></td>
                              <td className="p-4 text-red-600 font-bold text-sm">{displayPrice}</td>
                              <td className="p-4 text-center flex justify-center gap-2">
                                <button onClick={() => openModal(car)} className="p-2 bg-yellow-100 text-yellow-600 rounded hover:bg-yellow-200"><Edit2 size={16}/></button>
                                <button onClick={() => handleDelete(carId)} className="p-2 bg-red-100 text-red-600 rounded hover:bg-red-200"><Trash2 size={16}/></button>
                              </td>
                            </tr>
                            {isExpanded && versions.map((ver, idx) => (
                              <tr key={idx} className="bg-gray-50 text-sm border-l-4 border-blue-500">
                                <td></td>
                                <td className="p-2 pl-8 text-gray-700 font-medium">↳ {ver.name}</td>
                                <td className="p-2 text-gray-500">{ver.specs?.type}</td>
                                <td className="p-2 text-red-600 font-semibold">{formatCurrency(ver.price)}</td>
                                <td></td>
                              </tr>
                            ))}
                          </React.Fragment>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
            )}
              </div>
            )}

            {/* ========================================================= */}
            {/* SECTION 2: QUẢN LÝ FEEDBACK */}
            {/* ========================================================= */}
            {activeSection === 'feedback' && (
              <div className="bg-white rounded-xl shadow-lg p-6 animate-fade-in-up">
                 <div className="mb-6">
                   <h3 className="text-lg font-bold text-gray-800 flex items-center">
                     <MessageSquare className="mr-2 text-blue-500"/> Danh sách chờ duyệt
                   </h3>
                   <p className="text-sm text-gray-500">Các ảnh người dùng báo cáo sai cần được kiểm tra để cập nhật dữ liệu huấn luyện.</p>
                 </div>
                 
                 {feedbackLoading ? (
                   <div className="text-center py-10">Đang tải dữ liệu...</div>
                 ) : feedbacks.length === 0 ? (
                   <div className="text-center py-10 text-gray-500 bg-gray-50 rounded-lg border border-dashed">
                     <Check className="mx-auto mb-2 text-green-500" size={32}/>
                     <p>Không có phản hồi nào cần xử lý!</p>
                   </div>
                 ) : (
                   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                     {feedbacks.map((fb) => (
                       <div key={fb.id} className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition bg-white flex flex-col">
                          {/* Header: Ảnh */}
                          <div className="relative h-48 bg-gray-100">
                             <img src={fb.image_url} alt="Feedback" className="w-full h-full object-contain" />
                             <div className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
                               {new Date(fb.created_at).toLocaleDateString()}
                             </div>
                          </div>

                          {/* Body: Thông tin */}
                          <div className="p-4 flex-grow">
                             <div className="flex justify-between items-start mb-2">
                               <div>
                                 <div className="text-xs text-gray-500 uppercase font-semibold">Model đoán:</div>
                                 <div className="text-red-600 font-bold">{fb.predicted_label}</div>
                                 <div className="text-xs text-gray-400">Độ tin cậy: {(fb.confidence * 100).toFixed(1)}%</div>
                               </div>
                               <div className="text-right">
                                 <div className="text-xs text-gray-500 uppercase font-semibold">Thực tế là:</div>
                                 <div className="text-green-600 font-bold text-lg">{fb.actual_label}</div>
                               </div>
                             </div>
                             
                             <div className="mt-2 bg-yellow-50 text-yellow-800 text-xs p-2 rounded border border-yellow-100">
                               <strong>Người dùng báo:</strong> {fb.is_correct ? "Đúng" : "Sai"}
                             </div>
                          </div>

                          {/* Footer: Hành động */}
                          <div className="p-3 bg-gray-50 border-t flex gap-2">
                             <button 
                               onClick={() => handleRejectFeedback(fb.id)}
                               className="flex-1 flex items-center justify-center py-2 bg-white border border-gray-300 text-gray-600 rounded hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition"
                             >
                               <XCircle size={16} className="mr-1"/> Từ chối
                             </button>
                             <button 
                               onClick={() => handleApproveFeedback(fb.id)}
                               className="flex-1 flex items-center justify-center py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition shadow-sm"
                             >
                               <Check size={16} className="mr-1"/> Duyệt
                             </button>
                          </div>
                       </div>
                     ))}
                   </div>
                 )}
              </div>
            )}

            {/* MODAL FULL OPTION */}
            {showModal && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
                <div className="bg-white rounded-xl w-full max-w-5xl shadow-2xl flex flex-col max-h-[90vh]">
                  
                  <div className="flex justify-between items-center p-5 border-b">
                    <h3 className="text-xl font-bold flex items-center">
                      {editingCar ? <Edit2 className="mr-2"/> : <Plus className="mr-2"/>}
                      {editingCar ? `Sửa: ${formData.name}` : "Thêm dòng xe mới"}
                    </h3>
                    <button onClick={() => setShowModal(false)}><X className="text-gray-400 hover:text-red-500"/></button>
                  </div>

                  <div className="flex-grow overflow-y-auto p-6 custom-scrollbar">
                    <form id="carForm" onSubmit={handleSubmit} className="space-y-6">
                      
                      {/* 1. THÔNG TIN CHUNG */}
                      <div className="bg-gray-50 p-4 rounded-lg border">
                        <h4 className="font-bold text-gray-700 mb-3">Thông tin dòng xe</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {renderInput("Tên dòng xe", formData.name, v => handleInputChange("name", v), "VD: Toyota Innova", "name", true)}
                          {renderInput("Tên khác (YOLO Labels)", formData.yolo_labels, v => handleInputChange("yolo_labels", v), "VD: innova, toyota innova cross", "yolo_labels")}
                          <div className="md:col-span-2">
                              {/* Sửa lỗi: dùng renderInput cho description */}
                              {renderInput("Mô tả ngắn", formData.description, v => handleInputChange("description", v), "Mô tả về dòng xe này...", "description")}
                          </div>
                        </div>
                      </div>

                      {/* 2. QUẢN LÝ PHIÊN BẢN (TABS) */}
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-bold text-gray-700">Các phiên bản ({formData.versions.length})</h4>
                          <button type="button" onClick={addVersion} className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 flex items-center">
                            <Plus size={14} className="mr-1"/> Thêm phiên bản
                          </button>
                        </div>

                        {/* Tab Headers */}
                        <div className="flex overflow-x-auto gap-2 mb-4 pb-2">
                          {formData.versions.map((ver, idx) => (
                            <div 
                              key={idx}
                              onClick={() => setActiveTab(idx)}
                              className={`flex items-center px-4 py-2 rounded-lg cursor-pointer border whitespace-nowrap transition-colors ${
                                activeTab === idx ? 'bg-red-600 text-white border-red-600' : 'bg-white text-gray-600 hover:bg-gray-50'
                              }`}
                            >
                              <span className="mr-2 font-medium">{ver.name || `Phiên bản ${idx + 1}`}</span>
                              <button 
                                onClick={(e) => removeVersion(idx, e)}
                                className={`p-0.5 rounded-full ${activeTab === idx ? 'hover:bg-red-500' : 'hover:bg-gray-200'}`}
                              >
                                <X size={14} />
                              </button>
                            </div>
                          ))}
                        </div>

                        {/* Tab Content - FORM CHI TIẾT */}
                        <div className="bg-white border rounded-xl p-5 shadow-sm">
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            
                            {/* Hàng 1 */}
                            <div className="lg:col-span-4 border-b pb-2 mb-2 font-bold text-red-600 text-sm uppercase">1. Thông tin cơ bản</div>
                            {renderInput("Tên phiên bản", formData.versions[activeTab].name, v => handleVersionChange("name", v), "VD: Innova Cross V", "version_name", true)}
                            {renderInput("Giá bán", formData.versions[activeTab].price, v => handleVersionChange("price", v), "VD: 810.000.000 VNĐ", "version_price")}
                            {renderInput("Loại xe", formData.versions[activeTab].specs.type, v => handleVersionChange("type", v, true), "VD: MPV", "specs_type")}
                            {renderInput("Số chỗ", formData.versions[activeTab].specs.seats, v => handleVersionChange("seats", v, true), "VD: 8 chỗ", "specs_seats")}
                            {renderInput("Xuất xứ", formData.versions[activeTab].specs.origin, v => handleVersionChange("origin", v, true), "VD: Nhập khẩu", "specs_origin")}

                            {/* Hàng 2 */}
                            <div className="lg:col-span-4 border-b pb-2 mb-2 mt-4 font-bold text-red-600 text-sm uppercase">2. Kích thước & Khung gầm</div>
                            {renderInput("Kích thước DxRxC", formData.versions[activeTab].specs.dimensions, v => handleVersionChange("dimensions", v, true), "VD: 4755 x 1850 x 1790 mm", "specs_dimensions")}
                            {renderInput("Chiều dài cơ sở", formData.versions[activeTab].specs.wheelbase, v => handleVersionChange("wheelbase", v, true), "VD: 2850 mm", "specs_wheelbase")}
                            {renderInput("Khoảng sáng gầm", formData.versions[activeTab].specs.ground_clearance, v => handleVersionChange("ground_clearance", v, true), "VD: 218 mm", "specs_ground_clearance")}
                            {renderInput("Cỡ mâm", formData.versions[activeTab].specs.wheels, v => handleVersionChange("wheels", v, true), "VD: 18 inch", "specs_wheels")}
                            
                            {/* Hàng 3 */}
                            <div className="lg:col-span-4 border-b pb-2 mb-2 mt-4 font-bold text-red-600 text-sm uppercase">3. Động cơ & Vận hành</div>
                            {renderInput("Động cơ", formData.versions[activeTab].specs.engine, v => handleVersionChange("engine", v, true), "VD: 2.0L M20A-FKS", "specs_engine")}
                            {renderInput("Công suất", formData.versions[activeTab].specs.max_power, v => handleVersionChange("max_power", v, true), "VD: 172 mã lực", "specs_max_power")}
                            {renderInput("Mô-men xoắn", formData.versions[activeTab].specs.max_torque, v => handleVersionChange("max_torque", v, true), "VD: 205 Nm", "specs_max_torque")}
                            {renderInput("Hộp số", formData.versions[activeTab].specs.gearbox, v => handleVersionChange("gearbox", v, true), "VD: CVT", "specs_gearbox")}
                            {renderInput("Hệ dẫn động", formData.versions[activeTab].specs.drivetrain, v => handleVersionChange("drivetrain", v, true), "VD: Cầu trước", "specs_drivetrain")}
                            {renderInput("Nhiên liệu", formData.versions[activeTab].specs.fuel, v => handleVersionChange("fuel", v, true), "VD: Xăng", "specs_fuel")}
                            {renderInput("Bình nhiên liệu", formData.versions[activeTab].specs.fuel_tank, v => handleVersionChange("fuel_tank", v, true), "VD: 52 lít", "specs_fuel_tank")}
                            {renderInput("Tiêu thụ nhiên liệu", formData.versions[activeTab].specs.fuel_consumption, v => handleVersionChange("fuel_consumption", v, true), "VD: 7.2 L/100km", "specs_fuel_consumption")}

                            {/* Hàng 4 */}
                            <div className="lg:col-span-4 border-b pb-2 mb-2 mt-4 font-bold text-red-600 text-sm uppercase">4. Hệ thống treo & Phanh</div>
                            {renderInput("Hệ thống treo", formData.versions[activeTab].specs.suspension, v => handleVersionChange("suspension", v, true), "VD: MacPherson / Thanh xoắn", "specs_suspension")}
                            {renderInput("Phanh trước/sau", formData.versions[activeTab].specs.brakes, v => handleVersionChange("brakes", v, true), "VD: Đĩa tản nhiệt / Đĩa", "specs_brakes")}
                            {renderInput("Trợ lực lái", formData.versions[activeTab].specs.steering, v => handleVersionChange("steering", v, true), "VD: Điện (EPS)", "specs_steering")}
                          </div>
                        </div>
                      </div>

                    </form>
                  </div>

                  <div className="p-5 border-t bg-gray-50 flex justify-end gap-3 rounded-b-xl">
                    <button type="button" onClick={() => setShowModal(false)} className="px-5 py-2.5 bg-white border rounded-lg hover:bg-gray-100 font-medium">Hủy</button>
                    <button type="submit" form="carForm" className="px-5 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium flex items-center shadow-lg">
                      <Save size={18} className="mr-2"/> Lưu thay đổi
                    </button>
                  </div>

                </div>
              </div>
            )}
          </div>
        );
      };