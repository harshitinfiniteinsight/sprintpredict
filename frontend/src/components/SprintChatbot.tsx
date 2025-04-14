
import React, { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, User, Bot } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface Message {
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

interface SprintChatbotProps {
  sprintName: string;
  sprintData: any;
}

const SprintChatbot = ({ sprintName, sprintData }: SprintChatbotProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      content: `Hi there! I'm your Sprint Assistant for ${sprintName}. How can I help you with this sprint?`,
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Simple Q&A function - in a real app this would use AI
  const getSprintResponse = (question: string) => {
    const lowerQuestion = question.toLowerCase();
    
    if (lowerQuestion.includes("goal") || lowerQuestion.includes("objective")) {
      return `The goal for ${sprintName} is to complete user authentication and profile features.`;
    } else if (lowerQuestion.includes("duration") || lowerQuestion.includes("how long")) {
      return `${sprintName} runs for 14 days.`;
    } else if (lowerQuestion.includes("points") || lowerQuestion.includes("story points")) {
      return `This sprint has ${sprintData?.totalPoints || 85} story points planned.`;
    } else if (lowerQuestion.includes("team") || lowerQuestion.includes("members")) {
      return `There are ${sprintData?.teamMembers || 7} team members assigned to this sprint.`;
    } else if (lowerQuestion.includes("tasks") || lowerQuestion.includes("backlog")) {
      return `There are ${sprintData?.totalTasks || 7} tasks planned for this sprint.`;
    } else if (lowerQuestion.includes("start") || lowerQuestion.includes("begin")) {
      return `${sprintName} starts on April 5, 2025.`;
    } else if (lowerQuestion.includes("end") || lowerQuestion.includes("finish")) {
      return `${sprintName} ends on April 18, 2025.`;
    } else if (lowerQuestion.includes("risk") || lowerQuestion.includes("risks")) {
      return `The risk level for this sprint is Medium.`;
    } else {
      return `I don't have specific information about that for ${sprintName}. Would you like to know about the sprint goals, duration, or team allocation instead?`;
    }
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    // Simulate bot response with a small delay
    setTimeout(() => {
      const botResponse: Message = {
        content: getSprintResponse(inputValue),
        sender: "bot",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, botResponse]);
    }, 500);
  };

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <Card className="border-t-4 border-t-primary shadow-lg">
      <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent">
        <CardTitle className="flex items-center">
          <Bot className="mr-2 text-primary" /> Sprint Assistant
          <Badge className="ml-2">{sprintName}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[300px] p-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex max-w-[80%] items-start gap-2 ${
                    message.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  } rounded-lg p-3`}
                >
                  {message.sender === "bot" && (
                    <Bot className="mt-0.5 h-5 w-5 shrink-0" />
                  )}
                  <div>
                    <div className="text-sm">{message.content}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </div>
                  {message.sender === "user" && (
                    <User className="mt-0.5 h-5 w-5 shrink-0" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
        <div className="p-4 border-t flex gap-2">
          <Input
            placeholder="Ask a question about this sprint..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
            className="flex-1"
          />
          <Button size="icon" onClick={handleSendMessage}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default SprintChatbot;
