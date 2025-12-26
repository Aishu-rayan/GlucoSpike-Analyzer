import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Camera, Image, X, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string, image?: File) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, isLoading, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const clearImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if ((!message.trim() && !selectedImage) || isLoading || disabled) return;
    
    const messageToSend = message.trim() || (selectedImage ? 'Analyze this food' : '');
    onSendMessage(messageToSend, selectedImage || undefined);
    
    setMessage('');
    clearImage();
  };
  
  return (
    <div className="border-t border-sage-800/50 bg-sage-900/80 backdrop-blur-lg">
      {/* Image preview */}
      <AnimatePresence>
        {imagePreview && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="px-4 pt-3"
          >
            <div className="relative inline-block">
              <img 
                src={imagePreview} 
                alt="Preview" 
                className="h-20 rounded-lg border border-sage-700/50"
              />
              <button
                onClick={clearImage}
                className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-coral-600 text-white flex items-center justify-center hover:bg-coral-500 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex items-end gap-2">
          {/* Image upload buttons */}
          <div className="flex gap-1">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="hidden"
              id="image-upload"
            />
            <label
              htmlFor="image-upload"
              className="p-3 rounded-xl bg-sage-800/50 text-sage-300 hover:bg-sage-700/50 hover:text-sage-100 transition-all cursor-pointer border border-sage-700/30"
            >
              <Image className="w-5 h-5" />
            </label>
            <label
              htmlFor="image-upload"
              className="p-3 rounded-xl bg-sage-800/50 text-sage-300 hover:bg-sage-700/50 hover:text-sage-100 transition-all cursor-pointer border border-sage-700/30"
            >
              <Camera className="w-5 h-5" />
            </label>
          </div>
          
          {/* Text input */}
          <div className="flex-1 relative">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder={selectedImage ? "Add a message (optional)..." : "Upload a food photo or ask a question..."}
              disabled={isLoading || disabled}
              rows={1}
              className="w-full px-4 py-3 rounded-xl bg-sage-800/50 border border-sage-700/30 text-sage-100 placeholder-sage-500 resize-none focus:outline-none focus:ring-2 focus:ring-sage-500/50 focus:border-transparent disabled:opacity-50 transition-all"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
          </div>
          
          {/* Send button */}
          <button
            type="submit"
            disabled={(!message.trim() && !selectedImage) || isLoading || disabled}
            className="p-3 rounded-xl bg-gradient-to-r from-sage-600 to-sage-500 text-white hover:from-sage-500 hover:to-sage-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg glow-sage"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        
        {/* Hint text */}
        <p className="text-xs text-sage-500 mt-2 text-center">
          📸 Upload a food photo to analyze its insulin spike potential
        </p>
      </form>
    </div>
  );
}

