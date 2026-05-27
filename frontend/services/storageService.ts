const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? '';
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? '';

export async function uploadFileToStorage(
  file: File,
  bucket: string,
  path: string,
): Promise<string> {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error(
      'Supabase Storage no está configurado: faltan NEXT_PUBLIC_SUPABASE_URL o NEXT_PUBLIC_SUPABASE_ANON_KEY',
    );
  }

  const uniquePath = `${crypto.randomUUID()}-${path}`;
  const encoded = encodeURIComponent(uniquePath);
  const uploadUrl = `${SUPABASE_URL}/storage/v1/object/${bucket}/${encoded}`;

  const response = await fetch(uploadUrl, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      'Content-Type': file.type || 'application/octet-stream',
      'x-upsert': 'false',
    },
    body: file,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Upload a Storage falló (${response.status}): ${body}`);
  }

  return `${SUPABASE_URL}/storage/v1/object/public/${bucket}/${encoded}`;
}
