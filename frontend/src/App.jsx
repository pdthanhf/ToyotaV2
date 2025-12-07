import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';

// Import các trang
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import { AdminDashboard } from './components/admin/AdminDashboard'; // Đảm bảo đường dẫn này đúng với máy bạn

// --- COMPONENT BẢO VỆ ROUTE (Authorization) ---
const PrivateRoute = ({ children }) => {
  // Kiểm tra token trong localStorage (được lưu lúc đăng nhập)
  const token = localStorage.getItem('adminToken');
  
  if (!token) {
    // Nếu không có token, đá về trang login ngay lập tức
    return <Navigate to="/login" replace />;
  }
  
  // Nếu có token, cho phép truy cập
  return children;
};

// --- MAIN APP ---
const App = () => {
  return (
    <Router>
      <Routes>
        {/* Route: Đăng nhập */}
        <Route path="/login" element={<LoginPage />} />

        {/* Route: Admin (Được bảo vệ) */}
        <Route 
          path="/admin" 
          element={
            <PrivateRoute>
              {/* --- GIAO DIỆN ADMIN LAYOUT --- */}
              <div className="min-h-screen bg-gray-50">
                 
                 {/* HEADER ADMIN */}
                 <div className="bg-gray-900 text-white p-4 flex justify-between items-center shadow-md sticky top-0 z-50">
                    {/* Logo / Tiêu đề */}
                    <h1 className="font-bold text-xl flex items-center gap-2">
                        <span className="bg-red-600 px-2 rounded">Toyota</span> Admin Panel
                    </h1>

                    {/* Khu vực nút bấm điều hướng */}
                    <div className="flex gap-3">
                        {/* 1. NÚT VỀ TRANG CHỦ (Khắc phục lỗi bị kẹt) */}
                        <Link 
                            to="/" 
                            className="text-sm border border-gray-500 hover:bg-gray-800 text-gray-300 px-3 py-1 rounded transition flex items-center gap-1"
                            title="Quay về giao diện người dùng mà không đăng xuất"
                        >
                            ⬅ Về Trang Khách
                        </Link>

                        {/* 2. NÚT ĐĂNG XUẤT */}
                        <button 
                            onClick={() => {
                                // Xóa token xác thực
                                localStorage.removeItem('adminToken');
                                // Chuyển hướng cứng về trang login
                                window.location.href = '/login';
                            }} 
                            className="text-sm bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded transition font-semibold"
                        >
                            Đăng xuất
                        </button>
                    </div>
                 </div>
                 
                 {/* NỘI DUNG CHÍNH CỦA ADMIN (Dashboard) */}
                 <div className="p-6">
                    <AdminDashboard />
                 </div>
              </div>
            </PrivateRoute>
          } 
        />

        {/* Route: Trang chủ (Mặc định cho khách hàng) */}
        <Route path="/" element={<HomePage />} />
        
        {/* Route 404: Bất kỳ đường dẫn lạ nào cũng về trang chủ */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;