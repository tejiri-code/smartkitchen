"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { askAssistant } from "@/lib/api/assistant";
import type { ChatTurn } from "@/lib/types";
import ErrorMessage from "@/components/shared/ErrorMessage";
import { MessageSquare, Send, RotateCcw, Sparkles, Loader2, Zap, Wifi } from "lucide-react";

const EXAMPLE_QUESTIONS = [
  "What ingredients do I need?",
  "How long does this take?",
  "What can I substitute if I'm missing something?",
  "Can I make this vegetarian?",
  "Where can I buy this nearby?",
  "Give me step-by-step instructions.",
];

export default function AssistantPage() {
  const { currentContext, predictionsMode, chatHistory, useOllama, appendChatTurn, clearChat, setUseOllama } =
    useSessionContext();

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [image, setImage] = useState<string | null>(null);
  const [showOllamaInfo, setShowOllamaInfo] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  async function sendQuestion(question: string) {
    if (!question.trim() && !image) return;
    if (loading) return;
    
    const currentImage = image;
    setInput("");
    setImage(null);
    setError(null);
    setLoading(true);
    
    try {
      const res = await askAssistant({
        question: question || "What is in this image?",
        context: currentContext,
        history: chatHistory.slice(-3),
        use_ollama: useOllama,
        image: currentImage || undefined,
      });
      appendChatTurn({ question: question || "Sent an image", answer: res.answer });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to get an answer.");
      // Restore state on error if user might want to retry
      setImage(currentImage);
      setInput(question);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-8 flex flex-col h-[calc(100vh-7rem)] lg:h-[calc(100vh-1rem)]">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-md"
               style={{ background: "linear-gradient(135deg, #6366F1, #8B5CF6)" }}>
            <MessageSquare size={20} strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">AI Assistant</h1>
            <p className="text-sm text-gray-500">Ask anything about cooking, recipes, or ingredients.</p>
          </div>
        </div>

        {/* Ollama Toggle */}
        <motion.div
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          className="relative"
          onMouseEnter={() => setShowOllamaInfo(true)}
          onMouseLeave={() => setShowOllamaInfo(false)}
        >
          <button
            onClick={() => setUseOllama(!useOllama)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
              useOllama
                ? "bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-200"
                : "bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200"
            }`}
          >
            {useOllama ? (
              <>
                <Zap size={14} />
                Qwen Enabled
              </>
            ) : (
              <>
                <Wifi size={14} />
                Use Qwen
              </>
            )}
          </button>

          {/* Hover info */}
          {showOllamaInfo && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="absolute top-12 right-0 bg-white border border-gray-200 rounded-lg shadow-lg p-3 w-56 z-50"
            >
              <p className="text-xs font-medium text-gray-900 mb-1">
                {useOllama ? "✓ Using Local AI (Qwen)" : "Using Template Responses"}
              </p>
              <p className="text-xs text-gray-600 leading-relaxed">
                {useOllama
                  ? "Requires Ollama running. Provides smarter, context-aware answers."
                  : "No Ollama needed. Uses template-based responses."}
              </p>
            </motion.div>
          )}
        </motion.div>
      </div>

      {/* Context hint */}
      {predictionsMode === "none" && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-4 bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 flex items-start gap-2">
          <Sparkles size={16} className="text-blue-500 mt-0.5 shrink-0" />
          <p className="text-xs text-blue-700">Scan a dish or ingredients first for smarter, grounded answers!</p>
        </motion.div>
      )}

      {/* Context badge */}
      {predictionsMode !== "none" && currentContext.detected_dish && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-4 bg-white border border-gray-100 rounded-xl px-4 py-2 flex items-center justify-between shadow-sm">
          <div>
            <p className="text-xs font-medium text-gray-500">Current Context</p>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-sm font-semibold text-gray-900">{currentContext.detected_dish}</span>
              {currentContext.detected_ingredients && currentContext.detected_ingredients.length > 0 && (
                <span className="text-xs text-gray-400">+ {currentContext.detected_ingredients.length} ingredients</span>
              )}
            </div>
          </div>
          <button onClick={clearChat} className="text-xs text-gray-400 hover:text-gray-600 cursor-pointer">Clear</button>
        </motion.div>
      )}

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto mb-4 pr-2 space-y-4">
        {/* Empty state with suggestions */}
        {chatHistory.length === 0 && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex flex-col items-center justify-center h-full gap-6">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg"
                 style={{ background: "linear-gradient(135deg, #6366F1, #8B5CF6)" }}>
              <MessageSquare size={32} className="text-white" />
            </div>
            <div className="text-center">
              <h2 className="text-lg font-bold text-gray-900 mb-1">Start a conversation</h2>
              <p className="text-sm text-gray-500">Ask me anything about cooking!</p>
            </div>

            <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-2">
              {EXAMPLE_QUESTIONS.map((q) => (
                <motion.button
                  key={q}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.02 }}
                  onClick={() => sendQuestion(q)}
                  className="text-xs px-3 py-2.5 rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-all text-left font-medium cursor-pointer"
                >
                  {q}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Messages */}
        {chatHistory.map((turn: ChatTurn, i: number) => (
          <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="space-y-2">
            {/* User message */}
            <div className="flex justify-end">
              <div className="max-w-xs px-4 py-3 rounded-2xl rounded-tr-none text-sm text-white leading-relaxed"
                   style={{ background: "linear-gradient(135deg, #6366F1, #8B5CF6)" }}>
                {turn.question}
              </div>
            </div>
            {/* Assistant message */}
            <div className="flex justify-start">
              <div className="max-w-xs px-4 py-3 rounded-2xl rounded-tl-none text-sm bg-white border border-gray-100 text-gray-800 leading-relaxed shadow-sm">
                {turn.answer}
              </div>
            </div>
          </motion.div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
            <div className="px-4 py-3 bg-white border border-gray-100 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
              <Loader2 size={16} className="text-gray-400 animate-spin" />
              <p className="text-sm text-gray-500">Thinking…</p>
            </div>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Image Preview */}
      {image && (
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="relative w-20 h-20 mb-4 rounded-xl overflow-hidden border-2 border-indigo-500 shadow-lg">
          <img src={image} alt="Upload preview" className="w-full h-full object-cover" />
          <button 
            onClick={() => setImage(null)}
            className="absolute top-1 right-1 bg-white/80 rounded-full p-0.5 text-gray-700 hover:text-red-500 transition-colors"
          >
            <RotateCcw size={14} className="rotate-45" />
          </button>
        </motion.div>
      )}

      {/* Input bar */}
      <div className="flex gap-2 pt-4 border-t border-gray-100">
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={handleImageUpload}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center justify-center p-3 rounded-xl border border-gray-200 bg-white text-gray-500 hover:bg-gray-50 hover:text-indigo-600 transition-colors cursor-pointer"
          disabled={loading}
        >
          <Sparkles size={20} />
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendQuestion(input)}
          placeholder={image ? "Ask about this image..." : "Ask a question..."}
          className="flex-1 bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-200 transition-all"
          disabled={loading}
        />
        <button
          onClick={() => sendQuestion(input)}
          disabled={loading || (!input.trim() && !image)}
          className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold text-white disabled:opacity-40 cursor-pointer transition-all hover:shadow-lg"
          style={{ background: "linear-gradient(135deg, #6366F1, #8B5CF6)", pointerEvents: loading || (!input.trim() && !image) ? "none" : "auto" }}
        >
          <Send size={16} />
        </button>
        {chatHistory.length > 0 && (
          <button onClick={clearChat} className="flex items-center gap-1.5 px-3 py-2.5 rounded-xl text-sm text-gray-500 border border-gray-200 bg-white hover:bg-gray-50 transition-colors cursor-pointer">
            <RotateCcw size={14} />
          </button>
        )}
      </div>
    </div>
  );
}
