import { useState, useRef, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Header, ChatMessage, ChatInput, WelcomeScreen, LoadingMessage, Sidebar } from './components';
import { Message, ChatMessage as APIChatMessage } from './types';
import { analyzeImage, chat, getChat, addMessage, uploadImage, getImageUrl, createChat } from './api';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login, Register, Onboarding } from './pages';

function AppContent() {
  const { user, isLoading: authLoading, isAuthenticated } = useAuth();
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);
  const [chatListRefreshCounter, setChatListRefreshCounter] = useState(0);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const skipNextChatLoadRef = useRef(false);
  
  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load chat when selected
  useEffect(() => {
    if (currentChatId && !skipNextChatLoadRef.current) {
      loadChat(currentChatId);
    }
    skipNextChatLoadRef.current = false;
  }, [currentChatId]);

  const loadChat = async (chatId: number) => {
    try {
      const chatData = await getChat(chatId);
      const loadedMessages: Message[] = chatData.messages.map((msg: APIChatMessage) => ({
        id: msg.id.toString(),
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.created_at),
        image: msg.attachments.length > 0 ? getImageUrl(msg.attachments[0].file_path) : undefined,
        eglResult: msg.egl_result_json ? JSON.parse(msg.egl_result_json) : undefined,
        foodAnalysis: msg.food_analysis_json ? JSON.parse(msg.food_analysis_json) : undefined,
      }));
      setMessages(loadedMessages);
    } catch (err) {
      console.error('Failed to load chat:', err);
    }
  };

  const handleSendMessage = async (content: string, image?: File) => {
    setError(null);
    
    let ensuredChatId = currentChatId;
    if (!ensuredChatId && isAuthenticated) {
      const newChat = await createChat();
      ensuredChatId = newChat.id;
      skipNextChatLoadRef.current = true;
      setCurrentChatId(newChat.id);
      setChatListRefreshCounter((c) => c + 1);
    }
    
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
      
      // If we have a current chat and are authenticated, save to history
      if (ensuredChatId && isAuthenticated) {
        if (image) {
          // Upload image to chat
          await uploadImage(ensuredChatId, image, content);
        } else {
          // Add text message to chat
          await addMessage(ensuredChatId, 'user', content);
        }
      }
      
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
      
      // Save assistant response to chat history
      if (ensuredChatId && isAuthenticated) {
        await addMessage(
          ensuredChatId,
          'assistant',
          response.response,
          response.egl_result ? JSON.stringify(response.egl_result) : undefined,
          response.food_analysis ? JSON.stringify(response.food_analysis) : undefined
        );
      }
      
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

  const handleSelectChat = (chatId: number) => {
    setCurrentChatId(chatId);
  };

  const handleNewChat = () => {
    setCurrentChatId(null);
    setMessages([]);
  };

  // Auth loading state
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f1410]">
        <div className="text-sage-400">Loading...</div>
      </div>
    );
  }

  // Not authenticated - show login/register
  if (!isAuthenticated) {
    if (authMode === 'login') {
      return <Login onSwitchToRegister={() => setAuthMode('register')} />;
    }
    return <Register onSwitchToLogin={() => setAuthMode('login')} />;
  }

  // Need onboarding
  if (user && !user.onboarding_completed) {
    return <Onboarding />;
  }

  // Main app
  return (
    <div className="min-h-screen flex bg-[#0f1410]">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-sage-900/20 via-transparent to-coral-900/10 pointer-events-none" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-sage-800/10 via-transparent to-transparent pointer-events-none" />
      
      {/* Sidebar */}
      <Sidebar
        currentChatId={currentChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        refreshCounter={chatListRefreshCounter}
      />
      
      {/* Main content */}
      <div className="flex-1 flex flex-col relative">
        <Header />
        
        <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full pt-20">
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
              {error}
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
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
