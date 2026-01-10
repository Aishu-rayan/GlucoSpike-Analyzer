import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  MessageSquare, 
  Search, 
  Trash2, 
  Edit2, 
  Check, 
  X, 
  LogOut, 
  ChevronLeft,
  ChevronRight,
  User
} from 'lucide-react';
import { ChatSummary } from '../types';
import { listChats, createChat, deleteChat, updateChat } from '../api';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
  currentChatId: number | null;
  onSelectChat: (chatId: number) => void;
  onNewChat: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  refreshCounter?: number;
}

export function Sidebar({ 
  currentChatId, 
  onSelectChat, 
  onNewChat,
  isCollapsed,
  onToggleCollapse,
  refreshCounter = 0
}: SidebarProps) {
  const { user, logout } = useAuth();
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadChats();
  }, [refreshCounter]);

  const loadChats = async () => {
    setIsLoading(true);
    try {
      const data = await listChats(searchQuery || undefined);
      setChats(data);
    } catch (err) {
      console.error('Failed to load chats:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const debounce = setTimeout(() => {
      loadChats();
    }, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery]);

  const handleNewChat = async () => {
    try {
      const newChat = await createChat();
      setChats([newChat, ...chats]);
      onNewChat();
      onSelectChat(newChat.id);
    } catch (err) {
      console.error('Failed to create chat:', err);
    }
  };

  const handleDelete = async (chatId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this chat?')) return;
    
    try {
      await deleteChat(chatId);
      setChats(chats.filter(c => c.id !== chatId));
      if (currentChatId === chatId) {
        onNewChat();
      }
    } catch (err) {
      console.error('Failed to delete chat:', err);
    }
  };

  const handleStartEdit = (chat: ChatSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(chat.id);
    setEditTitle(chat.title);
  };

  const handleSaveEdit = async (chatId: number) => {
    try {
      await updateChat(chatId, editTitle);
      setChats(chats.map(c => 
        c.id === chatId ? { ...c, title: editTitle } : c
      ));
      setEditingId(null);
    } catch (err) {
      console.error('Failed to update chat:', err);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  if (isCollapsed) {
    return (
      <div className="w-16 h-full bg-sage-900/80 border-r border-sage-800/50 flex flex-col items-center py-4">
        <button
          onClick={onToggleCollapse}
          className="p-2 rounded-lg hover:bg-sage-800/50 text-sage-400 hover:text-sage-200 mb-4"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
        
        <button
          onClick={handleNewChat}
          className="p-3 rounded-xl bg-sage-700/50 text-sage-200 hover:bg-sage-600/50 mb-4"
        >
          <Plus className="w-5 h-5" />
        </button>
        
        <div className="flex-1 overflow-y-auto w-full px-2">
          {chats.slice(0, 10).map((chat) => (
            <button
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={`w-full p-3 rounded-xl mb-1 transition-colors ${
                currentChatId === chat.id
                  ? 'bg-sage-700/50 text-sage-100'
                  : 'text-sage-400 hover:bg-sage-800/50 hover:text-sage-200'
              }`}
            >
              <MessageSquare className="w-5 h-5 mx-auto" />
            </button>
          ))}
        </div>
        
        <button
          onClick={handleLogout}
          className="p-3 rounded-xl text-sage-400 hover:bg-sage-800/50 hover:text-sage-200"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    );
  }

  return (
    <div className="w-72 h-full bg-sage-900/80 border-r border-sage-800/50 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-sage-800/50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-sage-700/50 flex items-center justify-center">
              <User className="w-4 h-4 text-sage-300" />
            </div>
            <span className="text-sage-200 font-medium text-sm truncate max-w-[120px]">
              {user?.username}
            </span>
          </div>
          <button
            onClick={onToggleCollapse}
            className="p-2 rounded-lg hover:bg-sage-800/50 text-sage-400 hover:text-sage-200"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>
        
        <button
          onClick={handleNewChat}
          className="w-full py-2.5 rounded-xl bg-gradient-to-r from-sage-600 to-sage-500 text-white font-medium hover:from-sage-500 hover:to-sage-400 transition-all flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Search */}
      <div className="p-3 border-b border-sage-800/30">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-sage-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search chats..."
            className="w-full pl-9 pr-3 py-2 rounded-lg bg-sage-800/30 border border-sage-700/30 text-sage-200 placeholder-sage-500 text-sm focus:outline-none focus:ring-1 focus:ring-sage-500/50"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <div className="text-center py-8 text-sage-500 text-sm">Loading...</div>
        ) : chats.length === 0 ? (
          <div className="text-center py-8 text-sage-500 text-sm">
            {searchQuery ? 'No chats found' : 'No chats yet'}
          </div>
        ) : (
          <AnimatePresence>
            {chats.map((chat) => (
              <motion.div
                key={chat.id}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                onClick={() => onSelectChat(chat.id)}
                className={`group p-3 rounded-xl mb-1 cursor-pointer transition-all ${
                  currentChatId === chat.id
                    ? 'bg-sage-700/50'
                    : 'hover:bg-sage-800/50'
                }`}
              >
                {editingId === chat.id ? (
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="flex-1 px-2 py-1 rounded bg-sage-800 border border-sage-600 text-sage-200 text-sm focus:outline-none"
                      autoFocus
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveEdit(chat.id);
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                    />
                    <button
                      onClick={() => handleSaveEdit(chat.id)}
                      className="p-1 text-sage-400 hover:text-sage-200"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="p-1 text-sage-400 hover:text-sage-200"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div className="flex items-start gap-3">
                    <MessageSquare className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                      currentChatId === chat.id ? 'text-sage-300' : 'text-sage-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className={`text-sm font-medium truncate ${
                        currentChatId === chat.id ? 'text-sage-100' : 'text-sage-300'
                      }`}>
                        {chat.title}
                      </div>
                      {chat.last_message_preview && (
                        <div className="text-xs text-sage-500 truncate mt-0.5">
                          {chat.last_message_preview}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleStartEdit(chat, e)}
                        className="p-1 text-sage-500 hover:text-sage-300"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(chat.id, e)}
                        className="p-1 text-sage-500 hover:text-coral-400"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-sage-800/50">
        <button
          onClick={handleLogout}
          className="w-full py-2 rounded-lg text-sage-400 hover:bg-sage-800/50 hover:text-sage-200 text-sm flex items-center justify-center gap-2 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </div>
  );
}

