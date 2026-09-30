import axios from 'axios';

export interface AnalysisResult {
  id: string;
  session_id: string;
  shot_type: string;
  confidence: number;
  status: string;
  processing_time: number;
  overlay_video_url: string;
  features: Array<{ feature_name: string; value: number; unit: string }>;
  feedbacks: Array<{ category: string; severity: string; message: string; confidence: number }>;
}

const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    // Client-side browser execution uses same-origin relative rewrite path
    return '/api';
  }
  // Server-side / Service binding execution
  if (process.env.BACKEND_SERVICE_URL) {
    const baseUrl = process.env.BACKEND_SERVICE_URL.replace(/\/$/, '');
    return baseUrl.endsWith('/api') ? baseUrl : `${baseUrl}/api`;
  }
  if (process.env.NEXT_PUBLIC_API_URL) {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '');
    return baseUrl.endsWith('/api') ? baseUrl : `${baseUrl}/api`;
  }
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

export const uploadVideo = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE_URL}/videos/upload`, formData);
  return response.data;
};

export const startAnalysis = async (videoId: string, shotHint?: string) => {
  const response = await axios.post(`${API_BASE_URL}/analysis/start`, {
    video_id: videoId,
    shot_type_hint: shotHint || null,
  });
  return response.data as AnalysisResult;
};

export const getAthleteHistory = async (athleteId: string) => {
  const response = await axios.get(`${API_BASE_URL}/athletes/${athleteId}/history`);
  return response.data;
};
