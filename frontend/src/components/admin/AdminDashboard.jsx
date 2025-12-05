import React, { useState, useEffect } from 'react';
import { Database, Plus, Edit2, Trash2, Save, X, Search, Copy, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../../api';

export const AdminDashboard = () => {
  const [cars, setCars] = useState([]);
  const [filteredCars, setFilteredCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCar, setEditingCar] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedRows, setExpandedRows] = useState(new Set());
  
  const [activeTab, setActiveTab] = useState(0);

  const initialVersionState = {
    name: "",
    price: "",
    specs: {
      // Thông tin chung
      seats: "", type: "", origin: "", 
      // Kích thước & Khung gầm
      dimensions: "", wheelbase: "", ground_clearance: "", wheels: "",
      // Động cơ & Vận hành
      engine: "", fuel: "", fuel_tank: "", fuel_consumption: "",
      max_power: "", max_torque: "",
      gearbox: "", drivetrain: "",
      // Hệ thống treo & Phanh
      suspension: "", brakes: "", steering: ""
    }
  };

  const initialFormState = {
    name: "",
    description: "",
    yolo_labels: "", 
    versions: [{ ...initialVersionState }]
  };

  const [formData, setFormData] = useState(initialFormState);
  const [errors, setErrors] = useState({});

  useEffect(() => { loadCars(); }, []);

  useEffect(() => {
    if (searchTerm) {
      const lower = searchTerm.toLowerCase();
      const filtered = cars.filter(c => c.name.toLowerCase().includes(lower));
      setFilteredCars(filtered);
    } else {
      setFilteredCars(cars);
    }
  }, [searchTerm, cars]);

  const loadCars = async () => {
    setLoading(true);
    try {
      const data = await api.getCars();
      setCars(data);
      setFilteredCars(data);
    } catch (error) {
      console.error(error);
    }
    setLoading(false);
  };

  // --- HÀM XỬ LÝ FORM ---
  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleVersionChange = (field, value, isSpec = false) => {
    const newVersions = [...formData.versions];
    if (isSpec) {
      newVersions[activeTab].specs[field] = value;
    } else {
      newVersions[activeTab][field] = value;
    }
    setFormData({ ...formData, versions: newVersions });
  };

  const addVersion = () => {
    const currentVer = formData.versions[activeTab];
    const newVer = JSON.parse(JSON.stringify(currentVer)); 
    newVer.name = `${newVer.name} (Copy)`;
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

  // --- MỞ MODAL ---
  const openModal = (car = null) => {
    setErrors({});
    setActiveTab(0);
    if (car) {
      setEditingCar(car);
      setFormData({
        name: car.name || "",
        description: car.description || "",
        yolo_labels: car.yolo_labels ? car.yolo_labels.join(", ") : "",
        versions: (car.versions && car.versions.length > 0) 
          ? car.versions 
          : [{
              name: "Tiêu chuẩn",
              price: car.price || "", 
              specs: car.specs || car.versions?.[0]?.specs || { ...initialVersionState.specs }
            }]
      });
    } else {
      setEditingCar(null);
      setFormData(initialFormState);
    }
    setShowModal(true);
  };

  // --- LƯU DỮ LIỆU ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return setErrors({ name: "Tên xe là bắt buộc" });

    const payload = {
      ...formData,
      yolo_labels: formData.yolo_labels.split(",").map(s => s.trim()).filter(Boolean)
    };

    try {
      if (editingCar) {
        const id = editingCar.id || editingCar._id;
        const updated = await api.updateCar(id, payload);
        setCars(cars.map(c => (c.id === id || c._id === id) ? updated : c));
      } else {
        const newCar = await api.addCar(payload);
        setCars([newCar, ...cars]);
      }
      setShowModal(false);
      alert("Lưu thành công!");
    } catch (error) {
      alert("Lỗi khi lưu: " + error.message);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Xóa dòng xe này?")) {
      await api.deleteCar(id);
      setCars(cars.filter(c => (c.id !== id && c._id !== id)));
    }
  };

  const toggleRow = (carId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(carId)) newExpanded.delete(carId);
    else newExpanded.add(carId);
    setExpandedRows(newExpanded);
  };

  const renderInput = (label, value, onChange, placeholder, required = false) => (
    <div>
      <label className="block text-xs font-semibold text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input 
        type="text" 
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none"
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* HEADER */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center">
            <Database className="mr-2" /> Quản lý Dữ liệu Xe
          </h2>
          <p className="text-sm text-gray-500 mt-1">Tổng số: <b>{cars.length}</b> dòng xe</p>
        </div>
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

      {/* TABLE */}
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
              const minPrice = versions.length > 0 ? versions[0].price : "Liên hệ"; // Lấy giá bản đầu tiên

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
                    <td className="p-4">
                      <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                        {versions.length} phiên bản
                      </span>
                    </td>
                    <td className="p-4 text-red-600 font-bold text-sm">{minPrice}</td>
                    <td className="p-4 text-center flex justify-center gap-2">
                      <button onClick={() => openModal(car)} className="p-2 bg-yellow-100 text-yellow-600 rounded hover:bg-yellow-200"><Edit2 size={16}/></button>
                      <button onClick={() => handleDelete(carId)} className="p-2 bg-red-100 text-red-600 rounded hover:bg-red-200"><Trash2 size={16}/></button>
                    </td>
                  </tr>
                  {/* Expanded Rows */}
                  {isExpanded && versions.map((ver, idx) => (
                    <tr key={idx} className="bg-gray-50 text-sm border-l-4 border-blue-500">
                      <td></td>
                      <td className="p-2 pl-8 text-gray-700 font-medium">↳ {ver.name}</td>
                      <td className="p-2 text-gray-500">{ver.specs?.type}</td>
                      <td className="p-2 text-red-600 font-semibold">{ver.price}</td>
                      <td></td>
                    </tr>
                  ))}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* MODAL FULL OPTION */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-xl w-full max-w-5xl shadow-2xl flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="flex justify-between items-center p-5 border-b">
              <h3 className="text-xl font-bold flex items-center">
                {editingCar ? <Edit2 className="mr-2"/> : <Plus className="mr-2"/>}
                {editingCar ? `Sửa: ${formData.name}` : "Thêm dòng xe mới"}
              </h3>
              <button onClick={() => setShowModal(false)}><X className="text-gray-400 hover:text-red-500"/></button>
            </div>

            {/* Modal Body */}
            <div className="flex-grow overflow-y-auto p-6 custom-scrollbar">
              <form id="carForm" onSubmit={handleSubmit} className="space-y-6">
                
                {/* 1. THÔNG TIN CHUNG DÒNG XE */}
                <div className="bg-gray-50 p-4 rounded-lg border">
                  <h4 className="font-bold text-gray-700 mb-3">Thông tin dòng xe</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {renderInput("Tên dòng xe", formData.name, v => handleInputChange("name", v), "VD: Toyota Innova", true)}
                    {renderInput("Tên khác (YOLO Labels)", formData.yolo_labels, v => handleInputChange("yolo_labels", v), "VD: innova, toyota innova cross")}
                    <div className="md:col-span-2">
                        {renderInput("Mô tả ngắn", formData.description, v => handleInputChange("description", v), "Mô tả về dòng xe này...")}
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

                  {/* Tab Content - FORM CHI TIẾT (ĐÃ BỔ SUNG ĐẦY ĐỦ) */}
                  <div className="bg-white border rounded-xl p-5 shadow-sm">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      
                      {/* Hàng 1: Cơ bản */}
                      <div className="lg:col-span-4 border-b pb-2 mb-2 font-bold text-red-600 text-sm uppercase">1. Thông tin cơ bản</div>
                      {renderInput("Tên phiên bản", formData.versions[activeTab].name, v => handleVersionChange("name", v), "VD: Innova Cross V", true)}
                      {renderInput("Giá bán", formData.versions[activeTab].price, v => handleVersionChange("price", v), "VD: 810.000.000 VNĐ")}
                      {renderInput("Loại xe", formData.versions[activeTab].specs.type, v => handleVersionChange("type", v, true), "VD: MPV")}
                      {renderInput("Số chỗ", formData.versions[activeTab].specs.seats, v => handleVersionChange("seats", v, true), "VD: 8 chỗ")}
                      {renderInput("Xuất xứ", formData.versions[activeTab].specs.origin, v => handleVersionChange("origin", v, true), "VD: Nhập khẩu")}

                      {/* Hàng 2: Kích thước & Khung gầm (ĐÃ BỔ SUNG) */}
                      <div className="lg:col-span-4 border-b pb-2 mb-2 mt-4 font-bold text-red-600 text-sm uppercase">2. Kích thước & Khung gầm</div>
                      {renderInput("Kích thước DxRxC", formData.versions[activeTab].specs.dimensions, v => handleVersionChange("dimensions", v, true), "VD: 4755 x 1850 x 1790 mm")}
                      {renderInput("Chiều dài cơ sở", formData.versions[activeTab].specs.wheelbase, v => handleVersionChange("wheelbase", v, true), "VD: 2850 mm")}
                      {renderInput("Khoảng sáng gầm", formData.versions[activeTab].specs.ground_clearance, v => handleVersionChange("ground_clearance", v, true), "VD: 218 mm")}
                      {renderInput("Cỡ mâm", formData.versions[activeTab].specs.wheels, v => handleVersionChange("wheels", v, true), "VD: 18 inch")}
                      
                      {/* Hàng 3: Động cơ & Vận hành (ĐÃ BỔ SUNG) */}
                      <div className="lg:col-span-4 border-b pb-2 mb-2 mt-4 font-bold text-red-600 text-sm uppercase">3. Động cơ & Vận hành</div>
                      {renderInput("Động cơ", formData.versions[activeTab].specs.engine, v => handleVersionChange("engine", v, true), "VD: 2.0L M20A-FKS")}
                      {renderInput("Công suất", formData.versions[activeTab].specs.max_power, v => handleVersionChange("max_power", v, true), "VD: 172 mã lực")}
                      {renderInput("Mô-men xoắn", formData.versions[activeTab].specs.max_torque, v => handleVersionChange("max_torque", v, true), "VD: 205 Nm")}
                      {renderInput("Hộp số", formData.versions[activeTab].specs.gearbox, v => handleVersionChange("gearbox", v, true), "VD: CVT")}
                      {renderInput("Hệ dẫn động", formData.versions[activeTab].specs.drivetrain, v => handleVersionChange("drivetrain", v, true), "VD: Cầu trước")}
                      {renderInput("Nhiên liệu", formData.versions[activeTab].specs.fuel, v => handleVersionChange("fuel", v, true), "VD: Xăng")}
                      {renderInput("Bình nhiên liệu", formData.versions[activeTab].specs.fuel_tank, v => handleVersionChange("fuel_tank", v, true), "VD: 52 lít")}
                      {renderInput("Tiêu thụ nhiên liệu", formData.versions[activeTab].specs.fuel_consumption, v => handleVersionChange("fuel_consumption", v, true), "VD: 7.2 L/100km")}

                      {/* Hàng 4: Hệ thống an toàn & Khác (ĐÃ BỔ SUNG) */}
                      <div className="lg:col-span-4 border-b pb-2 mb-2 mt-4 font-bold text-red-600 text-sm uppercase">4. Hệ thống treo & Phanh</div>
                      {renderInput("Hệ thống treo", formData.versions[activeTab].specs.suspension, v => handleVersionChange("suspension", v, true), "VD: MacPherson / Thanh xoắn")}
                      {renderInput("Phanh trước/sau", formData.versions[activeTab].specs.brakes, v => handleVersionChange("brakes", v, true), "VD: Đĩa tản nhiệt / Đĩa")}
                      {renderInput("Trợ lực lái", formData.versions[activeTab].specs.steering, v => handleVersionChange("steering", v, true), "VD: Điện (EPS)")}
                    </div>
                  </div>
                </div>

              </form>
            </div>

            {/* Modal Footer */}
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