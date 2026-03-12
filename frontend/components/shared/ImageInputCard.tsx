"use client";

import { useRef, useState } from "react";
import { Upload, Camera, X } from "lucide-react";
import dynamic from "next/dynamic";

const CameraCapture = dynamic(() => import("./CameraCapture"), { ssr: false });

interface Props {
  onFile: (file: File) => void;
  label?: string;
  hint?: string;
}

type Tab = "upload" | "camera";

export default function ImageInputCard({
  onFile,
  label = "Upload an image",
  hint = "Drag & drop or click to browse",
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [tab, setTab] = useState<Tab>("upload");
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  function handleFile(file: File) {
    onFile(file);
    setPreview(URL.createObjectURL(file));
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f && f.type.startsWith("image/")) handleFile(f);
  }

  function reset() {
    setPreview(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  if (preview) {
    return (
      <div className="relative rounded-2xl overflow-hidden border border-gray-200 shadow-sm bg-white">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={preview} alt="Preview" className="w-full max-h-80 object-cover" />
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent px-4 py-3 flex items-end justify-between">
          <p className="text-xs text-white/80">Image ready for analysis</p>
          <button
            onClick={reset}
            className="flex items-center gap-1.5 text-xs text-white bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg backdrop-blur-sm transition-colors cursor-pointer"
          >
            <X size={12} /> Replace
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      {/* Tabs */}
      <div className="flex border-b border-gray-100">
        {(["upload", "camera"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={[
              "flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors cursor-pointer",
              tab === t
                ? "text-orange-600 border-b-2 border-orange-500 bg-orange-50/50"
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-50",
            ].join(" ")}
          >
            {t === "upload" ? <Upload size={15} /> : <Camera size={15} />}
            {t === "upload" ? "Upload" : "Take Photo"}
          </button>
        ))}
      </div>

      {/* Upload tab */}
      {tab === "upload" && (
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={[
            "flex flex-col items-center justify-center gap-3 p-12 cursor-pointer transition-colors",
            dragging ? "bg-orange-50" : "hover:bg-gray-50",
          ].join(" ")}
        >
          <div className={[
            "w-14 h-14 rounded-2xl flex items-center justify-center transition-colors",
            dragging ? "bg-orange-100 text-orange-500" : "bg-gray-100 text-gray-400",
          ].join(" ")}>
            <Upload size={24} strokeWidth={1.5} />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-700">{label}</p>
            <p className="text-xs text-gray-400 mt-0.5">{hint}</p>
            <p className="text-xs text-gray-300 mt-1">JPG, PNG, WebP up to 10MB</p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="hidden"
          />
        </div>
      )}

      {/* Camera tab */}
      {tab === "camera" && (
        <div className="p-2">
          <CameraCapture
            onCapture={(file) => { handleFile(file); setTab("upload"); }}
            onCancel={() => setTab("upload")}
          />
        </div>
      )}
    </div>
  );
}
