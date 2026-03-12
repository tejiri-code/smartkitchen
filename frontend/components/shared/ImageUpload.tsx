"use client";

import { useRef, useState } from "react";

interface Props {
  onFile: (file: File) => void;
  label?: string;
  accept?: string;
}

export default function ImageUpload({
  onFile,
  label = "Upload an image",
  accept = "image/*",
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  function handleFile(file: File) {
    onFile(file);
    const url = URL.createObjectURL(file);
    setPreview(url);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  return (
    <div className="space-y-3">
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={[
          "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors",
          dragging
            ? "border-orange-400 bg-orange-50"
            : "border-gray-200 hover:border-orange-300 hover:bg-gray-50",
        ].join(" ")}
      >
        <div className="flex justify-center mb-3">
          <svg className="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
          </svg>
        </div>
        <p className="text-sm font-medium text-gray-700">{label}</p>
        <p className="text-xs text-gray-400 mt-1">Click to browse or drag & drop</p>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="hidden"
        />
      </div>

      {preview && (
        <div className="relative rounded-xl overflow-hidden border border-gray-200">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={preview}
            alt="Preview"
            className="w-full max-h-72 object-cover"
          />
          <button
            onClick={() => { setPreview(null); if (inputRef.current) inputRef.current.value = ""; }}
            className="absolute top-2 right-2 bg-white/90 text-gray-600 rounded-full w-7 h-7 flex items-center justify-center text-xs hover:bg-white shadow-sm cursor-pointer border border-gray-200"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
