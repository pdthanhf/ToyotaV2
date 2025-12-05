import axios from 'axios';

// Khai báo URL gốc
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Tạo instance axios chung
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// ================== RESPONSE INTERCEPTOR ==================
apiClient.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err.response?.data?.detail || 'Server error')
);

export const api = {

  // ================== CARS CRUD ==================
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

  // ================== DETECTION ==================
  detect: async (formData) => {
    try {
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

  
  // ================== HISTORY ==================
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

  // --- Stats lịch sử ---
  getHistoryStats: async () => {
    try {
      const { data } = await apiClient.get('/history/stats/summary');
      return data;
    } catch (error) {
      console.error('Error fetching history stats:', error);
      return { total_detections: 0, today: 0, last_7_days: 0 };
    }
  },


  // ================== ANALYTICS ==================
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


  // ================== AUDIT LOGS ==================
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

  // ================== DASHBOARD (ĐÃ SỬA LỖI) ==================
  getDashboardStats: async () => {
    try {
      // SỬA LỖI: Dùng apiClient thay vì axios trực tiếp để tránh lỗi biến API_URL
      // apiClient đã tự động thêm base URL (http://localhost:8000/api)
      const { data } = await apiClient.get('/dashboard/stats');
      return data;
    } catch (error) {
      console.error("Lỗi lấy thống kê dashboard:", error);
      // Trả về dữ liệu mặc định để không crash UI nếu lỗi
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