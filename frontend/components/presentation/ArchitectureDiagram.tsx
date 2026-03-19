'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export function ArchitectureDiagram() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-8">System Architecture</h3>

      <motion.div
        className="space-y-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Layer 1: Frontend */}
        <motion.div variants={itemVariants}>
          <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
            <div className="font-semibold text-blue-900">Next.js Frontend</div>
            <div className="text-sm text-blue-700 mt-1">Port 3000 • React + Zustand + Tailwind</div>
          </div>
        </motion.div>

        {/* Arrow */}
        <motion.div
          className="flex justify-center"
          variants={itemVariants}
        >
          <div className="flex items-center gap-2 text-gray-500">
            <ArrowRight size={16} />
            <span className="text-xs">HTTP/REST</span>
            <ArrowRight size={16} />
          </div>
        </motion.div>

        {/* Layer 2: Backend */}
        <motion.div variants={itemVariants}>
          <div className="bg-purple-50 border-2 border-purple-300 rounded-lg p-4">
            <div className="font-semibold text-purple-900">FastAPI Backend</div>
            <div className="text-sm text-purple-700 mt-1">Port 8000 • Python + Pydantic</div>
          </div>
        </motion.div>

        {/* Arrow */}
        <motion.div
          className="flex justify-center"
          variants={itemVariants}
        >
          <div className="flex items-center gap-2 text-gray-500">
            <ArrowRight size={16} />
          </div>
        </motion.div>

        {/* Layer 3: Services */}
        <motion.div variants={itemVariants}>
          <div className="grid grid-cols-2 gap-4">
            {[
              { title: 'DishClassifier', desc: 'ResNet50 • 20 classes', color: 'bg-orange-50 border-orange-300' },
              { title: 'IngredientClassifier', desc: 'ResNet50 • 28 classes', color: 'bg-green-50 border-green-300' },
              { title: 'RecipeEngine', desc: 'recipes.json • Cosine 0.6', color: 'bg-yellow-50 border-yellow-300' },
              { title: 'QueryAssistant', desc: 'Qwen2.5:3b via Ollama', color: 'bg-red-50 border-red-300' },
            ].map((service, idx) => (
              <motion.div
                key={service.title}
                className={`border-2 rounded-lg p-3 ${service.color}`}
                variants={itemVariants}
                transition={{ delay: 0.4 + idx * 0.05 }}
              >
                <div className="font-medium text-sm">{service.title}</div>
                <div className="text-xs text-gray-600 mt-1">{service.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Arrow */}
        <motion.div
          className="flex justify-center"
          variants={itemVariants}
        >
          <div className="flex items-center gap-2 text-gray-500">
            <ArrowRight size={16} />
          </div>
        </motion.div>

        {/* Layer 4: External Services */}
        <motion.div variants={itemVariants}>
          <div className="grid grid-cols-3 gap-4">
            {[
              { title: 'Google Places API', desc: 'Restaurants & Groceries' },
              { title: 'Ollama Server', desc: 'Port 11434' },
              { title: 'Local Data', desc: 'recipes.json, substitutions' },
            ].map((service, idx) => (
              <motion.div
                key={service.title}
                className="bg-gray-50 border-2 border-gray-300 rounded-lg p-3"
                variants={itemVariants}
                transition={{ delay: 0.6 + idx * 0.05 }}
              >
                <div className="font-medium text-sm text-gray-900">{service.title}</div>
                <div className="text-xs text-gray-600 mt-1">{service.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
