'use client';

import { motion } from 'framer-motion';
import { ArrowDown } from 'lucide-react';

interface PipelineStep {
  title: string;
  description: string;
  color: string;
}

interface PipelineFlowProps {
  title: string;
  steps: PipelineStep[];
  direction?: 'vertical' | 'horizontal';
}

export function PipelineFlow({
  title,
  steps,
  direction = 'vertical',
}: PipelineFlowProps) {
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
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 },
  };

  if (direction === 'horizontal') {
    return (
      <div className="w-full">
        <h3 className="text-lg font-semibold text-gray-900 mb-8">{title}</h3>
        <motion.div
          className="flex items-center justify-between gap-4 overflow-x-auto pb-4"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {steps.map((step, idx) => (
            <div key={step.title} className="flex items-center gap-4 flex-shrink-0">
              <motion.div
                className={`${step.color} rounded-lg p-4 min-w-48`}
                variants={itemVariants}
              >
                <div className="font-semibold text-gray-900">{step.title}</div>
                <div className="text-sm text-gray-600 mt-2">{step.description}</div>
              </motion.div>
              {idx < steps.length - 1 && (
                <motion.div
                  className="flex-shrink-0 text-gray-400"
                  variants={itemVariants}
                >
                  <ArrowDown size={24} className="transform -rotate-90" />
                </motion.div>
              )}
            </div>
          ))}
        </motion.div>
      </div>
    );
  }

  // Vertical layout
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-8">{title}</h3>
      <motion.div
        className="space-y-4"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {steps.map((step, idx) => (
          <div key={step.title}>
            <motion.div
              className={`${step.color} rounded-lg p-4`}
              variants={itemVariants}
            >
              <div className="font-semibold text-gray-900 text-lg">{step.title}</div>
              <div className="text-sm text-gray-600 mt-2">{step.description}</div>
            </motion.div>
            {idx < steps.length - 1 && (
              <motion.div
                className="flex justify-center py-2 text-gray-400"
                variants={itemVariants}
              >
                <ArrowDown size={24} />
              </motion.div>
            )}
          </div>
        ))}
      </motion.div>
    </div>
  );
}
