import { get, patch, post, del } from '@/services/api';
import type { Proyecto, ProyectoDetalleResponse, AreaResponse, TareaResponse, ApiError } from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export async function getProyectos(): Promise<Proyecto[]> {
  return get<Proyecto[]>('/api/v1/planificacion');
}

export async function getProyecto(id: string): Promise<Proyecto> {
  return get<Proyecto>(`/api/v1/planificacion/${id}`);
}

export async function getProyectoDetalle(id: string): Promise<ProyectoDetalleResponse> {
  return get<ProyectoDetalleResponse>(`/api/v1/planificacion/${id}/detalle`);
}

export async function updateArea(
  proyectoId: string,
  areaId: string,
  campos: Partial<AreaResponse>,
): Promise<AreaResponse> {
  return patch<AreaResponse>(`/api/v1/planificacion/${proyectoId}/areas/${areaId}`, campos);
}

export async function marcarTarea(
  proyectoId: string,
  tareaId: string,
  completada: boolean,
): Promise<TareaResponse> {
  return patch<TareaResponse>(
    `/api/v1/planificacion/${proyectoId}/tareas/${tareaId}`,
    { completada },
  );
}

export async function createProyecto(formData: FormData): Promise<Proyecto> {
  const response = await fetch(`${BASE_URL}/api/v1/planificacion`, {
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

  return response.json() as Promise<Proyecto>;
}

export async function deleteProyecto(id: string): Promise<void> {
  return del<void>(`/api/v1/planificacion/${id}`);
}

export async function createArea(
  proyectoId: string,
  nombre: string,
  capWbs: string | null,
): Promise<AreaResponse> {
  return post<AreaResponse>(
    `/api/v1/planificacion/${proyectoId}/areas`,
    { nombre, cap_wbs: capWbs },
  );
}

export async function actualizarProgreso(
  proyectoId: string,
  tareaId: string,
  progreso: number,
): Promise<TareaResponse> {
  return patch<TareaResponse>(
    `/api/v1/planificacion/${proyectoId}/tareas/${tareaId}/progreso`,
    { progreso },
  );
}

export async function reprogramarTarea(
  proyectoId: string,
  tareaId: string,
  fechaInicio: string,
  fechaFin: string,
): Promise<TareaResponse> {
  return patch<TareaResponse>(
    `/api/v1/planificacion/${proyectoId}/tareas/${tareaId}/reprogramar`,
    { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
  );
}

export async function asignarArea(
  proyectoId: string,
  tareaId: string,
  areaId: string | null,
): Promise<TareaResponse> {
  return patch<TareaResponse>(
    `/api/v1/planificacion/${proyectoId}/tareas/${tareaId}/area`,
    { area_id: areaId },
  );
}
