import { motion } from 'framer-motion';
import { TrendingDown, Zap, AlertTriangle, CheckCircle, Info, Flame, Wheat, Drumstick, Droplets } from 'lucide-react';
import { EGLResult, SpikeLevel } from '../types';

interface EGLResultCardProps {
  result: EGLResult;
}

const spikeLevelConfig: Record<SpikeLevel, { 
  label: string; 
  color: string; 
  bgClass: string; 
  icon: React.ReactNode;
  description: string;
}> = {
  low: {
    label: 'LOW SPIKE',
    color: 'text-sage-400',
    bgClass: 'spike-low',
    icon: <CheckCircle className="w-5 h-5" />,
    description: 'Safe to eat freely'
  },
  moderate: {
    label: 'MODERATE SPIKE',
    color: 'text-honey-400',
    bgClass: 'spike-moderate',
    icon: <AlertTriangle className="w-5 h-5" />,
    description: 'Eat in moderation'
  },
  high: {
    label: 'HIGH SPIKE',
    color: 'text-coral-400',
    bgClass: 'spike-high',
    icon: <Zap className="w-5 h-5" />,
    description: 'Consider alternatives'
  }
};

export function EGLResultCard({ result }: EGLResultCardProps) {
  const spikeConfig = spikeLevelConfig[result.spike_level];
  const beforeConfig = spikeLevelConfig[result.spike_level_before_modifiers];
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl border border-sage-700/30 bg-sage-900/50 overflow-hidden"
    >
      {/* Header with spike level */}
      <div className={`px-4 py-3 ${spikeConfig.bgClass} border-b border-current/20`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {spikeConfig.icon}
            <div>
              <span className="font-semibold">{spikeConfig.label}</span>
              <p className="text-xs opacity-80">{spikeConfig.description}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{result.effective_gl.toFixed(1)}</div>
            <div className="text-xs opacity-70">eGL Score</div>
          </div>
        </div>
      </div>
      
      {/* Food name */}
      <div className="px-4 py-3 border-b border-sage-700/30">
        <h3 className="font-semibold text-sage-100 capitalize">{result.food_name}</h3>
        <p className="text-xs text-sage-400">
          {result.portions} serving{result.portions !== 1 ? 's' : ''} • {result.serving_size}g
        </p>
      </div>
      
      {/* Nutrition breakdown */}
      <div className="px-4 py-3 border-b border-sage-700/30">
        <p className="text-xs text-sage-400 mb-2 uppercase tracking-wider">Nutrition per serving</p>
        <div className="grid grid-cols-4 gap-2">
          <NutrientPill 
            icon={<Wheat className="w-3.5 h-3.5" />}
            label="Carbs" 
            value={result.nutrition.carbs} 
            unit="g"
            color="text-honey-400"
          />
          <NutrientPill 
            icon={<Drumstick className="w-3.5 h-3.5" />}
            label="Protein" 
            value={result.nutrition.protein} 
            unit="g"
            color="text-coral-400"
          />
          <NutrientPill 
            icon={<Droplets className="w-3.5 h-3.5" />}
            label="Fat" 
            value={result.nutrition.fat} 
            unit="g"
            color="text-sage-400"
          />
          <NutrientPill 
            icon={<Flame className="w-3.5 h-3.5" />}
            label="Fiber" 
            value={result.nutrition.fiber} 
            unit="g"
            color="text-sage-300"
          />
        </div>
      </div>
      
      {/* GL Comparison */}
      <div className="px-4 py-3 border-b border-sage-700/30">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-sage-400 uppercase tracking-wider">Glycemic Analysis</span>
          {result.spike_improved && (
            <span className="flex items-center gap-1 text-xs text-sage-400 bg-sage-800/50 px-2 py-0.5 rounded-full">
              <TrendingDown className="w-3 h-3" />
              Improved by modifiers
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-4">
          {/* Base GL */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-sage-400">Base GL</span>
              <span className={`text-xs ${beforeConfig.color}`}>{beforeConfig.label}</span>
            </div>
            <div className="h-2 rounded-full bg-sage-800 overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(result.base_gl / 30 * 100, 100)}%` }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className={`h-full rounded-full ${
                  result.spike_level_before_modifiers === 'low' ? 'bg-sage-500' :
                  result.spike_level_before_modifiers === 'moderate' ? 'bg-honey-500' : 'bg-coral-500'
                }`}
              />
            </div>
            <span className="text-sm font-semibold text-sage-200">{result.base_gl.toFixed(1)}</span>
          </div>
          
          {/* Arrow */}
          <div className="text-sage-500">→</div>
          
          {/* Effective GL */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-sage-400">Effective GL</span>
              <span className={`text-xs ${spikeConfig.color}`}>{spikeConfig.label}</span>
            </div>
            <div className="h-2 rounded-full bg-sage-800 overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(result.effective_gl / 30 * 100, 100)}%` }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className={`h-full rounded-full ${
                  result.spike_level === 'low' ? 'bg-sage-500' :
                  result.spike_level === 'moderate' ? 'bg-honey-500' : 'bg-coral-500'
                }`}
              />
            </div>
            <span className="text-sm font-semibold text-sage-200">{result.effective_gl.toFixed(1)}</span>
          </div>
        </div>
        
        {/* Modifiers breakdown */}
        {result.total_reduction_percent > 0 && (
          <div className="mt-3 p-2 rounded-lg bg-sage-800/30 text-xs text-sage-300">
            <div className="flex items-center gap-1 mb-1">
              <Info className="w-3 h-3" />
              <span>Spike reduced by {result.total_reduction_percent.toFixed(0)}% due to:</span>
            </div>
            <div className="flex flex-wrap gap-2 mt-1">
              {result.fiber_modifier > 0 && (
                <span className="px-2 py-0.5 rounded bg-sage-700/50">
                  Fiber: -{(result.fiber_modifier * 100).toFixed(0)}%
                </span>
              )}
              {result.protein_modifier > 0 && (
                <span className="px-2 py-0.5 rounded bg-coral-700/30">
                  Protein: -{(result.protein_modifier * 100).toFixed(0)}%
                </span>
              )}
              {result.fat_modifier > 0 && (
                <span className="px-2 py-0.5 rounded bg-honey-700/30">
                  Fat: -{(result.fat_modifier * 100).toFixed(0)}%
                </span>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Recommendations */}
      <div className="px-4 py-3">
        <p className="text-xs text-sage-400 mb-2 uppercase tracking-wider">Recommendations</p>
        <ul className="space-y-1.5">
          {result.recommendations.map((rec, i) => (
            <li key={i} className="text-sm text-sage-200 leading-relaxed">
              {rec}
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  );
}

function NutrientPill({ 
  icon, 
  label, 
  value, 
  unit, 
  color 
}: { 
  icon: React.ReactNode;
  label: string; 
  value: number; 
  unit: string;
  color: string;
}) {
  return (
    <div className="text-center p-2 rounded-lg bg-sage-800/30">
      <div className={`flex justify-center mb-1 ${color}`}>{icon}</div>
      <div className="text-sm font-semibold text-sage-100">{value.toFixed(1)}{unit}</div>
      <div className="text-xs text-sage-400">{label}</div>
    </div>
  );
}

