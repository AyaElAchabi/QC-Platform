export interface Image {
  id: string;
  project_id: string;
  filename: string;
  storage_path?: string;
  file_hash?: string;
  width: number;
  height: number;
  status: "uploaded" | "annotated" | "processing";
  annotation_count: number;
  created_at: string;
  thumbnail_url?: string;
}

export interface UploadProgress {
  filename: string;
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
}
