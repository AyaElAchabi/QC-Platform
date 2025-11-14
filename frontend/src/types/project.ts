export interface Project {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  task_type: string;
  status: string;
  classes?: Array<{
    name: string;
    color: string;
  }>;
  total_images: number;
  annotated_images: number;
  models_count?: number;
  created_at: string;
  updated_at?: string;
}
