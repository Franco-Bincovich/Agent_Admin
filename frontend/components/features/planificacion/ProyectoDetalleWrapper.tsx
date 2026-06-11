'use client';

import { usePlanificacion } from '@/hooks/usePlanificacion';
import ProyectoDetalleClient from './ProyectoDetalleClient';

interface Props { proyectoId: string }

export default function ProyectoDetalleWrapper({ proyectoId }: Props) {
  const { proyectos } = usePlanificacion();
  return <ProyectoDetalleClient proyectoId={proyectoId} proyectos={proyectos} />;
}
