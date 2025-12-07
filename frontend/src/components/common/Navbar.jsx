import { Camera, History, Database, BarChart2 } from 'lucide-react'; // Đã bỏ Newspaper
import logoToyota from '../../assets/Logo.png'; 

export const Navbar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'detect', label: 'Nhận diện & Tra cứu', icon: <Camera size={20} /> },
    { id: 'history', label: 'Lịch sử', icon: <History size={20} /> },
    { id: 'dashboard', label: 'Thống kê', icon: <BarChart2 size={20} /> },
    { id: 'admin', label: 'Quản trị Dữ liệu', icon: <Database size={20} /> },
  ];

  return (
    <nav className="bg-red-700 text-white shadow-lg sticky top-0 z-50 border-b border-red-800">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          
          {/* --- PHẦN LOGO --- */}
          <div 
            className="flex items-center gap-3 cursor-pointer group" 
            onClick={() => setActiveTab('detect')}
          >
            <img 
              src={logoToyota} 
              alt="Toyota Logo" 
              className="h-10 w-auto object-contain transition-transform group-hover:scale-105 mix-blend-lighten" 
            />
            <div className="flex flex-col leading-tight hidden sm:flex">
                <span className="font-extrabold text-xl tracking-wider text-white">TOYOTA</span>
                <span className="text-xs font-bold text-red-100 tracking-wide uppercase">Computer Vision</span>
            </div>
          </div>

          {/* --- PHẦN MENU TABS (Đã bỏ Tin tức) --- */}
          <div className="flex space-x-1 sm:space-x-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm sm:text-base ${
                  activeTab === tab.id 
                    ? 'bg-red-900 text-white font-bold shadow-inner translate-y-0.5' 
                    : 'text-red-100 hover:bg-red-600 hover:text-white'
                }`}
              >
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>

        </div>
      </div>
    </nav>
  );
};