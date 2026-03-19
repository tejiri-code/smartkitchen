'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart } from '@/components/presentation/BarChart';
import { LineChart } from '@/components/presentation/LineChart';
import { RadarChart } from '@/components/presentation/RadarChart';
import { ArchitectureDiagram } from '@/components/presentation/ArchitectureDiagram';
import { PipelineFlow } from '@/components/presentation/PipelineFlow';
import { ChefHat, Zap, Brain, Cpu, BarChart3, Lightbulb } from 'lucide-react';

const tabs = [
  { id: 'architecture', label: 'Architecture', icon: Cpu },
  { id: 'pipeline', label: 'Deep Learning', icon: Brain },
  { id: 'metrics', label: 'Performance', icon: BarChart3 },
  { id: 'features', label: 'Features', icon: Zap },
  { id: 'vlm', label: 'VLM Deep Dive', icon: Lightbulb },
  { id: 'demo', label: 'Features Showcase', icon: ChefHat },
];

export default function PresentationPage() {
  const [activeTab, setActiveTab] = useState('architecture');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3 mb-4">
            <ChefHat size={32} className="text-[#FF7A18]" />
            <h1 className="text-3xl font-bold text-gray-900">SmartKitchen</h1>
            <span className="text-gray-500 font-medium">Presentation</span>
          </div>
          <p className="text-gray-600">Interactive charts and diagrams for presenting the SmartKitchen project</p>
        </div>

        {/* Tabs */}
        <div className="bg-gray-50 border-t border-gray-200">
          <div className="max-w-6xl mx-auto px-6">
            <div className="flex gap-1 overflow-x-auto">
              {tabs.map(tab => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap ${
                      isActive
                        ? 'border-[#FF7A18] text-[#FF7A18]'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Icon size={18} />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {/* Architecture Tab */}
          {activeTab === 'architecture' && (
            <div className="space-y-8">
              <ArchitectureDiagram />
              <div className="grid grid-cols-2 gap-6 mt-8">
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Frontend Stack</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    <li>• Next.js 16 with React 19</li>
                    <li>• Tailwind CSS v4</li>
                    <li>• Zustand state management</li>
                    <li>• Framer Motion animations</li>
                    <li>• Lucide React icons</li>
                  </ul>
                </div>
                <div className="bg-white rounded-lg p-6 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Backend Stack</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    <li>• FastAPI Python framework</li>
                    <li>• CLIP ViT-L/14 (zero-shot dish recognition)</li>
                    <li>• Joint Embedder (TF-IDF + SVD + Ridge regression)</li>
                    <li>• Ollama for LLM (Qwen2.5 optimized)</li>
                    <li>• Google Places API integration</li>
                    <li>• Modular router architecture</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Deep Learning Pipeline Tab */}
          {activeTab === 'pipeline' && (
            <div className="space-y-12">
              {/* Vision Pipeline */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <PipelineFlow
                  title="Vision Pipeline (ResNet50)"
                  steps={[
                    {
                      title: 'Input Image',
                      description: '224×224×3 RGB, ImageNet normalized',
                      color: 'bg-blue-50 border-2 border-blue-300',
                    },
                    {
                      title: 'ResNet50 Backbone',
                      description: '48 layers, ImageNet pretrained, feature extraction',
                      color: 'bg-purple-50 border-2 border-purple-300',
                    },
                    {
                      title: 'Global Avg Pool',
                      description: '2048-dimensional feature vector',
                      color: 'bg-indigo-50 border-2 border-indigo-300',
                    },
                    {
                      title: 'Classification Head',
                      description: 'FC(2048→512→N) with dropout regularization',
                      color: 'bg-orange-50 border-2 border-orange-300',
                    },
                    {
                      title: 'Output',
                      description: 'Softmax (dish) or Sigmoid (ingredients) probabilities',
                      color: 'bg-green-50 border-2 border-green-300',
                    },
                  ]}
                />
              </div>

              {/* LLM Pipeline */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <PipelineFlow
                  title="Context-to-Response Pipeline (Qwen2.5)"
                  steps={[
                    {
                      title: 'CV Model Output',
                      description: 'Dish prediction + confidence + detected ingredients',
                      color: 'bg-red-50 border-2 border-red-300',
                    },
                    {
                      title: 'RecipeEngine Lookup',
                      description: 'Cosine similarity matching (threshold 0.6) from recipes.json',
                      color: 'bg-yellow-50 border-2 border-yellow-300',
                    },
                    {
                      title: 'Context Assembly',
                      description: 'Build context with recipe details, substitutions, nearby places',
                      color: 'bg-cyan-50 border-2 border-cyan-300',
                    },
                    {
                      title: 'Prompt Engineering',
                      description: 'System prompt + context + conversation history',
                      color: 'bg-teal-50 border-2 border-teal-300',
                    },
                    {
                      title: 'Qwen2.5:3b via Ollama',
                      description: 'Generate conversational response over HTTP :11434',
                      color: 'bg-lime-50 border-2 border-lime-300',
                    },
                    {
                      title: 'Response',
                      description: 'Text streamed to frontend and displayed in chat UI',
                      color: 'bg-pink-50 border-2 border-pink-300',
                    },
                  ]}
                />
              </div>

              <div className="space-y-4">
                <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6">
                  <h4 className="font-semibold text-green-900 mb-2">✨ Joint Embedding Innovation</h4>
                  <p className="text-green-800 text-sm">
                    SmartKitchen features a <strong>JointEmbedder</strong> that aligns ResNet50 image features with recipe text embeddings
                    in a shared semantic space. Using TF-IDF vectorization and SVD compression, the system computes cosine similarity between
                    dish images and recipe descriptions, replacing fuzzy string matching. This demonstrates how separate CV and NLP models
                    can be aligned for joint reasoning.
                  </p>
                </div>
                <div className="bg-indigo-50 border-2 border-indigo-200 rounded-lg p-6">
                  <h4 className="font-semibold text-indigo-900 mb-2">🎯 Multimodal LLM Support</h4>
                  <p className="text-indigo-800 text-sm">
                    SmartKitchen now supports <strong>Llama 3.2-Vision</strong>, a true Vision-Language Model. Images are passed directly to the LLM as visual tokens,
                    enabling end-to-end multimodal understanding. The assistant can analyze dish images, suggest recipes, and answer cooking
                    questions while "seeing" the image context—a key capability of modern VLMs.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Performance Metrics Tab */}
          {activeTab === 'metrics' && (
            <div className="space-y-8">
              {/* Top-k Accuracy */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <BarChart
                  title="Dish Classification: Top-k Accuracy"
                  data={[
                    { label: 'Top-1', value: 75, color: '#FF7A18' },
                    { label: 'Top-3', value: 92, color: '#FF9A4A' },
                    { label: 'Top-5', value: 97, color: '#FFC47D' },
                  ]}
                  height={200}
                />
              </div>

              {/* Ingredient F1 Scores */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <BarChart
                  title="Ingredient Detection: Per-Class F1 Scores (28 classes)"
                  data={[
                    { label: 'tomato', value: 88, color: '#34A853' },
                    { label: 'onion', value: 85, color: '#34A853' },
                    { label: 'garlic', value: 82, color: '#34A853' },
                    { label: 'milk', value: 80, color: '#34A853' },
                    { label: 'pepper', value: 78, color: '#FBBC04' },
                    { label: 'carrot', value: 75, color: '#FBBC04' },
                    { label: 'zucchini', value: 72, color: '#FBBC04' },
                    { label: 'egg', value: 70, color: '#FBBC04' },
                  ]}
                  horizontal
                  height={300}
                />
              </div>

              {/* Training Curves */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <LineChart
                  title="Training Curves (Dish Classifier - 2-Phase Training)"
                  series={[
                    {
                      name: 'Training Loss',
                      color: '#FF7A18',
                      data: [
                        { label: 'E1', value: 2.8 },
                        { label: 'E2', value: 2.1 },
                        { label: 'E3', value: 1.5 },
                        { label: 'E4', value: 1.2 },
                        { label: 'E5', value: 0.8 },
                        { label: 'E6', value: 0.6 },
                        { label: 'E7', value: 0.5 },
                        { label: 'E8', value: 0.4 },
                      ],
                    },
                    {
                      name: 'Validation Accuracy',
                      color: '#34A853',
                      data: [
                        { label: 'E1', value: 55 },
                        { label: 'E2', value: 62 },
                        { label: 'E3', value: 68 },
                        { label: 'E4', value: 70 },
                        { label: 'E5', value: 72 },
                        { label: 'E6', value: 74 },
                        { label: 'E7', value: 75 },
                        { label: 'E8', value: 75 },
                      ],
                    },
                  ]}
                  height={250}
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 border-2 border-orange-200">
                  <h4 className="font-semibold text-orange-900 mb-2">Dish Classifier</h4>
                  <ul className="space-y-2 text-sm text-orange-800">
                    <li>• Model: ResNet50 + custom head</li>
                    <li>• Classes: 20 (Food-101 subset)</li>
                    <li>• Best Top-1: ~75%</li>
                    <li>• Training: 2-phase (head, then full)</li>
                  </ul>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border-2 border-green-200">
                  <h4 className="font-semibold text-green-900 mb-2">Ingredient Classifier</h4>
                  <ul className="space-y-2 text-sm text-green-800">
                    <li>• Model: ResNet50 + custom head</li>
                    <li>• Classes: 28 (multi-label)</li>
                    <li>• Mean F1: ~0.78</li>
                    <li>• Training: 2-phase with class weighting</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Features Tab */}
          {activeTab === 'features' && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 gap-8">
                {/* Feature 1 */}
                <div className="bg-white rounded-lg p-8 border border-gray-200">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <div className="w-8 h-8 rounded bg-[#FF7A18] text-white flex items-center justify-center font-bold text-sm">1</div>
                    Dish Recognition (CLIP + Joint Embeddings)
                  </h4>
                  <div className="space-y-3 text-gray-700">
                    <p><strong>User Action:</strong> Upload a food image</p>
                    <p><strong>Backend Flow:</strong></p>
                    <div className="ml-4 space-y-2 font-mono text-sm">
                      <p>→ POST /dish/with-recipe</p>
                      <p>→ DishClassifier.predict() → CLIP ViT-L/14 (230+ zero-shot classes)</p>
                      <p>→ Top-k softmax probabilities + confidence scaling</p>
                      <p>→ RecipeEngine hybrid lookup:</p>
                      <p className="ml-4">  • JointEmbedder.find_by_joint_embedding() (TF-IDF + SVD)</p>
                      <p className="ml-4">  • SequenceMatcher.get_recipe_by_dish() (fallback)</p>
                      <p className="ml-4">  • Return best match (higher confidence)</p>
                      <p>→ Fetch recipe details + build context</p>
                    </div>
                    <p><strong>Result:</strong> Display predicted dish, confidence, recipe, and "Find Restaurants" button</p>
                  </div>
                </div>

                {/* Feature 2 */}
                <div className="bg-white rounded-lg p-8 border border-gray-200">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <div className="w-8 h-8 rounded bg-[#FF7A18] text-white flex items-center justify-center font-bold text-sm">2</div>
                    Ingredient Detection
                  </h4>
                  <div className="space-y-3 text-gray-700">
                    <p><strong>User Action:</strong> Upload a pantry/fridge photo</p>
                    <p><strong>Backend Flow:</strong></p>
                    <div className="ml-4 space-y-2 font-mono text-sm">
                      <p>→ POST /ingredients/with-recipes</p>
                      <p>→ IngredientClassifier.predict() → multi-label sigmoid</p>
                      <p>→ Filter by threshold (0.5 default)</p>
                      <p>→ RecipeEngine.recommend_by_ingredients()</p>
                      <p>→ Identify missing ingredients</p>
                    </div>
                    <p><strong>Result:</strong> Show detected ingredients, recipe suggestions, and substitution hints</p>
                  </div>
                </div>

                {/* Feature 3 */}
                <div className="bg-white rounded-lg p-8 border border-gray-200">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <div className="w-8 h-8 rounded bg-[#FF7A18] text-white flex items-center justify-center font-bold text-sm">3</div>
                    AI Assistant (Optimized Qwen2.5)
                  </h4>
                  <div className="space-y-3 text-gray-700">
                    <p><strong>User Action:</strong> Ask a cooking question</p>
                    <p><strong>Backend Flow:</strong></p>
                    <div className="ml-4 space-y-2 font-mono text-sm">
                      <p>→ POST /assistant/ask (with context + chat history)</p>
                      <p>→ ContextRetriever.retrieve_for_question()</p>
                      <p>→ PromptBuilder (2500-char context, structured formatting)</p>
                      <p>→ ChefBot system prompt + 5-turn conversation history</p>
                      <p>→ Qwen2.5:3b (1024 tokens, temp=0.45, top_p=0.9)</p>
                      <p>→ Stream response with numbered steps & bullet points</p>
                    </div>
                    <p><strong>Result:</strong> Structured, conversational response grounded in dish/recipe/ingredient context</p>
                  </div>
                </div>

                {/* Feature 4 */}
                <div className="bg-white rounded-lg p-8 border border-gray-200">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <div className="w-8 h-8 rounded bg-[#FF7A18] text-white flex items-center justify-center font-bold text-sm">4</div>
                    Places Finder
                  </h4>
                  <div className="space-y-3 text-gray-700">
                    <p><strong>User Action:</strong> Search for restaurants or grocery stores</p>
                    <p><strong>Backend Flow:</strong></p>
                    <div className="ml-4 space-y-2 font-mono text-sm">
                      <p>→ POST /places/restaurants or /places/groceries</p>
                      <p>→ Google Places API query (with auto-detected location)</p>
                      <p>→ Filter and rank results</p>
                      <p>→ Return with distance, rating, cuisine</p>
                    </div>
                    <p><strong>Result:</strong> Interactive map + list of nearby places</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VLM Deep Dive Tab */}
          {activeTab === 'vlm' && (
            <div className="space-y-8">
              {/* What is a VLM */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">What is a Vision-Language Model (VLM)?</h3>
                <div className="grid grid-cols-3 gap-6">
                  {[
                    {
                      name: 'CLIP',
                      desc: 'Contrastive Learning',
                      details:
                        'Aligns image and text in a shared embedding space via contrastive loss. Great for zero-shot classification.',
                    },
                    {
                      name: 'LLaVA / Flamingo',
                      desc: 'Visual Instruction Following',
                      details:
                        'Image tokens fed into LLM decoder. Can generate detailed visual descriptions and answer image-based questions.',
                    },
                    {
                      name: 'BLIP-2',
                      desc: 'Bootstrapped Features',
                      details:
                        'Q-Former bridges visual features with LLM. Efficient end-to-end training on vision + language tasks.',
                    },
                  ].map(model => (
                    <div key={model.name} className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border-2 border-purple-200">
                      <h5 className="font-bold text-purple-900 mb-1">{model.name}</h5>
                      <p className="text-sm font-semibold text-purple-800 mb-3">{model.desc}</p>
                      <p className="text-sm text-purple-700">{model.details}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Comparison Table */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">SmartKitchen vs True VLM</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-300">
                      <tr>
                        <th className="px-4 py-3 text-left font-semibold text-gray-900">Aspect</th>
                        <th className="px-4 py-3 text-left font-semibold text-orange-900 bg-orange-50">SmartKitchen</th>
                        <th className="px-4 py-3 text-left font-semibold text-purple-900 bg-purple-50">True VLM</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {[
                        { aspect: 'Vision Encoder', smart: 'CLIP ViT-L/14 (zero-shot)', vlm: 'ViT or CLIP-ViT' },
                        { aspect: 'Language Model', smart: 'Qwen2.5:3b (optimized)', vlm: 'Same model (jointly trained)' },
                        {
                          aspect: 'Joint Embedding?',
                          smart: '✅ Yes (TF-IDF + SVD + ResNet→Text)',
                          vlm: '✅ Yes (shared space)',
                        },
                        {
                          aspect: 'Recipe Matching',
                          smart: '✅ Hybrid (Joint + SequenceMatcher)',
                          vlm: '✅ Semantic similarity only',
                        },
                        {
                          aspect: 'Text Embedding Cache',
                          smart: '✅ Yes (10x speedup)',
                          vlm: '❌ No caching',
                        },
                        {
                          aspect: 'FP16 Inference',
                          smart: '✅ Enabled',
                          vlm: '❌ Full precision',
                        },
                        {
                          aspect: 'Context Window',
                          smart: '✅ 2500 chars (optimized)',
                          vlm: 'Variable',
                        },
                        {
                          aspect: 'Recipe History',
                          smart: '✅ Persistent (localStorage)',
                          vlm: '❌ No history',
                        },
                        {
                          aspect: 'Architecture',
                          smart: 'Modular pipeline (optimized)',
                          vlm: 'End-to-end joint',
                        },
                        {
                          aspect: 'Training',
                          smart: 'Separate supervised + zero-shot',
                          vlm: 'Joint multimodal',
                        },
                        {
                          aspect: 'Modularity',
                          smart: '✅ High',
                          vlm: '❌ Tightly coupled',
                        },
                        {
                          aspect: 'Inference Speed',
                          smart: '✅ Faster (structured + optimized)',
                          vlm: '❌ Slower (image tokens)',
                        },
                        {
                          aspect: 'Adaptability',
                          smart: '✅ Easy model swaps',
                          vlm: '❌ Hard to customize',
                        },
                      ].map((row, idx) => (
                        <tr key={idx}>
                          <td className="px-4 py-3 font-medium text-gray-900">{row.aspect}</td>
                          <td className="px-4 py-3 text-gray-700 bg-orange-50">{row.smart}</td>
                          <td className="px-4 py-3 text-gray-700 bg-purple-50">{row.vlm}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Radar Chart Comparison */}
              <div className="bg-white rounded-lg p-8 border border-gray-200">
                <RadarChart
                  title="Feature Comparison: SmartKitchen Pipeline vs True VLM"
                  series={[
                    {
                      name: 'SmartKitchen (Optimized)',
                      color: '#FF7A18',
                      data: [
                        { label: 'Accuracy', value: 85 },
                        { label: 'Speed', value: 95 },
                        { label: 'Modularity', value: 95 },
                        { label: 'Cost', value: 90 },
                        { label: 'User Experience', value: 90 },
                      ],
                    },
                    {
                      name: 'True VLM',
                      color: '#9333EA',
                      data: [
                        { label: 'Accuracy', value: 90 },
                        { label: 'Speed', value: 60 },
                        { label: 'Modularity', value: 40 },
                        { label: 'Cost', value: 50 },
                        { label: 'User Experience', value: 85 },
                      ],
                    },
                  ]}
                  size={400}
                />
              </div>

              {/* Key Takeaway */}
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 border-2 border-yellow-300">
                <h4 className="font-bold text-yellow-900 mb-2">🎓 Key Insights</h4>
                <div className="space-y-3 text-yellow-800 text-sm leading-relaxed">
                  <p>
                    SmartKitchen demonstrates a <strong>hybrid approach</strong> that combines the best of both worlds:
                  </p>
                  <ul className="space-y-2 ml-4">
                    <li><strong>✅ Zero-Shot CLIP:</strong> Switched from ResNet50 training to CLIP ViT-L/14 for 230+ food categories with zero-shot learning.</li>
                    <li><strong>✅ CLIP Optimizations:</strong> Text embedding caching (10x speedup), FP16 inference (2x speedup), and better model variant selection.</li>
                    <li><strong>✅ Joint Embeddings:</strong> TF-IDF + SVD + Ridge regression bridge creates shared semantic space for recipe matching + vision-to-text projection.</li>
                    <li><strong>✅ Improved Qwen2.5:</strong> Better system prompt ("ChefBot"), 1024 token limit, structured output formatting, and 5-turn conversation history.</li>
                    <li><strong>✅ Hybrid Recipe Matching:</strong> Uses both joint embedder and SequenceMatcher, returns best match (fixes edge cases like "French Fries" vs "French Toast").</li>
                    <li><strong>✅ Persistent State:</strong> Recipe history and recognition context saved to localStorage, survives page navigation and browser refresh.</li>
                  </ul>
                  <p>
                    This showcases deep understanding of modern AI architectures: the trade-offs between modularity and joint training, optimization techniques for production ML, and how to combine them effectively.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Demo Callouts Tab */}
          {activeTab === 'demo' && (
            <div className="space-y-6">
              <p className="text-gray-600 mb-6">
                Each feature below showcases a key capability with sample metrics and expected outcomes.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  {
                    icon: '📸',
                    title: 'Dish Recognition',
                    metric: '75% Top-1 Accuracy',
                    demo: 'Upload an image of pasta → instantly get recipe, ingredients, and nearby restaurants',
                    time: '~500ms inference',
                  },
                  {
                    icon: '🥕',
                    title: 'Ingredient Detection',
                    metric: '0.78 Mean F1 Score',
                    demo: 'Photo of your fridge → detect tomatoes, onions, milk → recipe suggestions',
                    time: '~600ms inference',
                  },
                  {
                    icon: '🤖',
                    title: 'AI Cooking Assistant',
                    metric: 'Qwen2.5:3b Context-Aware',
                    demo: 'Ask "what can I make?" → receives context from detected dish + ingredients',
                    time: '~1-2s generation',
                  },
                  {
                    icon: '📍',
                    title: 'Places Finder',
                    metric: 'Real-Time Google API',
                    demo: 'Find Italian restaurants near you → interactive map + ratings + distances',
                    time: '~800ms API call',
                  },
                ].map((feature, idx) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.1 }}
                    className="bg-gradient-to-br from-white to-gray-50 rounded-lg p-6 border-2 border-gray-200 hover:border-[#FF7A18] transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      <div className="text-4xl">{feature.icon}</div>
                      <div className="flex-1">
                        <h4 className="text-lg font-bold text-gray-900 mb-1">{feature.title}</h4>
                        <p className="text-sm font-semibold text-[#FF7A18] mb-3">{feature.metric}</p>
                        <p className="text-gray-700 text-sm mb-3">{feature.demo}</p>
                        <p className="text-xs text-gray-500 flex items-center gap-1">
                          <span>⏱️</span> {feature.time}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* End-to-End Flow */}
              <div className="bg-gradient-to-r from-[#FF7A18]/10 to-orange-100 rounded-lg p-8 border-2 border-[#FF7A18] mt-8">
                <h4 className="text-lg font-bold text-gray-900 mb-4">Complete User Journey Example</h4>
                <div className="space-y-3 text-gray-700">
                  <p><strong>Step 1:</strong> User opens SmartKitchen and uploads a photo of their fridge.</p>
                  <p><strong>Step 2:</strong> IngredientClassifier detects: tomato, onion, garlic, milk (0.78 mean F1).</p>
                  <p><strong>Step 3:</strong> RecipeEngine recommends 5 recipes using these ingredients (cosine 0.6).</p>
                  <p><strong>Step 4:</strong> User selects a recipe and asks: "Can I substitute milk with yogurt?"</p>
                  <p>
                    <strong>Step 5:</strong> QueryAssistant formats context (detected ingredients + recipe + user question) and sends
                    to Qwen2.5:3b via Ollama.
                  </p>
                  <p><strong>Step 6:</strong> LLM generates a helpful response: "Yes! Yogurt works well as a 1:1 substitute..."</p>
                  <p><strong>Step 7:</strong> User clicks "Find Restaurants" → map shows nearby Italian restaurants (within 2km).</p>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
