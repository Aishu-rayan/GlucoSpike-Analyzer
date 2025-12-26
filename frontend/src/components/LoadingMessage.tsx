import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';

export function LoadingMessage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center">
        <Bot className="w-5 h-5 text-white" />
      </div>
      
      <div className="flex-1">
        <div className="rounded-2xl px-4 py-3 bg-sage-800/50 border border-sage-700/30 inline-flex items-center gap-2">
          <span className="text-sage-300 text-sm">Analyzing your food</span>
          <div className="flex gap-1">
            <span className="w-2 h-2 rounded-full bg-sage-400 loading-dot" />
            <span className="w-2 h-2 rounded-full bg-sage-400 loading-dot" />
            <span className="w-2 h-2 rounded-full bg-sage-400 loading-dot" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

