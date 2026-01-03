export interface SparePart {
  id: number;
  material_number: string;
  description: string;
  category?: string;
  manufacturer?: string;
  specifications?: string;
  image_path?: string;
  created_at: string;
}

export interface SearchResult {
  spare_part: SparePart;
  confidence_score: number;
  match_reason: string;
}

export interface ImageUploadResponse {
  message: string;
  search_results: SearchResult[];
}

export interface HealthCheck {
  status: string;
  ai_model_available: boolean;
  timestamp: string;
} 