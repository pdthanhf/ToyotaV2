"""
File preprocess.py - Xử lý tiền xử lý ảnh
"""

from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from typing import Tuple, Optional
import cv2


def resize_image(
    image: Image.Image, 
    target_size: Tuple[int, int] = (640, 640),
    keep_aspect_ratio: bool = True
) -> Image.Image:
    """
    Resize ảnh về kích thước chuẩn
    
    Args:
        image: PIL Image
        target_size: (width, height)
        keep_aspect_ratio: Giữ tỷ lệ khung hình
        
    Returns:
        PIL Image đã resize
    """
    if keep_aspect_ratio:
        # Resize giữ tỷ lệ, padding phần thừa
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Tạo canvas mới và paste ảnh vào giữa
        new_image = Image.new('RGB', target_size, (128, 128, 128))
        paste_x = (target_size[0] - image.width) // 2
        paste_y = (target_size[1] - image.height) // 2
        new_image.paste(image, (paste_x, paste_y))
        
        return new_image
    else:
        # Resize trực tiếp (có thể méo ảnh)
        return image.resize(target_size, Image.Resampling.LANCZOS)


def normalize_image(image: Image.Image) -> np.ndarray:
    """
    Normalize ảnh về range [0, 1]
    
    Args:
        image: PIL Image
        
    Returns:
        numpy array đã normalize
    """
    img_array = np.array(image).astype(np.float32)
    img_array = img_array / 255.0
    return img_array


def enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
    """
    Tăng độ tương phản
    
    Args:
        image: PIL Image
        factor: Hệ số tăng (1.0 = giữ nguyên)
        
    Returns:
        PIL Image
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def enhance_brightness(image: Image.Image, factor: float = 1.2) -> Image.Image:
    """
    Tăng độ sáng
    
    Args:
        image: PIL Image
        factor: Hệ số tăng (1.0 = giữ nguyên)
        
    Returns:
        PIL Image
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def enhance_sharpness(image: Image.Image, factor: float = 2.0) -> Image.Image:
    """
    Tăng độ sắc nét
    
    Args:
        image: PIL Image
        factor: Hệ số tăng (1.0 = giữ nguyên)
        
    Returns:
        PIL Image
    """
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)


def auto_enhance(image: Image.Image) -> Image.Image:
    """
    Tự động enhance ảnh (contrast + brightness)
    
    Args:
        image: PIL Image
        
    Returns:
        PIL Image đã enhance
    """
    # Auto contrast
    image = ImageOps.autocontrast(image)
    
    # Auto brightness (equalize)
    image = ImageOps.equalize(image)
    
    return image


def remove_noise(image: Image.Image, kernel_size: int = 3) -> Image.Image:
    """
    Loại bỏ nhiễu bằng Gaussian Blur
    
    Args:
        image: PIL Image
        kernel_size: Kích thước kernel (phải là số lẻ)
        
    Returns:
        PIL Image
    """
    img_array = np.array(image)
    
    # Gaussian Blur
    blurred = cv2.GaussianBlur(img_array, (kernel_size, kernel_size), 0)
    
    return Image.fromarray(blurred)


def crop_to_square(image: Image.Image) -> Image.Image:
    """
    Crop ảnh thành hình vuông (từ trung tâm)
    
    Args:
        image: PIL Image
        
    Returns:
        PIL Image hình vuông
    """
    width, height = image.size
    
    # Lấy kích thước nhỏ nhất
    size = min(width, height)
    
    # Tính toán vùng crop
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    
    return image.crop((left, top, right, bottom))


def preprocess_for_detection(
    image: Image.Image,
    target_size: Tuple[int, int] = (640, 640),
    enhance: bool = False
) -> Image.Image:
    """
    Pipeline tiền xử lý hoàn chỉnh cho detection
    
    Args:
        image: PIL Image
        target_size: Kích thước đầu ra
        enhance: Có tự động enhance không
        
    Returns:
        PIL Image đã preprocess
    """
    # 1. Convert sang RGB nếu cần
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # 2. Auto enhance (optional)
    if enhance:
        image = auto_enhance(image)
    
    # 3. Resize về kích thước chuẩn
    image = resize_image(image, target_size, keep_aspect_ratio=True)
    
    return image


def validate_image(image: Image.Image) -> Tuple[bool, str]:
    """
    Kiểm tra ảnh có hợp lệ không
    
    Args:
        image: PIL Image
        
    Returns:
        (is_valid, error_message)
    """
    # Kiểm tra kích thước tối thiểu
    if image.width < 100 or image.height < 100:
        return False, "Image too small (min 100x100)"
    
    # Kiểm tra kích thước tối đa
    if image.width > 10000 or image.height > 10000:
        return False, "Image too large (max 10000x10000)"
    
    # Kiểm tra mode
    if image.mode not in ['RGB', 'RGBA', 'L']:
        return False, f"Unsupported image mode: {image.mode}"
    
    return True, ""


# ==================== AUGMENTATION (cho training) ====================

def horizontal_flip(image: Image.Image) -> Image.Image:
    """Lật ảnh ngang"""
    return ImageOps.mirror(image)


def rotate_image(image: Image.Image, angle: float) -> Image.Image:
    """
    Xoay ảnh
    
    Args:
        image: PIL Image
        angle: Góc xoay (độ)
        
    Returns:
        PIL Image đã xoay
    """
    return image.rotate(angle, expand=True, fillcolor=(128, 128, 128))


# ==================== TESTING ====================

if __name__ == "__main__":
    print("Testing preprocess functions...")
    
    # Test với ảnh mẫu
    test_image = Image.new('RGB', (800, 600), color='red')
    
    # Test resize
    resized = resize_image(test_image, (640, 640))
    print(f"✅ Resized: {resized.size}")
    
    # Test preprocess pipeline
    processed = preprocess_for_detection(test_image, enhance=True)
    print(f"✅ Processed: {processed.size}")
    
    # Test validation
    is_valid, msg = validate_image(test_image)
    print(f"✅ Validation: {is_valid} - {msg}")