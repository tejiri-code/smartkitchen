interface Props {
  value: number; // 0-1
  label?: string;
}

export default function ConfidenceMeter({ value, label }: Props) {
  const pct = Math.round(value * 100);
  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{label}</span>
          <span>{pct}%</span>
        </div>
      )}
      <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, backgroundColor: "#FF6B35" }}
        />
      </div>
    </div>
  );
}
