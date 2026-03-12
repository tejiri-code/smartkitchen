"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { Camera, RotateCcw, Check, X, AlertCircle } from "lucide-react";

interface Props {
  onCapture: (file: File) => void;
  onCancel: () => void;
}

export default function CameraCapture({ onCapture, onCancel }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [phase, setPhase] = useState<"loading" | "live" | "captured" | "error">("loading");
  const [captured, setCaptured] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const startCamera = useCallback(async () => {
    setPhase("loading");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => setPhase("live");
      }
    } catch {
      setErrorMsg("Camera access denied. Please allow camera permission in your browser settings.");
      setPhase("error");
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, [startCamera, stopCamera]);

  function capturePhoto() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d")?.drawImage(video, 0, 0);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.92);
    setCaptured(dataUrl);
    setPhase("captured");
    stopCamera();
  }

  function retake() {
    setCaptured(null);
    startCamera();
  }

  function confirm() {
    if (!canvasRef.current) return;
    canvasRef.current.toBlob(
      (blob) => {
        if (blob) {
          const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
          onCapture(file);
        }
      },
      "image/jpeg",
      0.92,
    );
  }

  return (
    <div className="rounded-2xl overflow-hidden border border-gray-200 bg-gray-900 relative">
      <canvas ref={canvasRef} className="hidden" />

      {/* Video / Preview */}
      <div className="relative aspect-video w-full bg-gray-900">
        {phase === "loading" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-orange-400 border-t-transparent animate-spin" />
            <p className="text-gray-400 text-sm">Starting camera…</p>
          </div>
        )}

        {phase === "error" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 px-6 text-center">
            <AlertCircle size={32} className="text-red-400" />
            <p className="text-gray-300 text-sm">{errorMsg}</p>
            <button
              onClick={startCamera}
              className="px-4 py-2 rounded-lg text-sm font-medium text-white cursor-pointer"
              style={{ backgroundColor: "#FF7A18" }}
            >
              Try again
            </button>
          </div>
        )}

        {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className={["w-full h-full object-cover transition-opacity", phase === "live" ? "opacity-100" : "opacity-0"].join(" ")}
        />

        {captured && phase === "captured" && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={captured} alt="Captured" className="absolute inset-0 w-full h-full object-cover" />
        )}

        {/* Viewfinder overlay */}
        {phase === "live" && (
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-6 border border-white/20 rounded-xl" />
            <div className="absolute top-6 left-6 w-6 h-6 border-t-2 border-l-2 border-white/60 rounded-tl-lg" />
            <div className="absolute top-6 right-6 w-6 h-6 border-t-2 border-r-2 border-white/60 rounded-tr-lg" />
            <div className="absolute bottom-6 left-6 w-6 h-6 border-b-2 border-l-2 border-white/60 rounded-bl-lg" />
            <div className="absolute bottom-6 right-6 w-6 h-6 border-b-2 border-r-2 border-white/60 rounded-br-lg" />
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4 px-4 py-4 bg-gray-900">
        <button
          onClick={onCancel}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white/10 text-white hover:bg-white/20 transition-colors cursor-pointer"
        >
          <X size={18} />
        </button>

        {phase === "live" && (
          <button
            onClick={capturePhoto}
            className="flex items-center justify-center w-16 h-16 rounded-full border-4 border-white cursor-pointer hover:scale-105 transition-transform"
            style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}
          >
            <Camera size={24} className="text-white" />
          </button>
        )}

        {phase === "captured" && (
          <>
            <button
              onClick={retake}
              className="flex items-center justify-center w-12 h-12 rounded-full bg-white/10 text-white hover:bg-white/20 transition-colors cursor-pointer"
            >
              <RotateCcw size={20} />
            </button>
            <button
              onClick={confirm}
              className="flex items-center justify-center w-16 h-16 rounded-full cursor-pointer hover:scale-105 transition-transform"
              style={{ background: "linear-gradient(135deg, #34A853, #4CAF6A)" }}
            >
              <Check size={24} className="text-white" />
            </button>
          </>
        )}

        {phase === "loading" && (
          <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center">
            <Camera size={24} className="text-white/40" />
          </div>
        )}
      </div>
    </div>
  );
}
