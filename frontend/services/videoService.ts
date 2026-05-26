import { get } from '@/services/api';
import type { VideoJob, ApiError } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export async function createVideoJob(formData: FormData): Promise<VideoJob> {
  const response = await fetch(`${BASE_URL}/api/v1/video/jobs`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });

  if (response.status === 401) {
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    throw (await response.json()) as ApiError;
  }

  if (!response.ok) {
    throw (await response.json()) as ApiError;
  }

  return response.json() as Promise<VideoJob>;
}

export async function getVideoJob(jobId: string): Promise<VideoJob> {
  return get<VideoJob>(`/api/v1/video/jobs/${jobId}`);
}

export async function listVideoJobs(): Promise<VideoJob[]> {
  return get<VideoJob[]>('/api/v1/video/jobs');
}
