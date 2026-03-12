interface Props {
  label?: string;
}

export default function LoadingSpinner({ label }: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-10">
      <div
        className="w-10 h-10 rounded-full border-4 border-gray-200 animate-spin"
        style={{ borderTopColor: "#FF6B35" }}
      />
      {label && <p className="text-sm text-gray-500">{label}</p>}
    </div>
  );
}
