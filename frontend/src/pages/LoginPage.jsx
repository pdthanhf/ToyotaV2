import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Thêm Link
import { api } from '../api'; 
import { ShieldCheck, Mail, Lock, ArrowRight, CheckCircle, AlertCircle, Home } from 'lucide-react';

const LoginPage = () => {
  const [step, setStep] = useState(1); 
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  // --- BƯỚC 1: GỬI EMAIL & PASSWORD ---
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.login(email, password); 
      setStep(2); 
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Đăng nhập thất bại. Vui lòng kiểm tra lại!";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // --- BƯỚC 2: XÁC THỰC OTP ---
  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.verifyOtp(email, otp);
      const token = response.access_token || response.token || response.data?.token;

      if (token) {
         localStorage.setItem('adminToken', token);
         navigate('/admin');
      } else {
         throw new Error("Không nhận được mã xác thực từ máy chủ.");
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || "Mã OTP không chính xác hoặc đã hết hạn.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-800 to-red-950 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in-up">
        
        {/* Header */}
        <div className="bg-gray-50 p-8 text-center border-b">
          <div className="bg-red-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 text-red-600 shadow-inner ring-4 ring-red-50">
            <ShieldCheck size={40} />
          </div>
          <h2 className="text-3xl font-extrabold text-gray-800 tracking-tight">Toyota Admin</h2>
          <p className="text-gray-500 mt-2 text-sm font-medium">Hệ thống quản trị bảo mật 2 lớp</p>
        </div>

        <div className="p-8">
          
          {/* Thông báo lỗi */}
          {error && (
            <div className="mb-6 bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded flex items-start text-sm">
                <AlertCircle size={18} className="mr-2 mt-0.5 flex-shrink-0"/>
                <span>{error}</span>
            </div>
          )}

          {step === 1 ? (
            /* --- FORM BƯỚC 1 --- */
            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Email quản trị</label>
                <div className="relative group">
                  <Mail className="absolute left-3 top-3.5 text-gray-400 group-focus-within:text-red-600 transition-colors" size={20}/>
                  <input 
                    type="email" value={email} onChange={e => setEmail(e.target.value)} 
                    required 
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all bg-gray-50 focus:bg-white"
                    placeholder="admin@toyota.com"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Mật khẩu</label>
                <div className="relative group">
                  <Lock className="absolute left-3 top-3.5 text-gray-400 group-focus-within:text-red-600 transition-colors" size={20}/>
                  <input 
                    type="password" value={password} onChange={e => setPassword(e.target.value)} 
                    required 
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all bg-gray-50 focus:bg-white"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <button disabled={loading} className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3.5 rounded-lg shadow-lg hover:shadow-red-500/30 transition-all flex items-center justify-center group disabled:opacity-70">
                {loading ? "Đang kết nối server..." : <>Đăng nhập <ArrowRight size={20} className="ml-2 group-hover:translate-x-1 transition-transform"/></>}
              </button>

              {/* 👇 NÚT QUAY VỀ TRANG CHỦ (BƯỚC 1) 👇 */}
              <div className="text-center pt-2">
                <Link to="/" className="inline-flex items-center text-sm text-gray-500 hover:text-red-600 font-medium transition-colors">
                    <Home size={16} className="mr-1.5" /> 
                    Quay lại Trang chủ 
                </Link>
              </div>

            </form>
          ) : (
            /* --- FORM BƯỚC 2 --- */
            <form onSubmit={handleVerify} className="space-y-6 animate-fade-in-right">
              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-sm text-blue-800 flex items-start">
                <CheckCircle size={20} className="mr-3 mt-0.5 flex-shrink-0 text-blue-600"/> 
                <span>Mã xác nhận đã gửi tới <strong>{email}</strong>.</span>
              </div>
              
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-3 text-center uppercase tracking-widest">Nhập mã OTP</label>
                <input 
                  type="text" value={otp} onChange={e => setOtp(e.target.value)} 
                  maxLength={6} 
                  className="w-full p-4 text-center text-4xl tracking-[12px] font-bold border-2 border-gray-200 rounded-xl focus:border-red-500 focus:ring-4 focus:ring-red-100 outline-none transition-all font-mono text-gray-800"
                  placeholder="------"
                  autoFocus
                />
              </div>

              <button disabled={loading} className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3.5 rounded-lg shadow-lg hover:shadow-green-500/30 transition-all disabled:opacity-70">
                {loading ? "Đang xác thực..." : "XÁC NHẬN & VÀO HỆ THỐNG"}
              </button>
              
              <div className="flex flex-col gap-3 mt-4">
                  <button 
                    type="button" 
                    onClick={() => { setStep(1); setError(''); setOtp(''); }} 
                    className="w-full text-gray-400 text-sm hover:text-gray-600 font-medium transition-colors"
                  >
                    ← Quay lại bước trước
                  </button>

                  {/* 👇 NÚT QUAY VỀ TRANG CHỦ (BƯỚC 2 - Dự phòng) 👇 */}
                  <Link to="/" className="w-full text-center text-gray-400 text-sm hover:text-red-600 font-medium transition-colors">
                     Về trang chủ
                  </Link>
              </div>
            </form>
          )}
        </div>
        
        <div className="bg-gray-50 py-3 text-center border-t">
            <p className="text-xs text-gray-400">© 2025 Toyota Computer Vision Security</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;