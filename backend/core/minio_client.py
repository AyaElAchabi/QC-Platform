"""
MinIO client for object storage
"""
from minio import Minio
from minio.error import S3Error
from typing import Optional, BinaryIO
import io

from core.config import settings


class MinioClient:
    """
    Wrapper around MinIO Python SDK
    """
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if not exists"""
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
                print(f"✅ Created MinIO bucket: {settings.MINIO_BUCKET}")
        except S3Error as e:
            print(f"❌ Error creating bucket: {e}")
    
    def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None
    ):
        """
        Upload file to MinIO
        
        Args:
            bucket: Bucket name
            object_name: Object path (e.g., "raw-images/proj-123/abc.jpg")
            data: File-like object (use io.BytesIO for in-memory)
            content_type: MIME type
            metadata: Optional metadata dict
        """
        try:
            # Get data length
            data.seek(0, 2)  # Seek to end
            length = data.tell()
            data.seek(0)  # Reset to start
            
            self.client.put_object(
                bucket,
                object_name,
                data,
                length,
                content_type=content_type,
                metadata=metadata or {}
            )
            return True
        except S3Error as e:
            print(f"❌ MinIO upload error: {e}")
            raise
    
    def get_file(self, bucket: str, object_name: str) -> bytes:
        """
        Download file from MinIO
        
        Returns file content as bytes
        """
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"❌ MinIO download error: {e}")
            raise
    
    def delete_file(self, bucket: str, object_name: str):
        """Delete file from MinIO"""
        try:
            self.client.remove_object(bucket, object_name)
        except S3Error as e:
            print(f"❌ MinIO delete error: {e}")
            raise
    
    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires_seconds: int = 3600
    ) -> str:
        """
        Generate presigned URL for temporary access
        
        Args:
            bucket: Bucket name
            object_name: Object path
            expires_seconds: URL expiration (default 1h)
        
        Returns:
            Presigned URL string
        """
        try:
            from datetime import timedelta
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(seconds=expires_seconds)
            )
            return url
        except S3Error as e:
            print(f"❌ MinIO presigned URL error: {e}")
            raise
    
    def list_objects(self, bucket: str, prefix: str = ""):
        """List objects in bucket with optional prefix"""
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"❌ MinIO list error: {e}")
            raise


# Global instance
minio_client = MinioClient()