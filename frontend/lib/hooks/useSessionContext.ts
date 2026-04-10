"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { AssistantContext, ChatTurn } from "@/lib/types";

interface SessionState {
  // Detection context
  predictionsMode: "none" | "dish" | "ingredients";
  currentContext: AssistantContext;

  // Chat
  chatHistory: ChatTurn[];

  // Recipe history
  recipeHistory: Array<{ name: string; timestamp: number }>;

  // Feedback
  recipeFeedback: Record<string, number>; // recipe_name -> rating (1 or -1)
  chatFeedback: Record<number, boolean>; // turn_index -> helpful

  // Location
  userLat: number;
  userLon: number;
  userCity: string;
  locationEnabled: boolean;
  autoDetectLocation: boolean;

  // Settings
  confidenceThreshold: number;
  useOllama: boolean;
  defaultImageSource: "upload" | "camera";
  resultsPerPage: number;

  // Actions
  setDishContext: (ctx: AssistantContext) => void;
  setIngredientContext: (ctx: AssistantContext) => void;
  setCurrentContext: (ctx: AssistantContext) => void;
  appendChatTurn: (turn: ChatTurn) => void;
  clearChat: () => void;
  addRecipeToHistory: (recipeName: string) => void;
  clearRecipeHistory: () => void;
  rateRecipe: (name: string, score: number) => void;
  rateChatTurn: (turnIndex: number, helpful: boolean) => void;
  setLocation: (lat: number, lon: number, city?: string) => void;
  setThreshold: (t: number) => void;
  setUseOllama: (v: boolean) => void;
  setAutoDetectLocation: (v: boolean) => void;
  setDefaultImageSource: (v: "upload" | "camera") => void;
  setResultsPerPage: (v: number) => void;
  clearCache: () => void;
}

const defaultState = {
  predictionsMode: "none" as const,
  currentContext: {},
  chatHistory: [] as ChatTurn[],
  recipeHistory: [] as Array<{ name: string; timestamp: number }>,
  recipeFeedback: {} as Record<string, number>,
  chatFeedback: {} as Record<number, boolean>,
  userLat: 51.5074,
  userLon: -0.1278,
  userCity: "",
  locationEnabled: false,
  autoDetectLocation: true,
  confidenceThreshold: 0.5,
  useOllama: false,
  defaultImageSource: "upload" as const,
  resultsPerPage: 5,
};

export const useSessionContext = create<SessionState, [["zustand/persist", unknown]]>(
  persist(
    (set) => ({
      ...defaultState,

      setDishContext: (ctx) =>
        set({ currentContext: ctx, predictionsMode: "dish" }),

      setIngredientContext: (ctx) =>
        set({ currentContext: ctx, predictionsMode: "ingredients" }),

      setCurrentContext: (ctx) =>
        set({ currentContext: ctx }),

      appendChatTurn: (turn) =>
        set((s) => ({ chatHistory: [...s.chatHistory, turn] })),

      clearChat: () => set({ chatHistory: [] }),

      addRecipeToHistory: (recipeName: string) =>
        set((s) => {
          const filtered = s.recipeHistory.filter((r) => r.name !== recipeName);
          return { recipeHistory: [{ name: recipeName, timestamp: Date.now() }, ...filtered].slice(0, 20) };
        }),

      clearRecipeHistory: () => set({ recipeHistory: [] }),

      rateRecipe: (name, score) =>
        set((s) => ({ recipeFeedback: { ...s.recipeFeedback, [name]: score } })),

      rateChatTurn: (turnIndex, helpful) =>
        set((s) => ({ chatFeedback: { ...s.chatFeedback, [turnIndex]: helpful } })),

      setLocation: (lat, lon, city = "") =>
        set({ userLat: lat, userLon: lon, userCity: city, locationEnabled: true }),

      setThreshold: (t) => set({ confidenceThreshold: t }),

      setUseOllama: (v) => set({ useOllama: v }),

      setAutoDetectLocation: (v) => set({ autoDetectLocation: v }),

      setDefaultImageSource: (v) => set({ defaultImageSource: v }),

      setResultsPerPage: (v) => set({ resultsPerPage: v }),

      clearCache: () => set({
        currentContext: {},
        chatHistory: [],
        predictionsMode: "none",
        recipeHistory: []
      }),
    }),
    {
      name: "smartkitchen-session",
      storage: createJSONStorage(() => {
        // Only use localStorage on client side
        if (typeof window === "undefined") {
          return {
            getItem: () => null,
            setItem: () => {},
            removeItem: () => {},
          };
        }
        return localStorage;
      }),
      merge: (persistedState, currentState) => ({
        ...currentState,
        ...(persistedState as Partial<SessionState>),
        // Always reset chat history on load
        chatHistory: [],
      }),
    }
  )
);
