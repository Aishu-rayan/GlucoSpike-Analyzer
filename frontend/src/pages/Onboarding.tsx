import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Salad, ArrowRight, ArrowLeft, Check, Loader2, Heart, Activity, Target } from 'lucide-react';
import { completeOnboarding } from '../api';
import { OnboardingData } from '../types';
import { useAuth } from '../context/AuthContext';

export function Onboarding() {
  const { refreshUser } = useAuth();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [data, setData] = useState<OnboardingData>({
    display_name: '',
    health_status: 'healthy',
    age: undefined,
    sex: undefined,
    goals: 'health',
    activity_level: 'moderate',
  });

  const healthOptions = [
    { value: 'healthy', label: 'Healthy', description: 'No diabetes or insulin resistance', icon: '💪' },
    { value: 'insulin_resistance', label: 'Insulin Resistance', description: 'Pre-diabetic or IR diagnosis', icon: '⚡' },
    { value: 'prediabetes', label: 'Prediabetes', description: 'Elevated blood sugar levels', icon: '📊' },
    { value: 'type2', label: 'Type 2 Diabetes', description: 'Diagnosed with Type 2', icon: '🩺' },
    { value: 'type1', label: 'Type 1 Diabetes', description: 'Diagnosed with Type 1', icon: '💉' },
  ];

  const goalOptions = [
    { value: 'weight_loss', label: 'Weight Loss', icon: <Target className="w-5 h-5" /> },
    { value: 'maintenance', label: 'Maintain Weight', icon: <Activity className="w-5 h-5" /> },
    { value: 'health', label: 'General Health', icon: <Heart className="w-5 h-5" /> },
    { value: 'diabetes_management', label: 'Manage Diabetes', icon: '🩺' },
  ];

  const activityOptions = [
    { value: 'sedentary', label: 'Sedentary', description: 'Little to no exercise' },
    { value: 'light', label: 'Light', description: '1-2 days/week' },
    { value: 'moderate', label: 'Moderate', description: '3-4 days/week' },
    { value: 'active', label: 'Active', description: '5-6 days/week' },
    { value: 'very_active', label: 'Very Active', description: 'Daily intense exercise' },
  ];

  const handleComplete = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      await completeOnboarding(data);
      await refreshUser();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile');
    } finally {
      setIsLoading(false);
    }
  };

  const totalSteps = 3;

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f1410] p-4">
      <div className="fixed inset-0 bg-gradient-to-br from-sage-900/20 via-transparent to-coral-900/10 pointer-events-none" />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-lg"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center mx-auto mb-4 shadow-xl">
            <Salad className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-sage-100">Let's personalize your experience</h1>
          <p className="text-sage-400 mt-1">This helps us give you better recommendations</p>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-6">
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all ${
                i + 1 <= step ? 'bg-sage-500 w-8' : 'bg-sage-800 w-4'
              }`}
            />
          ))}
        </div>

        {/* Form */}
        <div className="bg-sage-900/50 border border-sage-800/50 rounded-2xl p-6 backdrop-blur-lg">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 rounded-lg bg-coral-900/30 border border-coral-500/30 text-coral-200 text-sm"
            >
              {error}
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                <h2 className="text-lg font-semibold text-sage-100 mb-4">What's your health status?</h2>
                <div className="space-y-2">
                  {healthOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setData({ ...data, health_status: option.value as OnboardingData['health_status'] })}
                      className={`w-full p-4 rounded-xl border text-left transition-all flex items-center gap-3 ${
                        data.health_status === option.value
                          ? 'border-sage-500 bg-sage-800/50'
                          : 'border-sage-700/50 bg-sage-800/20 hover:border-sage-600/50'
                      }`}
                    >
                      <span className="text-2xl">{option.icon}</span>
                      <div>
                        <div className="font-medium text-sage-100">{option.label}</div>
                        <div className="text-sm text-sage-400">{option.description}</div>
                      </div>
                      {data.health_status === option.value && (
                        <Check className="w-5 h-5 text-sage-400 ml-auto" />
                      )}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                <h2 className="text-lg font-semibold text-sage-100 mb-4">What's your goal?</h2>
                <div className="grid grid-cols-2 gap-3">
                  {goalOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setData({ ...data, goals: option.value })}
                      className={`p-4 rounded-xl border text-center transition-all ${
                        data.goals === option.value
                          ? 'border-sage-500 bg-sage-800/50'
                          : 'border-sage-700/50 bg-sage-800/20 hover:border-sage-600/50'
                      }`}
                    >
                      <div className="flex justify-center mb-2 text-sage-300">
                        {typeof option.icon === 'string' ? <span className="text-2xl">{option.icon}</span> : option.icon}
                      </div>
                      <div className="font-medium text-sage-100 text-sm">{option.label}</div>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                <h2 className="text-lg font-semibold text-sage-100 mb-4">How active are you?</h2>
                <div className="space-y-2">
                  {activityOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setData({ ...data, activity_level: option.value })}
                      className={`w-full p-3 rounded-xl border text-left transition-all flex items-center justify-between ${
                        data.activity_level === option.value
                          ? 'border-sage-500 bg-sage-800/50'
                          : 'border-sage-700/50 bg-sage-800/20 hover:border-sage-600/50'
                      }`}
                    >
                      <div>
                        <div className="font-medium text-sage-100">{option.label}</div>
                        <div className="text-sm text-sage-400">{option.description}</div>
                      </div>
                      {data.activity_level === option.value && (
                        <Check className="w-5 h-5 text-sage-400" />
                      )}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6">
            {step > 1 ? (
              <button
                onClick={() => setStep(step - 1)}
                className="flex items-center gap-2 text-sage-400 hover:text-sage-200 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </button>
            ) : (
              <div />
            )}

            {step < totalSteps ? (
              <button
                onClick={() => setStep(step + 1)}
                className="flex items-center gap-2 px-6 py-2 rounded-xl bg-sage-700/50 text-sage-100 hover:bg-sage-600/50 transition-colors"
              >
                Next
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleComplete}
                disabled={isLoading}
                className="flex items-center gap-2 px-6 py-2 rounded-xl bg-gradient-to-r from-sage-600 to-sage-500 text-white hover:from-sage-500 hover:to-sage-400 transition-all disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    Get Started
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Skip */}
        <div className="text-center mt-4">
          <button
            onClick={handleComplete}
            className="text-sage-500 hover:text-sage-400 text-sm transition-colors"
          >
            Skip for now
          </button>
        </div>
      </motion.div>
    </div>
  );
}

