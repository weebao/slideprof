import React, { useState, useRef, useEffect } from "react";
import { Send, Mic, MessageCircle, Minus } from "lucide-react"; // Added Minus for minimize icon
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false); // Control chat box visibility
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const chatBoxRef = useRef<HTMLDivElement>(null); // Ref for detecting outside clicks

  // Scroll to the bottom of the chat when a new message is added
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to handle clicks outside of the chat box
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (chatBoxRef.current && !chatBoxRef.current.contains(event.target as Node)) {
        setIsChatOpen(false); // Collapse chat box if clicked outside
      }
    }

    if (isChatOpen) {
      document.addEventListener("mousedown", handleClickOutside); // Listen for clicks
    } else {
      document.removeEventListener("mousedown", handleClickOutside); // Remove listener
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside); // Cleanup
    };
  }, [isChatOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      const newMessage: Message = { text: inputText, isUser: true, timestamp: new Date() };
      setMessages((prev) => [...prev, newMessage]);
      setInputText("");
      setIsLoading(true);

      // Simulate bot response after 2 seconds
      setTimeout(() => {
        const botMessage: Message = { text: "What's up?", isUser: false, timestamp: new Date() };
        setMessages((prev) => [...prev, botMessage]);
        setIsLoading(false);
      }, 2000);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="relative">
      {/* Chat Toggle Button (Chat Bubble Icon) */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="fixed bottom-4 right-4 w-16 h-16 rounded-full bg-blue-500 text-white flex items-center justify-center shadow-lg"
      >
        <MessageCircle className="h-8 w-8" />
      </button>

      {/* Chat Box */}
      <div
        ref={chatBoxRef} // Ref for detecting clicks outside
        className={`fixed bottom-4 right-4 w-80 h-96 bg-white border rounded-lg shadow-lg transform transition-transform duration-300 ease-in-out ${
          isChatOpen ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0 pointer-events-none"
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Chat Box Header with Minimize Button */}
          <div className="p-2 bg-gray-200 border-b flex items-center justify-between">
            <span className="text-gray-700 font-semibold">Chat</span>
            <button onClick={() => setIsChatOpen(false)} className="text-gray-500 hover:text-gray-700">
              <Minus className="h-6 w-6" />
              <span className="sr-only">Minimize</span>
            </button>
          </div>

          {/* Chat messages container */}
          <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.isUser ? "justify-end" : "justify-start"} transition-all duration-300 ease-in-out`}>
                <div className={`max-w-[70%] rounded-lg p-3 ${message.isUser ? "bg-black text-white" : "bg-white text-gray-800 border"}`}>
                  <p>{message.text}</p>
                  <p className={`text-xs mt-1 ${message.isUser ? "text-white/70" : "text-gray-500"}`}>{formatTime(message.timestamp)}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 rounded-lg p-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Message input field */}
          <form onSubmit={handleSubmit} className="p-4 bg-gray-100 border-t">
            <div className="flex space-x-2">
              <Button type="button" size="icon" variant="outline">
                <Mic className="h-4 w-4" />
                <span className="sr-only">Voice input</span>
              </Button>
              <Input
                type="text"
                placeholder="Type a message..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" size="icon">
                <Send className="h-4 w-4" />
                <span className="sr-only">Send message</span>
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};