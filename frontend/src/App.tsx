import { useState, useRef, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Header, ChatMessage, ChatInput, WelcomeScreen, LoadingMessage } from './components';
import { Message } from './types';
import { analyzeImage, chat } from './api';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = async (content: string, image?: File) => {
    setError(null);
    
    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    
    // If there's an image, create a preview URL
    if (image) {
      const reader = new FileReader();
      reader.onload = () => {
        userMessage.image = reader.result as string;
        setMessages(prev => [...prev, userMessage]);
      };
      reader.readAsDataURL(image);
    } else {
      setMessages(prev => [...prev, userMessage]);
    }
    
    setIsLoading(true);
    
    try {
      let response;
      
      if (image) {
        // Analyze image
        response = await analyzeImage(image, content);
      } else {
        // Regular chat
        response = await chat(content);
      }
      
      // Create assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        foodAnalysis: response.food_analysis || undefined,
        eglResult: response.egl_result || undefined,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Something went wrong';
      setError(errorMessage);
      
      // Add error message to chat
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${errorMessage}. Please make sure the backend server is running and try again.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSampleQuery = (query: string) => {
    handleSendMessage(query);
  };
  
  return (
    <div className="min-h-screen flex flex-col bg-[#0f1410]">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-sage-900/20 via-transparent to-coral-900/10 pointer-events-none" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-sage-800/10 via-transparent to-transparent pointer-events-none" />
      
      <Header />
      
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full pt-20 relative">
        {messages.length === 0 ? (
          <WelcomeScreen onSampleQuery={handleSampleQuery} />
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </AnimatePresence>
            
            {isLoading && <LoadingMessage />}
            
            <div ref={messagesEndRef} />
          </div>
        )}
        
        {/* Error banner */}
        {error && (
          <div className="mx-4 mb-2 p-3 rounded-lg bg-coral-900/30 border border-coral-500/30 text-coral-200 text-sm">
            ⚠️ {error}
          </div>
        )}
        
        <ChatInput 
          onSendMessage={handleSendMessage} 
          isLoading={isLoading}
        />
      </main>
      
      {/* Footer hint */}
      <footer className="text-center py-2 text-xs text-sage-600">
        GlucoGuide analyzes food for educational purposes only. Not medical advice.
      </footer>
    </div>
  );
}

export default App;

