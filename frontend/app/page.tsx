"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ChefHat, ShoppingBasket, MessageSquare, MapPin, ArrowRight, Sparkles } from "lucide-react";

const FEATURES = [
  {
    icon: ChefHat,
    title: "Dish Recognition",
    description: "Upload a food photo and get instant AI identification with recipe matches.",
    href: "/dish",
    color: "from-orange-500 to-amber-400",
  },
  {
    icon: ShoppingBasket,
    title: "Ingredient Detection",
    description: "Scan your pantry and discover recipes you can make right now.",
    href: "/ingredients",
    color: "from-emerald-500 to-teal-400",
  },
  {
    icon: MessageSquare,
    title: "AI Assistant",
    description: "Ask any cooking question — get grounded, context-aware answers.",
    href: "/assistant",
    color: "from-blue-500 to-indigo-400",
  },
  {
    icon: MapPin,
    title: "Nearby Places",
    description: "Find restaurants and grocery stores near you based on your dish.",
    href: "/places",
    color: "from-purple-500 to-pink-400",
  },
];

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45 } },
};

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden px-6 py-20 lg:py-32"
               style={{ background: "linear-gradient(135deg, #1A1A1A 0%, #2D1207 50%, #1A1A1A 100%)" }}>
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-10"
               style={{ background: "radial-gradient(circle, #FF7A18, transparent 70%)" }} />
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full opacity-8"
               style={{ background: "radial-gradient(circle, #FF7A18, transparent 70%)" }} />
        </div>

        <div className="relative max-w-3xl mx-auto text-center">
          <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full border text-orange-400 border-orange-500/30 bg-orange-500/10 mb-6">
              <Sparkles size={12} />
              AI-Powered Cooking Assistant
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.1 }}
            className="text-5xl lg:text-7xl font-bold tracking-tight mb-4"
          >
            <span className="text-white">Smart</span>
            <span style={{ background: "linear-gradient(90deg, #FF7A18, #FFB347)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Kitchen</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.2 }}
            className="text-lg lg:text-xl text-gray-300 mb-3 leading-relaxed"
          >
            See what you can cook, ask questions about it,<br className="hidden sm:block" /> or find where to buy it.
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.35 }}
            className="text-sm text-gray-500 mb-10"
          >
            Dish recognition · Ingredient detection · Recipe recommendations · Local discovery
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-3"
          >
            <Link
              href="/dish"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white shadow-lg transition-transform hover:scale-105 hover:shadow-orange-500/25"
              style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}
            >
              <ChefHat size={16} />
              Try Dish Recognition
              <ArrowRight size={14} />
            </Link>
            <Link
              href="/ingredients"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-gray-200 border border-white/20 bg-white/5 backdrop-blur-sm transition-all hover:bg-white/10"
            >
              <ShoppingBasket size={16} />
              Try Ingredient Detection
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-16 max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Everything you need in the kitchen</h2>
          <p className="text-gray-500 text-sm">Four powerful AI features, seamlessly connected.</p>
        </motion.div>

        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-4"
        >
          {FEATURES.map(({ icon: Icon, title, description, href, color }) => (
            <motion.div key={href} variants={item}>
              <Link href={href} className="group block">
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1 h-full">
                  <div className={`inline-flex w-10 h-10 rounded-xl items-center justify-center text-white mb-4 bg-gradient-to-br ${color}`}>
                    <Icon size={20} strokeWidth={2} />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1.5 group-hover:text-orange-600 transition-colors">{title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
                  <div className="mt-4 flex items-center gap-1 text-xs font-medium text-orange-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    Get started <ArrowRight size={12} />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* How it works */}
      <section className="px-6 pb-20 max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8"
        >
          <h2 className="text-xl font-bold text-gray-900 mb-6 text-center">How it works</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              { step: "01", title: "Capture or Upload", desc: "Take a photo of your dish or ingredients using your camera or device gallery." },
              { step: "02", title: "AI Recognition", desc: "Our models identify what's in your photo and match it with recipes and context." },
              { step: "03", title: "Explore & Discover", desc: "Get recipes, ask the AI assistant questions, and find local restaurants or stores." },
            ].map(({ step, title, desc }) => (
              <div key={step} className="text-center">
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-orange-50 text-orange-600 text-sm font-bold mb-3">{step}</div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">{title}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </section>
    </div>
  );
}
