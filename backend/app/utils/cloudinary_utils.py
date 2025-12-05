import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from typing import Optional, Dict
from io import BytesIO
from PIL import Image
import base64

from app.core.config import settings

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

class CloudinaryService:
    """Service để upload và quản lý ảnh trên Cloudinary"""
    
    @staticmethod
    def upload_image(
        image_file,
        folder: str = None,
        public_id: str = None,
        tags: list = None
    ) -> Dict[str, str]:
        """
        Upload ảnh lên Cloudinary
        
        Args:
            image_file: File ảnh (bytes, BytesIO, hoặc PIL Image)
            folder: Folder trên Cloudinary (mặc định lấy từ config)
            public_id: Tên file tùy chỉnh (nếu không có sẽ tự động)
            tags: Tags để phân loại ảnh
            
        Returns:
            Dict chứa URL và public_id
        """
        try:
            upload_params = {
                "folder": folder or settings.CLOUDINARY_FOLDER,
                "resource_type": "image",
                "overwrite": False,
                "invalidate": True,
            }
            
            if public_id:
                upload_params["public_id"] = public_id
            
            if tags:
                upload_params["tags"] = tags
            
            # Upload
            result = cloudinary.uploader.upload(image_file, **upload_params)
            
            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "format": result.get("format"),
                "width": result.get("width"),
                "height": result.get("height"),
                "bytes": result.get("bytes"),
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def upload_pil_image(
        pil_image: Image.Image,
        folder: str = None,
        public_id: str = None,
        tags: list = None,
        format: str = "JPEG"
    ) -> Dict[str, str]:
        """
        Upload ảnh PIL Image lên Cloudinary
        
        Args:
            pil_image: PIL Image object
            folder: Folder trên Cloudinary
            public_id: Tên file
            tags: Tags
            format: Format ảnh (JPEG, PNG, WEBP)
        """
        try:
            # Convert PIL Image to BytesIO
            buffer = BytesIO()
            pil_image.save(buffer, format=format)
            buffer.seek(0)
            
            return CloudinaryService.upload_image(
                buffer,
                folder=folder,
                public_id=public_id,
                tags=tags
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def upload_base64_image(
        base64_string: str,
        folder: str = None,
        public_id: str = None,
        tags: list = None
    ) -> Dict[str, str]:
        """
        Upload ảnh từ base64 string
        
        Args:
            base64_string: Base64 encoded image
            folder: Folder trên Cloudinary
            public_id: Tên file
            tags: Tags
        """
        try:
            # Decode base64
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
            
            image_data = base64.b64decode(base64_string)
            
            return CloudinaryService.upload_image(
                image_data,
                folder=folder,
                public_id=public_id,
                tags=tags
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def delete_image(public_id: str) -> Dict[str, bool]:
        """
        Xóa ảnh trên Cloudinary
        
        Args:
            public_id: Public ID của ảnh
            
        Returns:
            Dict với status success/failure
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return {
                "success": result.get("result") == "ok",
                "message": result.get("result")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_optimized_url(
        public_id: str,
        width: int = None,
        height: int = None,
        crop: str = "fill",
        quality: str = "auto",
        format: str = "auto"
    ) -> str:
        """
        Lấy URL ảnh đã tối ưu
        
        Args:
            public_id: Public ID của ảnh
            width: Chiều rộng
            height: Chiều cao
            crop: Chế độ crop (fill, fit, scale, etc.)
            quality: Chất lượng (auto, best, good, etc.)
            format: Format (auto, jpg, png, webp)
            
        Returns:
            Optimized URL
        """
        try:
            transformation = {
                "quality": quality,
                "fetch_format": format
            }
            
            if width:
                transformation["width"] = width
            if height:
                transformation["height"] = height
            if width or height:
                transformation["crop"] = crop
            
            url, _ = cloudinary_url(
                public_id,
                **transformation,
                secure=True
            )
            
            return url
            
        except Exception as e:
            return None
    
    @staticmethod
    def get_thumbnail_url(public_id: str, size: int = 300) -> str:
        """
        Lấy URL thumbnail
        
        Args:
            public_id: Public ID của ảnh
            size: Kích thước thumbnail (default 300px)
            
        Returns:
            Thumbnail URL
        """
        return CloudinaryService.get_optimized_url(
            public_id,
            width=size,
            height=size,
            crop="fill"
        )


# Singleton instance
cloudinary_service = CloudinaryService()