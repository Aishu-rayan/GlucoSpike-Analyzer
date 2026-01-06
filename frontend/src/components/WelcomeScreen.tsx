import { motion } from 'framer-motion';
import { Upload, Search, TrendingDown, Sparkles, ArrowRight } from 'lucide-react';

interface WelcomeScreenProps {
  onSampleQuery: (query: string) => void;
}

export function WelcomeScreen({ onSampleQuery }: WelcomeScreenProps) {
  const sampleQueries = [
    { icon: '🍕', text: 'Analyze pizza', query: 'Tell me about the insulin spike from eating pizza' },
    { icon: '🍚', text: 'White rice vs brown rice', query: 'Compare white rice and brown rice for insulin spike' },
    { icon: '🥗', text: 'Best low-spike foods', query: 'What are the best foods with low insulin spike?' },
    { icon: '🍌', text: 'Fruits and insulin', query: 'Which fruits are best for low insulin spike?' },
  ];
  
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
      {/* Logo animation */}
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: 'spring', duration: 0.8 }}
        className="w-24 h-24 rounded-3xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center mb-6 shadow-2xl glow-sage"
      >
        <span className="text-5xl">🥗</span>
      </motion.div>
      
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-3xl font-bold mb-2"
      >
        Welcome to <span className="gradient-text">GlucoGuide</span>
      </motion.h1>
      
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="text-sage-400 max-w-md mb-8"
      >
        Understand how your food choices affect your insulin levels. 
        Upload a food photo or ask questions to get started.
      </motion.p>
      
      {/* Features */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mb-8"
      >
        <label htmlFor="image-upload" className="cursor-pointer">
          <FeatureCard
            icon={<Upload className="w-5 h-5" />}
            title="Upload Food Photos"
            description="AI-powered food recognition"
          />
        </label>
        <FeatureCard
          icon={<Search className="w-5 h-5" />}
          title="Glycemic Analysis"
          description="Calculate effective GL scores"
        />
        <FeatureCard
          icon={<TrendingDown className="w-5 h-5" />}
          title="Smart Recommendations"
          description="Tips to reduce insulin spikes"
        />
      </motion.div>
      
      {/* Sample queries */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="w-full max-w-lg"
      >
        <div className="flex items-center gap-2 mb-3 justify-center">
          <Sparkles className="w-4 h-4 text-honey-400" />
          <span className="text-sm text-sage-400">Try asking about</span>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          {sampleQueries.map((item, i) => (
            <motion.button
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 + i * 0.1 }}
              onClick={() => onSampleQuery(item.query)}
              className="group flex items-center gap-2 p-3 rounded-xl bg-sage-800/30 border border-sage-700/30 hover:border-sage-500/50 hover:bg-sage-800/50 transition-all text-left"
            >
              <span className="text-xl">{item.icon}</span>
              <span className="text-sm text-sage-300 group-hover:text-sage-100 flex-1">{item.text}</span>
              <ArrowRight className="w-4 h-4 text-sage-500 group-hover:text-sage-300 group-hover:translate-x-1 transition-all" />
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-4 rounded-xl bg-sage-800/30 border border-sage-700/30">
      <div className="w-10 h-10 rounded-lg bg-sage-700/50 flex items-center justify-center text-sage-300 mb-3">
        {icon}
      </div>
      <h3 className="font-medium text-sage-100 mb-1">{title}</h3>
      <p className="text-xs text-sage-400">{description}</p>
    </div>
  );
}

