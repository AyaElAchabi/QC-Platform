"""
Storage service wrapper (MinIO)
"""
from core.minio_client import minio_client
from core.config import settings


class StorageService:
    """
    High-level storage operations
    """
    
    @staticmethod
    def upload_image(project_id: str, file_hash: str, content: bytes, format: str) -> str:
        """
        Upload image to MinIO
        
        Returns:
            storage_path
        """
        import io
        storage_path = f"raw-images/{project_id}/{file_hash}.{format}"
        
        minio_client.upload_file(
            bucket=settings.MINIO_BUCKET,
            object_name=storage_path,
            data=io.BytesIO(content),
            content_type=f"image/{format}"
        )
        
        return storage_path
    
    @staticmethod
    def upload_thumbnail(project_id: str, file_hash: str, content: bytes) -> str:
        """
        Upload thumbnail to MinIO
        
        Returns:
            thumbnail_path
        """
        import io
        thumbnail_path = f"thumbnails/{project_id}/{file_hash}_thumb.jpg"
        
        minio_client.upload_file(
            bucket=settings.MINIO_BUCKET,
            object_name=thumbnail_path,
            data=io.BytesIO(content),
            content_type="image/jpeg"
        )
        
        return thumbnail_path
    
    @staticmethod
    def get_image(storage_path: str) -> bytes:
        """
        Download image from MinIO
        """
        return minio_client.get_file(bucket=settings.MINIO_BUCKET, object_name=storage_path)
    
    @staticmethod
    def delete_image(storage_path: str):
        """
        Delete image from MinIO
        """
        minio_client.delete_file(bucket=settings.MINIO_BUCKET, object_name=storage_path)
    
    @staticmethod
    def get_presigned_url(storage_path: str, expires_seconds: int = 3600) -> str:
        """
        Generate temporary URL for image
        """
        return minio_client.get_presigned_url(
            bucket=settings.MINIO_BUCKET,
            object_name=storage_path,
            expires_seconds=expires_seconds
        )