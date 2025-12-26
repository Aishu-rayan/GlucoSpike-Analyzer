import { Salad, Sparkles } from 'lucide-react';

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-sage-800/30">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center shadow-lg glow-sage">
            <Salad className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-sage-100 flex items-center gap-2">
              GlucoGuide
              <Sparkles className="w-4 h-4 text-honey-400" />
            </h1>
            <p className="text-xs text-sage-400">Insulin Spike Analyzer</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 text-xs font-medium rounded-full bg-sage-800/50 text-sage-300 border border-sage-700/50">
            AI-Powered
          </span>
        </div>
      </div>
    </header>
  );
}

