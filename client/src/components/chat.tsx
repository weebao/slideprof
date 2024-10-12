import React, { useState, useRef, useEffect } from "react";
import { Send, Mic } from "lucide-react";
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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      const scrollHeight = chatContainerRef.current.scrollHeight;
      const height = chatContainerRef.current.clientHeight;
      const maxScrollTop = scrollHeight - height;
      chatContainerRef.current.scrollTop = maxScrollTop > 0 ? maxScrollTop : 0;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      const newMessage: Message = { text: inputText, isUser: true, timestamp: new Date() };
      setMessages((prev) => [...prev, newMessage]);
      setInputText("");
      setIsLoading(true);

      // Simulate bot response after 5 seconds
      setTimeout(() => {
        const botMessage: Message = { text: "What's up?", isUser: false, timestamp: new Date() };
        setMessages((prev) => [...prev, botMessage]);
        setIsLoading(false);
      }, 5000);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="flex flex-col bg-white">
      <div className="flex-1 overflow-hidden flex flex-col justify-end">
        <div ref={chatContainerRef} className="overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.isUser ? "justify-end" : "justify-start"} transition-all duration-300 ease-in-out`}>
              <div className={`max-w-[70%] rounded-lg p-3 ${message.isUser ? "bg-black text-white" : "bg-white text-gray-800"}`}>
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
      </div>
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t">
        <div className="flex space-x-2">
          <Button type="button" size="icon" variant="outline">
            <Mic className="h-4 w-4" />
            <span className="sr-only">Voice input</span>
          </Button>
          <Input type="text" placeholder="Type a message..." value={inputText} onChange={(e) => setInputText(e.target.value)} className="flex-1" />
          <Button type="submit" size="icon">
            <Send className="h-4 w-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </div>
      </form>
    </div>
  );
};
