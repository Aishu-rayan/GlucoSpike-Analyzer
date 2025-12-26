import { motion } from 'framer-motion';
import { User, Bot } from 'lucide-react';
import { Message } from '../types';
import { EGLResultCard } from './EGLResultCard';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center ${
        isUser 
          ? 'bg-gradient-to-br from-coral-500 to-coral-600' 
          : 'bg-gradient-to-br from-sage-500 to-sage-600'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>
      
      {/* Content */}
      <div className={`flex-1 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Image preview for user messages */}
        {message.image && (
          <div className="mb-3">
            <img 
              src={message.image} 
              alt="Food" 
              className="max-w-xs rounded-xl border border-sage-700/50 shadow-lg"
            />
          </div>
        )}
        
        {/* Text content */}
        <div className={`rounded-2xl px-4 py-3 ${
          isUser 
            ? 'bg-coral-600/20 border border-coral-500/30 text-coral-50' 
            : 'bg-sage-800/50 border border-sage-700/30 text-sage-100'
        }`}>
          <div className="chat-content whitespace-pre-wrap text-sm leading-relaxed">
            {formatMessage(message.content)}
          </div>
        </div>
        
        {/* eGL Result Card */}
        {message.eglResult && (
          <div className="mt-3">
            <EGLResultCard result={message.eglResult} />
          </div>
        )}
        
        {/* Timestamp */}
        <p className={`text-xs text-sage-500 mt-1 ${isUser ? 'text-right' : ''}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </motion.div>
  );
}

function formatMessage(content: string): React.ReactNode {
  // Simple markdown-like formatting
  const parts = content.split(/(\*\*.*?\*\*|\*.*?\*)/g);
  
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={i}>{part.slice(1, -1)}</em>;
    }
    return part;
  });
}

