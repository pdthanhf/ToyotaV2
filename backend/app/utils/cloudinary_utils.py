import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
from typing import Optional, Dict, List, Union
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
        """Upload ảnh PIL Image lên Cloudinary"""
        try:
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
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def upload_base64_image(
        base64_string: str,
        folder: str = None,
        public_id: str = None,
        tags: list = None
    ) -> Dict[str, str]:
        """Upload ảnh từ base64 string"""
        try:
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
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def delete_image(public_id: str) -> Dict[str, bool]:
        """Xóa ảnh trên Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return {
                "success": result.get("result") == "ok",
                "message": result.get("result")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================
    #  ACTIVE LEARNING UTILS (MỚI THÊM)
    # ========================================================
    @staticmethod
    def add_tag_to_image(public_id: str, tag: str) -> bool:
        """
        Gắn thẻ (tag) cho ảnh trên Cloudinary.
        Dùng khi Admin duyệt ảnh để đánh dấu ảnh này thuộc dòng xe nào.
        """
        try:
            if not public_id or not tag:
                return False

            # Gắn tag (Cloudinary cho phép 1 ảnh có nhiều tag)
            cloudinary.uploader.add_tag(tag, [public_id])
            print(f" Cloudinary: Đã gắn tag '{tag}' cho ảnh '{public_id}'")
            return True
        except Exception as e:
            print(f" Cloudinary Error (add_tag): {e}")
            return False

    @staticmethod
    def remove_tag_from_image(public_id: str, tag: str) -> bool:
        """Gỡ tag khỏi ảnh"""
        try:
            cloudinary.uploader.remove_tag(tag, [public_id])
            return True
        except Exception as e:
            print(f" Cloudinary Error (remove_tag): {e}")
            return False

    # ========================================================
    #  URL OPTIMIZATION
    # ========================================================
    @staticmethod
    def get_optimized_url(
        public_id: str,
        width: int = None,
        height: int = None,
        crop: str = "fill",
        quality: str = "auto",
        format: str = "auto"
    ) -> str:
        """Lấy URL ảnh đã tối ưu"""
        try:
            transformation = {
                "quality": quality,
                "fetch_format": format
            }
            
            if width: transformation["width"] = width
            if height: transformation["height"] = height
            if width or height: transformation["crop"] = crop
            
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
        """Lấy URL thumbnail"""
        return CloudinaryService.get_optimized_url(
            public_id,
            width=size,
            height=size,
            crop="fill"
        )

# Singleton instance
cloudinary_service = CloudinaryService()