import { useState, useEffect, useRef } from 'react';
import { Button, Input } from '../components/ui';
import api from '../lib/api';
import { MessageSquare, Plus, Send, CheckCircle2, Bot, User } from 'lucide-react';
import { cn } from '../lib/utils';

export default function ChatPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [activeConv, setActiveConv] = useState<any>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConv?.messages]);

  const fetchConversations = async () => {
    try {
      const { data } = await api.get('/conversations');
      setConversations(data.items || []);
    } catch (err) {
      console.error(err);
    }
  };

  const createConversation = async () => {
    try {
      const { data } = await api.post('/conversations', { title: "New Chat", mode: "chat" });
      setConversations(prev => [data, ...prev]);
      setActiveConv({ ...data, messages: [] });
    } catch (err) {
      console.error(err);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      const { data } = await api.get(`/conversations/${id}`);
      setActiveConv(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !activeConv) return;
    
    const userMsg = { role: 'user', content: message };
    setActiveConv((prev: any) => ({
      ...prev,
      messages: [...(prev.messages || []), userMsg]
    }));
    
    const currentMessage = message;
    setMessage('');
    setLoading(true);
    
    try {
      const { data } = await api.post(`/conversations/${activeConv.id}/messages`, { content: currentMessage });
      setActiveConv((prev: any) => ({
        ...prev,
        messages: [...(prev.messages || []), data]
      }));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar for Conversations */}
      <div className="w-80 border-r bg-muted/10 flex flex-col">
        <div className="p-4 border-b">
          <Button onClick={createConversation} className="w-full justify-start shadow-sm" variant="outline">
            <Plus className="w-4 h-4 mr-2" /> New Chat
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {conversations.length === 0 && (
            <p className="text-sm text-muted-foreground text-center mt-4">No previous chats.</p>
          )}
          {conversations.map(conv => (
            <button
              key={conv.id}
              onClick={() => loadConversation(conv.id)}
              className={cn(
                "w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-colors truncate",
                activeConv?.id === conv.id 
                  ? "bg-primary text-primary-foreground" 
                  : "hover:bg-muted text-foreground"
              )}
            >
              <MessageSquare className="w-4 h-4 inline-block mr-2 opacity-70" />
              {conv.title || 'Untitled Chat'}
            </button>
          ))}
        </div>
      </div>
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative bg-card">
        {!activeConv ? (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
            <MessageSquare className="w-16 h-16 mb-4 opacity-20" />
            <p className="text-lg font-medium">Select or start a new chat</p>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {activeConv.messages?.length === 0 && (
                <div className="text-center text-muted-foreground mt-10">
                  <p>Start a conversation. The Copilot will search your library for context.</p>
                </div>
              )}
              {activeConv.messages?.map((msg: any, idx: number) => (
                <div key={idx} className={cn("flex space-x-4 max-w-4xl mx-auto", msg.role === 'user' ? "justify-end" : "justify-start")}>
                  {msg.role !== 'user' && (
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-primary" />
                    </div>
                  )}
                  
                  <div className={cn(
                    "rounded-2xl px-6 py-4 max-w-[80%] shadow-sm",
                    msg.role === 'user' ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
                  )}>
                    <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                      {msg.content}
                    </div>
                    {msg.role === 'assistant' && msg.confidence && (
                      <div className="mt-3 pt-3 border-t border-border/50 flex items-center justify-between text-xs text-muted-foreground">
                        <span className="flex items-center">
                          <CheckCircle2 className="w-3 h-3 mr-1 text-green-500" />
                          Confidence: {(msg.confidence * 100).toFixed(0)}%
                        </span>
                        {msg.agent_trace && (
                          <span>Iterations: {msg.agent_trace.iterations || 1}</span>
                        )}
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex justify-start space-x-4 max-w-4xl mx-auto">
                   <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-primary animate-pulse" />
                   </div>
                   <div className="bg-muted text-muted-foreground rounded-2xl px-6 py-4 shadow-sm animate-pulse">
                     Thinking...
                   </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="p-4 bg-background border-t">
              <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-center">
                <Input 
                  value={message} 
                  onChange={(e) => setMessage(e.target.value)} 
                  placeholder="Ask a question..." 
                  className="pr-12 py-6 rounded-2xl text-base shadow-sm border-muted-foreground/20 focus-visible:ring-primary"
                />
                <Button 
                  type="submit" 
                  disabled={loading || !message.trim()} 
                  
                  className="absolute right-2 rounded-xl h-10 w-10"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
