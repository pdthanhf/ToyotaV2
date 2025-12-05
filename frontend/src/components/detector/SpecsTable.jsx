
export const SpecsTable = ({ carData }) => {
  if (!carData) return null;

  // --- LOGIC MỚI: Lấy dữ liệu từ phiên bản đầu tiên ---
  // Nếu dữ liệu có cấu trúc versions (mới), lấy bản đầu tiên.
  // Nếu không (dữ liệu cũ), dùng chính carData.
  const version = carData.versions && carData.versions.length > 0 ? carData.versions[0] : carData;
  
  // Lấy thông số kỹ thuật (specs)
  // Nếu cấu trúc mới: nằm trong version.specs
  // Nếu cấu trúc cũ: nằm trong version (hoặc version.specs tùy lúc migration)
  const specs = version.specs || version || {};

  // Hàm render dòng dữ liệu cho gọn
  const renderRow = (label, value) => (
    <tr className="border-b last:border-b-0 hover:bg-gray-50 transition-colors">
      <td className="py-3 px-4 text-gray-600 font-medium w-1/3 bg-gray-50/50">
        {label}
      </td>
      <td className="py-3 px-4 text-gray-800 font-semibold">
        {value || <span className="text-gray-400 italic text-sm">Đang cập nhật...</span>}
      </td>
    </tr>
  );

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden h-full flex flex-col">
      {/* Header đỏ */}
      <div className="bg-red-700 text-white p-4 text-center">
        <h3 className="font-bold text-lg uppercase tracking-wide">
          THÔNG SỐ {carData.name || "XE"}
        </h3>
        {/* Hiển thị tên phiên bản nếu có */}
        {version.name && version.name !== carData.name && (
          <p className="text-red-100 text-sm mt-1 font-medium">
            Phiên bản: {version.name}
          </p>
        )}
      </div>

      {/* Bảng thông số */}
      <div className="overflow-y-auto custom-scrollbar flex-grow p-0">
        <table className="w-full text-sm text-left">
          <tbody>
            {renderRow("Tên xe", carData.name)}
            {renderRow("Giá niêm yết", <span className="text-red-600 font-bold text-base">{version.price}</span>)}
            
            {/* Nhóm thông tin chung */}
            {renderRow("Số chỗ ngồi", specs.seats)}
            {renderRow("Kiểu xe", specs.type)}
            {renderRow("Xuất xứ", specs.origin)}
            
            {/* Nhóm kích thước */}
            {renderRow("Kích thước DxRxC", specs.dimensions)}
            {renderRow("Chiều dài cơ sở", specs.wheelbase)}
            {renderRow("Khoảng sáng gầm", specs.ground_clearance)}
            {renderRow("Cỡ mâm", specs.wheels)}

            {/* Nhóm động cơ */}
            {renderRow("Động cơ", specs.engine)}
            {renderRow("Loại nhiên liệu", specs.fuel)}
            {renderRow("Dung tích bình nhiên liệu", specs.fuel_tank)}
            {renderRow("Công suất cực đại", specs.max_power)}
            {renderRow("Mô-men xoắn cực đại", specs.max_torque)}
            
            {/* Nhóm vận hành */}
            {renderRow("Hộp số", specs.gearbox || specs.transmission)}
            {renderRow("Hệ dẫn động", specs.drivetrain)}
            {renderRow("Treo trước/sau", specs.suspension)}
            {renderRow("Phanh trước/sau", specs.brakes)}
            {renderRow("Trợ lực lái", specs.steering)}
            
            {/* Tiêu thụ nhiên liệu (nếu có) */}
            {specs.consumption && renderRow("Tiêu thụ nhiên liệu", specs.consumption)}
          </tbody>
        </table>
      </div>
      
      {/* Footer ghi chú */}
      <div className="p-3 bg-gray-50 text-xs text-center text-gray-500 border-t">
        * Thông số mang tính chất tham khảo, vui lòng liên hệ đại lý để biết chi tiết.
      </div>
    </div>
  );
};