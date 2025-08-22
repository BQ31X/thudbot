'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Chat with Thudbot
      const response = await axios.post('/api/chat', {
        user_message: userMessage,
        api_key: apiKey
      }, {
        responseType: 'json'
      });

      setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'An error occurred while fetching the response.';
      setMessages(prev => [...prev, { role: 'error', content: errorMessage }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      {/* PDA Interface Container */}
      <div className="relative w-full max-w-[1623px]">
        {/* PDA Background Image */}
        <img 
          src="/PDA-interface150.png" 
          alt="PDA Interface" 
          className="block w-full h-auto"
        />
        
        {/* Main Screen Area - Chat Interface */}
        <div 
          className="absolute bg-black overflow-hidden"
          style={{ 
            left: '20.08%', 
            top: '17.5%', 
            width: '48.7%', 
            height: '54.2%',
            borderRadius: '0.25%'
          }}
        >
          {/* Messages Display */}
          <div className="h-full overflow-y-auto p-[1%] bg-gray-900 text-green-400 font-mono text-[0.9vw]">
            {messages.length === 0 && (
              <div className="text-center text-green-300 mt-32">
                <p className="text-base">👋 Zelda here. Ready to assist with The Space Bar.</p>
                <p className="mt-2 text-sm">Ask me anything about the game!</p>
              </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-3 p-2 rounded max-w-[90%] text-sm ${
                  message.role === 'user'
                    ? 'bg-blue-900 ml-auto border-l-2 border-blue-400 text-blue-100'
                    : message.role === 'error'
                    ? 'bg-red-900 border-l-2 border-red-400 text-red-100'
                    : 'bg-green-900 border-l-2 border-green-400 text-green-100'
                }`}
              >
                <p className="text-xs font-semibold mb-1 opacity-80">
                  {message.role === 'user' ? '> USER' : message.role === 'error' ? '> ERROR' : '> ZELDA'}
                </p>
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
            ))}
            {isLoading && (
              <div className="text-center text-green-300 p-3">
                <p className="flex items-center justify-center text-sm">
                  <span className="animate-spin mr-2">⚙</span>
                  Processing request...
                </p>
              </div>
            )}
            {/* Invisible element to scroll to */}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Small Status Screen Area */}
        <div 
          className="absolute bg-black overflow-hidden"
          style={{ 
            left: '75.0%', 
            top: '26%', 
            width: '17.8%', 
            height: '16.8%',
            borderRadius: '0.12%'
          }}
        >
          <div className="h-full p-[1%] bg-gray-900 text-green-400 font-mono text-[0.9vw]">
            <div className="text-left">
              <p className="font-bold mb-2">💡 How to chat with Zelda:</p>
              <p className="text-[0.8vw] mb-1">• "How do I get a token for the bus?"</p>
              <p className="text-[0.8vw] mb-1">• "How do I use the voice printer?"</p>
              <p className="text-[0.8vw]">• Ask about puzzles & locations</p>
            </div>
          </div>
        </div>

        {/* Input Area - Positioned over first 4 buttons */}
        <div 
          className="absolute"
          style={{ 
            left: '20.6%', 
            bottom: '12.6%', 
            width: '38.3%',
          }}
        >
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Zelda about The Space Bar..."
              className="w-full p-[1%] bg-gray-800 text-green-400 border border-green-600 rounded text-[0.9vw] font-mono focus:ring-1 focus:ring-green-500 focus:border-green-500"
              disabled={isLoading}
            />
          </form>
        </div>

        {/* Send Button - Positioned independently over LOG button */}
        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className="absolute bg-green-700 text-green-100 rounded hover:bg-green-600 disabled:bg-gray-600 transition-colors font-mono text-[0.9vw]"
          style={{
            left: '60.3%',
            bottom: '12.6%',
            width: '5.5%',
            height: '5.3%'
          }}
        >
          SEND
        </button>
      </div>
    </main>
  );
}