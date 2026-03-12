interface Props {
  name: string;
  variant: "matched" | "missing" | "detected";
  confidence?: number;
}

const variantStyles = {
  matched: "bg-green-100 text-green-800 border-green-200",
  missing: "bg-red-100 text-red-800 border-red-200",
  detected: "bg-blue-100 text-blue-800 border-blue-200",
};

export default function IngredientBadge({ name, variant, confidence }: Props) {
  return (
    <span
      className={[
        "inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full border",
        variantStyles[variant],
      ].join(" ")}
    >
      {name}
      {confidence != null && (
        <span className="opacity-60">({Math.round(confidence * 100)}%)</span>
      )}
    </span>
  );
}
