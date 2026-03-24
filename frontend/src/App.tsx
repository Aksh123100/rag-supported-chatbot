import { useState, useRef, useEffect } from 'react';
import { Message, chatApi, SourceDocument } from './services/api';
import { ChatInput, ChatMessage, SourceCard } from './components';

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<SourceDocument[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    setError(null);

    // Add user message
    const userMessage: Message = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Get conversation history (last 10 messages)
      const conversationHistory = messages.slice(-10);

      // Send request
      const response = await chatApi.sendMessage({
        query: content,
        conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined,
        top_k: 5,
      });

      // Add assistant message
      const assistantMessage: Message = { role: 'assistant', content: response.response };
      setMessages((prev) => [...prev, assistantMessage]);
      setSources(response.sources);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to get response. Please try again.');

      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setSources([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
              <span className="text-white text-xl">💬</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Support Chatbot</h1>
              <p className="text-sm text-gray-500">Powered by RAG + OpenAI</p>
            </div>
          </div>
          <button
            onClick={handleClearChat}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Clear Chat
          </button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto flex">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col h-[calc(100vh-73px)]">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">👋</span>
                </div>
                <h2 className="text-xl font-semibold text-gray-800 mb-2">
                  Welcome! How can I help you?
                </h2>
                <p className="text-gray-500 max-w-md mx-auto">
                  Ask me anything about orders, returns, shipping, payments, and more.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {['What is the return policy?', 'How do I track my order?', 'Payment methods?'].map(
                    (suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => handleSendMessage(suggestion)}
                        className="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-600 hover:bg-gray-50 hover:border-primary-300 transition-colors"
                      >
                        {suggestion}
                      </button>
                    )
                  )}
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}

            {isLoading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                  <span className="text-white text-sm">🤖</span>
                </div>
                <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-tl-sm">
                  <div className="flex items-center gap-2 text-gray-500">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 bg-white border-t border-gray-200">
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
          </div>
        </div>

        {/* Sources Sidebar */}
        <div className="w-80 border-l border-gray-200 bg-white hidden lg:block">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Sources</h3>
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              {showSources ? 'Hide' : 'Show'}
            </button>
          </div>
          <div className="p-4 space-y-3 overflow-y-auto h-[calc(100vh-120px)]">
            {sources.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-8">
                Sources will appear here when you ask a question.
              </p>
            ) : (
              sources.map((source, index) => (
                <SourceCard key={index} source={source} index={index} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}