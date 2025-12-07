import axios from 'axios';

// Khai báo URL gốc (Ưu tiên lấy từ biến môi trường VITE, nếu không có thì dùng localhost)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Tạo instance axios chung với cấu hình mặc định
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000, // Timeout sau 30s
});

// =================================================================
// 1. REQUEST INTERCEPTOR (QUAN TRỌNG NHẤT)
// Tự động gắn Token vào Header nếu người dùng đã đăng nhập
// =================================================================
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('adminToken');
    if (token) {
      // Chuẩn OAuth2 thường dùng: Authorization: Bearer <token>
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// =================================================================
// 2. RESPONSE INTERCEPTOR
// Xử lý khi Token hết hạn hoặc không hợp lệ (Lỗi 401)
// =================================================================
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    // Nếu lỗi 401 (Unauthorized) -> Tự động đăng xuất
    if (err.response?.status === 401) {
      console.warn("Phiên đăng nhập hết hạn hoặc không hợp lệ.");
      localStorage.removeItem('adminToken');
      // Tùy chọn: Chuyển hướng về trang login
      // window.location.href = '/login'; 
    }
    // Trả về lỗi chi tiết từ server nếu có
    return Promise.reject(err.response?.data?.detail || err.message || 'Server error');
  }
);

// =================================================================
// 3. DANH SÁCH API EXPORT
// =================================================================
export const api = {

  // --- AUTHENTICATION (ĐĂNG NHẬP / ĐĂNG XUẤT) ---
  
  // Bước 1: Gửi Email + Password để nhận OTP
  login: async (email, password) => {
    try {
      const { data } = await apiClient.post('/auth/login', { email, password });
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Bước 2: Gửi OTP để nhận Token
  verifyOtp: async (email, otp) => {
    try {
      const { data } = await apiClient.post('/auth/verify-otp', { email, otp });
      
      // Tự động lưu token vào LocalStorage ngay tại đây để tiện lợi
      if (data.access_token) {
        localStorage.setItem('adminToken', data.access_token);
      }
      return data;
    } catch (error) {
      console.error('OTP Verify error:', error);
      throw error;
    }
  },

  // Đăng xuất: Xóa token và reload trang hoặc chuyển hướng
  logout: () => {
    localStorage.removeItem('adminToken');
    window.location.href = '/login';
  },

  // --- CARS CRUD (QUẢN LÝ XE) ---
  getCars: async () => {
    try {
      const { data } = await apiClient.get('/cars/');
      return data;
    } catch (error) {
      console.error('Error fetching cars:', error);
      return [];
    }
  },

  getCarById: async (id) => {
    try {
      const { data } = await apiClient.get(`/cars/${id}`);
      return data;
    } catch (err) {
      console.error('Error fetching car:', err);
      throw err;
    }
  },

  addCar: async (car) => {
    const { data } = await apiClient.post('/cars/', car);
    return data;
  },

  updateCar: async (id, car) => {
    const { data } = await apiClient.put(`/cars/${id}`, car);
    return data;
  },

  deleteCar: async (id) => {
    await apiClient.delete(`/cars/${id}`);
    return { success: true };
  },

  searchCars: async (keyword = '') => {
    try {
      const { data } = await apiClient.get(`/cars/search/${keyword}`);
      return data;
    } catch {
      return [];
    }
  },

  // --- DETECTION (NHẬN DIỆN ẢNH) ---
  detect: async (formData) => {
    try {
      // Upload ảnh cần timeout lâu hơn và Content-Type multipart
      const { data } = await apiClient.post('/detect/detect', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000, 
      });
      return data;
    } catch (error) {
      console.error('Detection error:', error);
      throw error;
    }
  },

  getClasses: async () => (await apiClient.get('/detect/classes')).data,

  // --- FEEDBACK / CORRECTION (Gửi phản hồi sai/đúng) ---
  sendFeedback: async (feedbackData) => {
    try {
      const { data } = await apiClient.post('/correct/', feedbackData);
      return data;
    } catch (error) {
      console.error('Error sending feedback:', error);
      throw error;
    }
  },

  // --- ADMIN FEEDBACK MANAGEMENT (Duyệt phản hồi) ---
  getCorrections: async (status = 'pending') => {
    try {
      const { data } = await apiClient.get(`/correct/?status=${status}`);
      return data;
    } catch (error) {
      console.error("Lỗi lấy danh sách feedback:", error);
      return [];
    }
  },

  approveCorrection: async (id) => {
    try {
      const { data } = await apiClient.put(`/correct/${id}/approve`);
      return data;
    } catch (error) {
      console.error("Lỗi duyệt feedback:", error);
      throw error;
    }
  },

  rejectCorrection: async (id) => {
    try {
      const { data } = await apiClient.put(`/correct/${id}/reject`);
      return data;
    } catch (error) {
      console.error("Lỗi từ chối feedback:", error);
      throw error;
    }
  },

  // --- HISTORY (Lịch sử nhận diện) ---
  getHistory: async (params = {}) => {
    try {
      const { data } = await apiClient.get('/history/', { params });
      return data;
    } catch (error) {
      console.error('Error fetching history:', error);
      return [];
    }
  },

  getHistoryById: async (id) => {
    const { data } = await apiClient.get(`/history/${id}`);
    return data;
  },

  deleteHistory: async (id) => {
    await apiClient.delete(`/history/${id}`);
    return { success: true };
  },

  getHistoryStats: async () => {
    try {
      const { data } = await apiClient.get('/history/stats/summary');
      return data;
    } catch (error) {
      console.error('Error fetching history stats:', error);
      return { total_detections: 0, today: 0, last_7_days: 0 };
    }
  },

  // --- ANALYTICS (Thống kê) ---
  getTopDetectedCars: async (limit = 10) => {
    try {
      const { data } = await apiClient.get(`/stats/top-cars?limit=${limit}`);
      return data;
    } catch (error) {
      console.error('Error fetching top cars:', error);
      return [];
    }
  },

  getTrainingStats: async () => {
    try {
      const { data } = await apiClient.get('/training/stats');
      return data;
    } catch (error) {
      console.error('Error fetching training stats:', error);
      return { total: 0, pending: 0, approved: 0, by_priority: {} };
    }
  },

  // --- AUDIT LOGS (Nhật ký hoạt động) ---
  getEntityHistory: async (entityType, entityId) => {
    try {
      const { data } = await apiClient.get(`/audit/entity/${entityType}/${entityId}`);
      return data;
    } catch (error) {
      console.error('Error fetching entity history:', error);
      return { history: [] };
    }
  },

  getRecentActivities: async (days = 7) => {
    try {
      const { data } = await apiClient.get(`/audit/recent?days=${days}`);
      return data;
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      return { activities: [] };
    }
  },

  // --- DASHBOARD TỔNG HỢP ---
  getDashboardStats: async () => {
    try {
      const { data } = await apiClient.get('/dashboard/stats');
      return data;
    } catch (error) {
      console.error("Lỗi lấy thống kê dashboard:", error);
      return {
        total_detections: 0,
        avg_confidence: 0,
        popular_cars: [],
        detections_timeline: [],
        detection_by_hour: []
      };
    }
  }
};