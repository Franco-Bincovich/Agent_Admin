import VideoForm from '@/components/features/video/VideoForm';

export default function VideoPage() {
  return (
    <div className="max-w-[800px] mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
          Editor de Video
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          Subí tu video y configurá la edición automática.
        </p>
      </div>

      <div
        className="rounded-lg border p-6"
        style={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)' }}
      >
        <VideoForm />
      </div>
    </div>
  );
}
