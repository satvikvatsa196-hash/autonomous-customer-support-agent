import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Loader2, Bot, User } from 'lucide-react';

// For demo purposes, we generate a random session ID or just hardcode one
const SESSION_ID = 12345;

interface ChatMessage {
  id: string;
  role: 'human' | 'ai';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'human',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/chat', {
        session_id: SESSION_ID,
        message: userMessage.content,
      });

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: response.data.reply,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: 'Sorry, I encountered an error connecting to the FastAPI backend. Please make sure the server is running on port 8000.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans">
      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2.5 rounded-xl shadow-md">
            <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
            <h1 className="text-xl font-bold text-gray-800 tracking-tight">Support Agent</h1>
            <p className="text-xs font-medium text-green-500 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                Online
            </p>
            </div>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-4 sm:p-6 w-full max-w-4xl mx-auto flex flex-col gap-6">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center px-4 animate-in fade-in duration-500">
            <div className="bg-blue-100 p-5 rounded-full mb-6 ring-8 ring-white shadow-sm">
              <Bot className="w-14 h-14 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3 tracking-tight">How can I help you today?</h2>
            <p className="text-gray-500 max-w-md text-base leading-relaxed">
              I can help you check shipping status, process refunds, find your orders, or answer policy questions.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'human' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
            >
              <div
                className={`flex gap-3 max-w-[85%] sm:max-w-[75%] ${
                  msg.role === 'human' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${
                    msg.role === 'human' ? 'bg-indigo-600' : 'bg-blue-600'
                  }`}
                >
                  {msg.role === 'human' ? (
                    <User className="w-5 h-5 text-white" />
                  ) : (
                    <Bot className="w-5 h-5 text-white" />
                  )}
                </div>
                <div
                  className={`py-3.5 px-5 rounded-2xl shadow-sm ${
                    msg.role === 'human'
                      ? 'bg-indigo-600 text-white rounded-tr-sm'
                      : 'bg-white text-gray-800 border border-gray-100 rounded-tl-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.content}</p>
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start animate-in fade-in duration-300">
            <div className="flex gap-3 max-w-[85%] flex-row">
              <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0 shadow-sm">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="py-3 px-5 rounded-2xl bg-white border border-gray-100 rounded-tl-sm shadow-sm flex items-center gap-3">
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                <span className="text-gray-500 text-sm font-medium">Agent is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t p-4 sm:p-6 pb-6">
        <form
          onSubmit={handleSubmit}
          className="max-w-4xl mx-auto relative flex items-center group"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            className="w-full py-4 pl-6 pr-16 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-inner text-[15px]"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-full transition-all duration-200 hover:scale-105 active:scale-95 shadow-md disabled:shadow-none"
          >
            <Send className="w-5 h-5 ml-0.5" />
          </button>
        </form>
        <div className="text-center mt-3">
          <p className="text-xs text-gray-400 font-medium tracking-wide">
            Powered by FastAPI, LangGraph & React
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
