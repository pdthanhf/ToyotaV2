import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  // Giả sử bạn lưu trạng thái đăng nhập trong localStorage khi login thành công
  // Bạn có thể thay đổi điều kiện này tùy theo cách bạn xử lý auth (ví dụ: check token)
  const isAuthenticated = localStorage.getItem("isAdminLoggedIn"); 

  if (!isAuthenticated) {
    // Nếu chưa đăng nhập, chuyển hướng ngay lập tức về trang login
    return <Navigate to="/admin-login" replace />;
  }

  // Nếu đã đăng nhập, cho phép hiển thị trang con (Admin Dashboard)
  return children;
};

export default ProtectedRoute;