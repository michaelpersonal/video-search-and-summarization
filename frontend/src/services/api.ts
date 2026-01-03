import axios from 'axios';
import { SparePart, ImageUploadResponse, HealthCheck } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health check
  async getHealth(): Promise<HealthCheck> {
    const response = await api.get('/health');
    return response.data;
  },

  // Upload image and get matches
  async uploadImage(file: File): Promise<ImageUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all spare parts
  async getSpareParts(skip = 0, limit = 100): Promise<SparePart[]> {
    const response = await api.get(`/spare-parts?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Get specific spare part
  async getSparePart(materialNumber: string): Promise<SparePart> {
    const response = await api.get(`/spare-parts/${materialNumber}`);
    return response.data;
  },

  // Create new spare part
  async createSparePart(sparePart: Omit<SparePart, 'id' | 'created_at'>): Promise<SparePart> {
    const response = await api.post('/spare-parts', sparePart);
    return response.data;
  },

  // Search spare parts
  async searchSpareParts(query: string): Promise<SparePart[]> {
    const response = await api.get(`/search?query=${encodeURIComponent(query)}`);
    return response.data;
  },
};

export default apiService; 