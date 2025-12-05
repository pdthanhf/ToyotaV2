import pymongo

# --- 1. KẾT NỐI MONGODB ---
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["toyota_v2_db"]
collection = db["car_info"]

# --- 2. DỮ LIỆU CHI TIẾT (Mapping đủ 41 Class YOLO) ---
full_data_cars = [
    # --- 1. TOYOTA VIOS ---
    {
        "name": "Toyota Vios",
        "yolo_labels": ["Toyota Vios", "Toyota Vios_sedan"],
        "description": "Ông vua doanh số phân khúc B. Bền bỉ, rộng rãi, chi phí sử dụng thấp.",
        "versions": [
            {
                "name": "1.5E MT (Số sàn)",
                "price": "479.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Lắp ráp VN",
                    "dimensions": "4425 x 1730 x 1475 mm",
                    "wheelbase": "2550 mm",
                    "engine": "1.5L Dual VVT-i (2NR-FE)",
                    "max_power": "107 mã lực @ 6000 rpm",
                    "max_torque": "140 Nm @ 4200 rpm",
                    "gearbox": "Số sàn 5 cấp",
                    "drivetrain": "Cầu trước (FWD)",
                    "suspension": "Độc lập MacPherson / Dầm xoắn",
                    "brakes": "Đĩa thông gió / Đĩa đặc",
                    "wheels": "15 inch",
                    "ground_clearance": "133 mm",
                    "fuel_tank": "42 lít"
                }
            },
            {
                "name": "1.5G CVT",
                "price": "592.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Lắp ráp VN",
                    "dimensions": "4425 x 1730 x 1475 mm",
                    "engine": "1.5L Dual VVT-i (2NR-FE)",
                    "max_power": "107 mã lực",
                    "gearbox": "Tự động vô cấp CVT",
                    "drivetrain": "Cầu trước (FWD)",
                    "features": "7 túi khí, Cruise Control, Màn hình 7 inch",
                    "fuel_tank": "42 lít"
                }
            }
        ]
    },
    
    # --- 2. TOYOTA CAMRY ---
    {
        "name": "Toyota Camry",
        "yolo_labels": [
            "Toyota Camry", "Toyota Camry XSE", "Toyota Camry XV40", 
            "Toyota Camry XV50", "Toyota Camry_Hybrid", "Toyota Camry_sedan"
        ],
        "description": "Biểu tượng sedan hạng D sang trọng với nền tảng toàn cầu TNGA êm ái tuyệt đối.",
        "versions": [
            {
                "name": "2.0Q",
                "price": "1.220.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Thái Lan",
                    "dimensions": "4885 x 1840 x 1445 mm",
                    "wheelbase": "2825 mm",
                    "engine": "2.0L (M20A-FKS)",
                    "max_power": "170 mã lực",
                    "max_torque": "206 Nm",
                    "gearbox": "Direct Shift CVT",
                    "drivetrain": "Cầu trước (FWD)",
                    "suspension": "MacPherson / Tay đòn kép",
                    "brakes": "Đĩa tản nhiệt / Đĩa đặc",
                    "wheels": "18 inch đa chấu"
                }
            },
            {
                "name": "2.5 HEV (Hybrid)",
                "price": "1.495.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Thái Lan",
                    "engine": "2.5L Xăng + Mô tơ điện",
                    "max_power": "176 hp + 118 hp (điện)",
                    "gearbox": "E-CVT",
                    "fuel_consumption": "4.4L/100km (Siêu tiết kiệm)",
                    "features": "Cửa sổ trời, TSS, HUD, Camera 360"
                }
            },
            {
                "name": "XV40/XV50 (Đời cũ)",
                "price": "300 - 600.000.000 VNĐ",
                "specs": {
                    "engine": "2.4L / 2.5L / 3.5L",
                    "note": "Các phiên bản đời 2007-2018 nồi đồng cối đá"
                }
            },
            {
                "name": "Camry XSE (Nhập Mỹ)",
                "price": "Khoảng 2 tỷ VNĐ",
                "specs": {
                    "origin": "Nhập Mỹ",
                    "style": "Thiết kế thể thao, pô kép, mặt ca-lăng lưới tổ ong"
                }
            }
        ]
    },

    # --- 3. TOYOTA FORTUNER ---
    {
        "name": "Toyota Fortuner",
        "yolo_labels": ["Toyota Fortuner"],
        "description": "SUV 7 chỗ khung gầm rời, mạnh mẽ, chinh phục mọi địa hình.",
        "versions": [
            {
                "name": "2.4 MT 4x2 (Máy dầu)",
                "price": "1.026.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ",
                    "origin": "Lắp ráp VN",
                    "dimensions": "4795 x 1855 x 1835 mm",
                    "wheelbase": "2745 mm",
                    "engine": "2.4L Diesel (2GD-FTV)",
                    "max_power": "147 mã lực @ 3400 rpm",
                    "max_torque": "400 Nm @ 1600 rpm",
                    "gearbox": "Số sàn 6 cấp",
                    "drivetrain": "Cầu sau (RWD)",
                    "suspension": "Độc lập tay đòn kép / Phụ thuộc liên kết 4 điểm",
                    "ground_clearance": "279 mm",
                    "fuel_tank": "80 lít"
                }
            },
            {
                "name": "2.8 Legender 4x4",
                "price": "1.470.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ",
                    "origin": "Lắp ráp VN",
                    "engine": "2.8L Diesel Turbo (1GD-FTV)",
                    "max_power": "201 mã lực @ 3400 rpm",
                    "max_torque": "500 Nm @ 1600 rpm",
                    "gearbox": "Tự động 6 cấp",
                    "drivetrain": "2 cầu bán thời gian (4WD)",
                    "features": "Đá cốp, Loa JBL, Camera 360"
                }
            }
        ]
    },

    # --- 4. TOYOTA INNOVA ---
    {
        "name": "Toyota Innova",
        "yolo_labels": ["Toyota Innova", "Toyota Innova Cross"],
        "description": "MPV đa dụng. Bản Cross thế hệ mới êm ái như sedan, bản cũ bền bỉ.",
        "versions": [
            {
                "name": "Innova Cross V",
                "price": "810.000.000 VNĐ",
                "specs": {
                    "seats": "8 chỗ",
                    "origin": "Nhập khẩu",
                    "dimensions": "4755 x 1850 x 1790 mm",
                    "wheelbase": "2850 mm",
                    "engine": "2.0L M20A-FKS",
                    "max_power": "172 mã lực",
                    "gearbox": "Direct Shift CVT",
                    "drivetrain": "Cầu trước (FWD)",
                    "suspension": "MacPherson / Thanh xoắn"
                }
            },
            {
                "name": "Innova Cross HEV (Hybrid)",
                "price": "990.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ (Ghế thương gia)",
                    "engine": "2.0L Hybrid",
                    "max_power": "150 hp + 111 hp (điện)",
                    "gearbox": "E-CVT",
                    "features": "Cửa sổ trời toàn cảnh, Cốp điện, TSS"
                }
            }
        ]
    },

    # --- 5. TOYOTA COROLLA ALTIS ---
    {
        "name": "Toyota Corolla Altis",
        "yolo_labels": [
            "Toyota Corolla Altis", "Toyota Corolla Altis_sedan", 
            "Toyota Corolla EX_sedan", "Toyota Corolla Furia"
        ],
        "description": "Sedan hạng C chuẩn mực, thiết kế lịch lãm, an toàn hàng đầu.",
        "versions": [
            {
                "name": "1.8V",
                "price": "765.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Thái Lan",
                    "dimensions": "4630 x 1780 x 1435 mm",
                    "engine": "1.8L (2ZR-FBE)",
                    "max_power": "138 mã lực",
                    "gearbox": "CVT",
                    "features": "Gói an toàn Toyota Safety Sense"
                }
            },
            {
                "name": "1.8HEV (Hybrid)",
                "price": "860.000.000 VNĐ",
                "specs": {
                    "engine": "1.8L Hybrid",
                    "gearbox": "E-CVT",
                    "fuel_consumption": "4.3 L/100km",
                    "features": "HUD, Cảnh báo áp suất lốp"
                }
            }
        ]
    },

    # --- 6. TOYOTA YARIS CROSS ---
    {
        "name": "Toyota Yaris Cross",
        "yolo_labels": ["Toyota Yaris Cross"],
        "description": "B-SUV hoàn toàn mới, thiết kế năng động, option miên man.",
        "versions": [
            {
                "name": "Máy xăng",
                "price": "730.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Indonesia",
                    "dimensions": "4310 x 1770 x 1615 mm",
                    "engine": "1.5L (2NR-VE)",
                    "max_power": "105 mã lực",
                    "gearbox": "D-CVT",
                    "drivetrain": "Cầu trước"
                }
            },
            {
                "name": "Hybrid (HEV)",
                "price": "838.000.000 VNĐ",
                "specs": {
                    "engine": "1.5L Hybrid",
                    "gearbox": "E-CVT",
                    "fuel_consumption": "3.56 L/100km (Đô thị)",
                    "features": "Cốp điện đá cốp, Kính trần toàn cảnh"
                }
            }
        ]
    },

    # --- 7. TOYOTA LAND CRUISER ---
    {
        "name": "Toyota Land Cruiser",
        "yolo_labels": ["Toyota Land Cruiser", "Toyota Land Cruiser_suv"],
        "description": "Vua địa hình, đẳng cấp doanh nhân, cháy hàng toàn cầu (LC300).",
        "versions": [
            {
                "name": "LC300",
                "price": "4.286.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ",
                    "origin": "Nhập khẩu Nhật Bản",
                    "dimensions": "4965 x 1980 x 1945 mm",
                    "engine": "3.5L V6 Twin Turbo",
                    "max_power": "409 mã lực",
                    "max_torque": "650 Nm",
                    "gearbox": "Tự động 10 cấp",
                    "drivetrain": "4WD Full-time, 3 khóa vi sai",
                    "features": "MTS, Crawl Control, Vân tay khởi động"
                }
            }
        ]
    },

    # --- 8. TOYOTA LAND CRUISER PRADO ---
    {
        "name": "Toyota Land Cruiser Prado",
        "yolo_labels": ["Toyota Prado_suv"],
        "description": "SUV hạng sang cỡ trung, bền bỉ và giữ giá.",
        "versions": [
            {
                "name": "Prado VX",
                "price": "2.628.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ",
                    "origin": "Nhập khẩu Nhật Bản",
                    "dimensions": "4840 x 1885 x 1890 mm",
                    "engine": "2.7L Xăng (2TR-FE)",
                    "max_power": "164 mã lực",
                    "max_torque": "246 Nm",
                    "gearbox": "Tự động 6 cấp",
                    "drivetrain": "2 cầu toàn thời gian (AWD)",
                    "wheels": "19 inch",
                    "features": "Loa JBL, Làm mát ghế, TSS"
                }
            }
        ]
    },

    # --- 9. TOYOTA RAIZE ---
    {
        "name": "Toyota Raize",
        "yolo_labels": ["Toyota Raize"],
        "description": "SUV đô thị gầm cao cỡ nhỏ (A+), động cơ Turbo linh hoạt.",
        "versions": [
            {
                "name": "1.0 Turbo",
                "price": "498.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Indonesia",
                    "dimensions": "4030 x 1710 x 1605 mm",
                    "engine": "1.0L Turbo (1KR-VET)",
                    "max_power": "98 mã lực",
                    "max_torque": "140 Nm",
                    "gearbox": "D-CVT",
                    "ground_clearance": "200 mm",
                    "features": "Lẫy chuyển số vô lăng, Cảnh báo điểm mù"
                }
            }
        ]
    },

    # --- 10. TOYOTA VELOZ CROSS ---
    {
        "name": "Toyota Veloz Cross",
        "yolo_labels": ["Toyota Veloz Cross"],
        "description": "MPV 7 chỗ phong cách Crossover, thiết kế sắc sảo.",
        "versions": [
            {
                "name": "CVT Top",
                "price": "660.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ",
                    "origin": "Lắp ráp VN",
                    "dimensions": "4475 x 1750 x 1700 mm",
                    "engine": "1.5L (2NR-VE)",
                    "max_power": "105 mã lực",
                    "gearbox": "D-CVT",
                    "features": "Toyota Safety Sense, Sạc không dây, Phanh tay điện tử"
                }
            }
        ]
    },

    # --- 11. TOYOTA AVANZA PREMIO ---
    {
        "name": "Toyota Avanza Premio",
        "yolo_labels": ["Toyota Avanza"],
        "description": "MPV 7 chỗ thực dụng, giá rẻ nhất nhà Toyota.",
        "versions": [
            {
                "name": "CVT",
                "price": "598.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ",
                    "origin": "Lắp ráp VN",
                    "engine": "1.5L",
                    "gearbox": "CVT",
                    "drivetrain": "Cầu trước"
                }
            }
        ]
    },

    # --- 12. TOYOTA WIGO ---
    {
        "name": "Toyota Wigo",
        "yolo_labels": ["Toyota Wigo"],
        "description": "Xe hạng A rộng nhất phân khúc, nhập khẩu nguyên chiếc.",
        "versions": [
            {
                "name": "G CVT",
                "price": "405.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Indonesia",
                    "dimensions": "3760 x 1665 x 1505 mm",
                    "engine": "1.2L (WA-VE)",
                    "max_power": "87 mã lực",
                    "gearbox": "D-CVT",
                    "features": "Cảnh báo điểm mù, Cân bằng điện tử"
                }
            }
        ]
    },

    # --- 13. TOYOTA YARIS ---
    {
        "name": "Toyota Yaris",
        "yolo_labels": ["Toyota Yaris", "Toyota Yaris_hatchback"],
        "description": "Biến thể Hatchback của Vios, thời trang và linh hoạt.",
        "versions": [
            {
                "name": "1.5G CVT",
                "price": "684.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Thái Lan",
                    "engine": "1.5L",
                    "gearbox": "CVT",
                    "type": "Hatchback"
                }
            }
        ]
    },

    # --- 14. TOYOTA HILUX ---
    {
        "name": "Toyota Hilux",
        "yolo_labels": ["Toyota Hilux"],
        "description": "Bán tải bền bỉ, mạnh mẽ, đúng chất 'nồi đồng cối đá'.",
        "versions": [
            {
                "name": "2.8 Adventure 4x4",
                "price": "999.000.000 VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Thái Lan",
                    "dimensions": "5325 x 1855 x 1815 mm",
                    "engine": "2.8L Diesel",
                    "max_power": "201 mã lực",
                    "max_torque": "500 Nm",
                    "drivetrain": "2 cầu (4x4)",
                    "gearbox": "Tự động 6 cấp"
                }
            }
        ]
    },

    # --- 15. TOYOTA ALPHARD ---
    {
        "name": "Toyota Alphard",
        "yolo_labels": ["Toyota Alphard", "Toyota Alphard_mpv", "Alphard"],
        "description": "Chuyên cơ mặt đất, MPV hạng sang đắt giá nhất.",
        "versions": [
            {
                "name": "Alphard Luxury Hybrid",
                "price": "4.370.000.000 VNĐ",
                "specs": {
                    "seats": "7 chỗ (Thương gia)",
                    "origin": "Nhập khẩu Nhật Bản",
                    "engine": "2.4L Turbo Hybrid",
                    "max_power": "275 mã lực",
                    "gearbox": "Tự động 8 cấp"
                }
            }
        ]
    },

    # --- 16. TOYOTA RUSH ---
    {
        "name": "Toyota Rush",
        "yolo_labels": ["Toyota Rush"],
        "description": "Tiểu Fortuner, dẫn động cầu sau khỏe khoắn (Đã ngừng bán xe mới).",
        "versions": [
            {
                "name": "1.5 AT",
                "price": "Xe cũ (~500 triệu VNĐ)",
                "specs": {
                    "seats": "7 chỗ",
                    "engine": "1.5L",
                    "gearbox": "Tự động 4 cấp",
                    "drivetrain": "Cầu sau (RWD)",
                    "origin": "Nhập khẩu Indonesia"
                }
            }
        ]
    },

    # --- 17. TOYOTA PRIUS ---
    {
        "name": "Toyota Prius",
        "yolo_labels": ["Toyota Prius", "Toyota Prius_hybrid"],
        "description": "Biểu tượng xe Hybrid toàn cầu, thiết kế Futuristic.",
        "versions": [
            {
                "name": "Prius HEV (2024)",
                "price": "Nhập tư nhân (Liên hệ)",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu",
                    "engine": "2.0L Hybrid",
                    "max_power": "194 mã lực",
                    "gearbox": "E-CVT"
                }
            }
        ]
    },

    # --- 18. TOYOTA RAV4 ---
    {
        "name": "Toyota RAV4",
        "yolo_labels": ["Toyota RAV4", "Toyota RAV4_suv"],
        "description": "Mẫu Crossover bán chạy nhất thế giới tại thị trường Mỹ.",
        "versions": [
            {
                "name": "XLE Premium",
                "price": "Nhập Mỹ (~2 tỷ VNĐ)",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Mỹ",
                    "engine": "2.5L Dynamic Force",
                    "max_power": "203 mã lực",
                    "gearbox": "Tự động 8 cấp"
                }
            }
        ]
    },

    # --- 19. TOYOTA TUNDRA ---
    {
        "name": "Toyota Tundra",
        "yolo_labels": ["Toyota Tundra_pickup"],
        "description": "Siêu bán tải cỡ lớn (Full-size) tại Mỹ, đối trọng Ford F-150.",
        "versions": [
            {
                "name": "1794 Edition",
                "price": "Hơn 4 tỷ VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Mỹ",
                    "dimensions": "5933 x 2037 x 1981 mm",
                    "engine": "i-FORCE 3.5L V6 Twin-Turbo",
                    "max_power": "389 mã lực",
                    "gearbox": "Tự động 10 cấp"
                }
            }
        ]
    },

    # --- 20. TOYOTA 4RUNNER ---
    {
        "name": "Toyota 4Runner",
        "yolo_labels": ["Toyota 4Runner_SUV"],
        "description": "SUV địa hình chuyên nghiệp, cực kỳ bền bỉ tại Mỹ.",
        "versions": [
            {
                "name": "TRD Pro",
                "price": "Hơn 4 tỷ VNĐ",
                "specs": {
                    "seats": "5 chỗ",
                    "origin": "Nhập khẩu Mỹ",
                    "engine": "4.0L V6",
                    "drivetrain": "4WD",
                    "suspension": "Fox Shocks chuyên offroad"
                }
            }
        ]
    },

    # --- 21. TOYOTA CROWN ---
    {
        "name": "Toyota Crown",
        "yolo_labels": ["Toyota Crown_sedan"],
        "description": "Biểu tượng xe sang nội địa Nhật (JDM), logo vương miện.",
        "versions": [
            {
                "name": "Crown Crossover",
                "price": "Nhập khẩu (Liên hệ)",
                "specs": {
                    "origin": "Nhật Bản",
                    "engine": "2.4L Turbo Hybrid / 2.5L Hybrid",
                    "style": "Sedan gầm cao lai Crossover"
                }
            }
        ]
    },

    # --- 22. TOYOTA AYGO ---
    {
        "name": "Toyota Aygo",
        "yolo_labels": ["Toyota Aygo_hatchback"],
        "description": "Xe đô thị cỡ nhỏ (City car) tại thị trường Châu Âu.",
        "versions": [
            {
                "name": "Aygo X",
                "price": "Thị trường Châu Âu",
                "specs": {
                    "seats": "4 chỗ",
                    "origin": "Châu Âu",
                    "engine": "1.0L 3 xy-lanh",
                    "gearbox": "Sàn / CVT"
                }
            }
        ]
    },

    # --- 23. TOYOTA GT86 / 86 ---
    {
        "name": "Toyota GT86",
        "yolo_labels": ["Toyota GT86", "GT86", "Toyota 86_sport"],
        "description": "Xe thể thao 2 cửa, trọng tâm thấp, cảm giác lái thuần khiết.",
        "versions": [
            {
                "name": "GT86 Standard",
                "price": "Xe cũ (~1.5 tỷ VNĐ)",
                "specs": {
                    "seats": "4 chỗ (2+2)",
                    "origin": "Nhập khẩu Nhật Bản",
                    "engine": "2.0L Boxer (Subaru)",
                    "max_power": "197 mã lực",
                    "drivetrain": "Cầu sau (RWD)"
                }
            }
        ]
    },

    # --- 24. TOYOTA SUPRA ---
    {
        "name": "Toyota Supra",
        "yolo_labels": ["Toyota Supra"],
        "description": "Huyền thoại xe đua đường phố, hợp tác cùng BMW.",
        "versions": [
            {
                "name": "GR Supra",
                "price": "Nhập khẩu (Liên hệ)",
                "specs": {
                    "seats": "2 chỗ",
                    "origin": "Áo (Magna Steyr)",
                    "engine": "3.0L I6 Turbo (BMW B58)",
                    "max_power": "382 mã lực",
                    "gearbox": "Tự động 8 cấp ZF"
                }
            }
        ]
    }
]

# --- 3. THỰC HIỆN NẠP DỮ LIỆU ---
print("Đang xóa dữ liệu cũ và nạp mới...")
collection.delete_many({}) # Xóa sạch để tránh trùng lặp

try:
    result = collection.insert_many(full_data_cars)
    print(f"✅ THÀNH CÔNG! Đã nạp đủ {len(result.inserted_ids)} dòng xe (Bao gồm đầy đủ 41 nhãn YOLO).")
except Exception as e:
    print(f"❌ CÓ LỖI: {e}")