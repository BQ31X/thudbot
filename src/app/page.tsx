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
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-xl p-6">
          <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
            🍺 Thudbot: Your Agentic Companion for The Space Bar
          </h1>
          
          {/* API Key Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              OpenAI API Key <span className="text-gray-500 font-normal">(optional)</span>
            </label>
                               <input
                     type="password"
                     value={apiKey}
                     onChange={(e) => setApiKey(e.target.value)}
                     placeholder="Enter your OpenAI API key (not needed if set in .env)"
                     className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                   />
          </div>

          {/* Messages Display */}
          <div className="h-[400px] overflow-y-auto mb-6 p-4 bg-gray-50 rounded-lg border">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-20">
                <p className="text-lg">👋 Hi. I'm Thud. I am at The Thirsty Tentacle waiting for my shuttle.</p>
                <p className="mt-2">Need help with The Space Bar? Ask me a question!</p>
              </div>
            )}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-4 p-4 rounded-lg max-w-[80%] ${
                  message.role === 'user'
                    ? 'bg-blue-100 ml-auto border-l-4 border-blue-500'
                    : message.role === 'error'
                    ? 'bg-red-100 border-l-4 border-red-500'
                    : 'bg-green-100 border-l-4 border-green-500'
                }`}
              >
                <p className="text-sm font-semibold mb-2 text-gray-700">
                  {message.role === 'user' ? '🤔 You' : message.role === 'error' ? '❌ Error' : '🍺 Thud'}
                </p>
                <p className="whitespace-pre-wrap text-gray-800">{message.content}</p>
              </div>
            ))}
            {isLoading && (
              <div className="text-center text-gray-500 p-4">
                <p className="flex items-center justify-center">
                  <span className="animate-spin mr-2">🍺</span>
                  Thud is thinking...
                </p>
              </div>
            )}
            {/* Invisible element to scroll to */}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Thud about The Space Bar..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
            >
              Send
            </button>
          </form>

          {/* Instructions */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="font-semibold text-yellow-800 mb-2">💡 How to chat with Thud:</h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Ask about puzzles: "How do I get the token from the cup?"</li>
              <li>• Get general game help: "How do I use the voice printer"</li>
              <li>• Talk about the weather: "What's the weather in Boston?"</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  );
}