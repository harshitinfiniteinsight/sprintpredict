import React, { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area"; // Assuming this is from Shadcn UI/Radix UI
import { Send, User, Bot, MessageCircle, Loader } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import axios from "axios";

interface Message {
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

interface SprintChatbotProps {
  sprintName: string;
  sprintData: any; // Consider defining a more specific type for sprintData
  setSprintAssignment: (assignment: any) => void; // Add setSprintAssignment to props
  setTotalStoryPoint: (assignment: any) => void; 
  setTotalTasks: (assignment: any) => void; 
  setRiskCategory:(assignment: any) => void; 
  forecastedVelocity:any
}

const SprintChatbot = ({ sprintName, sprintData, setSprintAssignment,setTotalStoryPoint, setTotalTasks,setRiskCategory,forecastedVelocity}: SprintChatbotProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      content: `Hi there! I'm your Sprint Assistant for ${sprintName}. How can I help you with this sprint?`,
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isChatOpen, setIsChatOpen] = useState(false); // State to toggle chat window
  const [isThinking, setIsThinking] = useState(false); // State to show thinking animation
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Simple Q&A function - in a real app this would use AI
  // Keeping this as it was in your original code
  

  function categorizeSprintPlan(forecastedVelocity, totalStoryPoints) {
    forecastedVelocity = Math.ceil(forecastedVelocity); // Convert forecastedVelocity to an integer
    const differencePercentage = ((totalStoryPoints - forecastedVelocity) / forecastedVelocity) * 100;
  
    if (differencePercentage >= 20) {
      return "Overcommitted / High Risk";
    } else if (differencePercentage > 5 && differencePercentage < 20) {
      return "Ambitious / Stretch";
    } else if (differencePercentage >= -5 && differencePercentage <= 5) {
      return "Realistic / On Track";
    } else if (differencePercentage < -5 && differencePercentage > -20) {
      return "Conservative / Under-planned";
    } else if (differencePercentage <= -20) {
      return "Significantly Under-planned";
    }
  }

  // Using the more robust parsing function from previous discussion
  const parseChatResponse = (data: any) => {
      console.log("Parsing chat response:", data.response);
      // Added \s* and 'i' flag for more flexible matching
      const answer = data.response.match(/\s*Answer:\s*([^]*?)\s*Actionable Suggestions:/i)?.[1]?.trim() || "";
      const actions = data.response.match(/\s*Actionable Suggestions:\s*([^]*?)\s*(Updated Sprint Plan:|Summary:)/i)?.[1]?.trim() || "";
      // Adjusted regex for JSON block with whitespace flexibility and case insensitivity
      const updatedJsonMatch = data.response.match(/\s*Updated Sprint Plan:\s*```json\s*([^]*?)\s*```/i);
      const updatedJson = updatedJsonMatch ? JSON.parse(updatedJsonMatch[1].trim()) : null;
      // Added \s* and 'i' flag for Summary
      const summary = data.response.match(/\s*Summary:\s*([^]*)/i)?.[1]?.trim() || "";

      // Extract sprint_plan_updated and sprint_plan
      const sprint_plan_updated = data.sprint_plan_updated || null;
      const sprint_plan = data.sprint_plan || null;

      return { answer, actions, updatedJson, summary, sprint_plan_updated, sprint_plan };
  };


  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setInputValue(""); // Clear input field
    setIsThinking(true); // Show thinking animation

    try {
        const chatResponse = await axios.post("http://localhost:8000/api/chat", { message: userMessage.content, sprint_data: sprintData });
        console.log("Chat API Response:", chatResponse.data);

        // Use the robust parsing function
        const { answer, actions, updatedJson, summary, sprint_plan_updated, sprint_plan } = parseChatResponse(chatResponse.data);
        console.log("Parsed Response:", { answer, actions, updatedJson, summary, sprint_plan_updated, sprint_plan });

        // If updatedJson is present, send it to the update-sprint-task-distribution endpoint
        if (updatedJson !== null) {
            try {
                await axios.post("http://localhost:8000/api/update-sprint-task-distribution", updatedJson);
                console.log("Updated sprint task distribution successfully.");

                // Pass updatedJson as prop and update sprintAssignment state
                console.log("Updated JSON:", updatedJson.developer_daily_schedule);
                setSprintAssignment(updatedJson.developer_daily_schedule);
                setTotalTasks(updatedJson.total_tasks_selected);
                setTotalStoryPoint(updatedJson.total_story_points_selected);
                setRiskCategory(categorizeSprintPlan(updatedJson.total_story_points_selected,"188"))

                // Refresh TaskAssignmentTable
                // Assuming TaskAssignmentTable is a child component that reacts to sprintAssignment changes
            } catch (updateError) {
                console.error("Error updating sprint task distribution:", updateError);
            }
        } else {
            console.log("No updated JSON to send to the update-sprint-task-distribution endpoint.");
        }

        // Use sprint_plan_updated and sprint_plan as needed
        if (sprint_plan_updated) {
          console.log("Sprint Plan Updated:", sprint_plan_updated);
        }
        if (sprint_plan) {
          console.log("Sprint Plan:", sprint_plan);
        }

        // Delay adding bot message slightly for better UX
        // Using the parsed 'answer' for the bot response
        setTimeout(() => {
            const botResponseContent = answer || "Sorry, I couldn't process that request."; // Fallback if answer is empty
            const botResponse: Message = {
                content: botResponseContent,
                sender: "bot",
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, botResponse]);
            setIsThinking(false); // Hide thinking animation

            // You might want to handle 'actions', 'updatedJson', 'summary' here
            // e.g., display actions below the answer, use updatedJson elsewhere in the UI
            if (actions) {
                 // Optionally add actions as a separate bot message or render differently
                 console.log("Actionable Suggestions:", actions);
                 // Example: Add as a new message (adjust formatting as needed)
                // setMessages(prev => [...prev, { content: `**Actionable Suggestions:**\n${actions}`, sender: 'bot', timestamp: new Date() }]);
            }
            if (updatedJson) {
                 console.log("Updated Sprint Plan (JSON):", updatedJson);
                 // Optionally update sprint data state elsewhere
            }
            if (summary) {
                 console.log("Summary:", summary);
                 // Optionally display summary
            }

        }, 500); // 500ms delay
    } catch (error) {
        console.error("Error fetching chat response:", error);
        // Add an error message to the chat
        setMessages((prev) => [...prev, { content: "Sorry, there was an error fetching the response.", sender: "bot", timestamp: new Date() }]);
        setIsThinking(false); // Hide thinking animation
    }
};


  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    // Check if the ref is attached and the element exists
    if (scrollAreaRef.current) {
      // Use requestAnimationFrame to wait for the next paint cycle
      // This ensures the DOM has potentially updated with the new message height
      requestAnimationFrame(() => {
        // The ScrollArea component likely manages an internal scrollable element.
        // If scrollAreaRef.current is the correct element (the viewport), this works.
        // If not, you might need to target a specific child element (see previous explanation).
        scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
      });
    }
  }, [messages, isThinking]); // Effect depends on the messages array changing

  return (
    <>
      {/* Floating Icon */}
      {!isChatOpen && (
        <div
          className="fixed bottom-4 right-4 bg-primary text-white p-3 rounded-full shadow-lg cursor-pointer"
          onClick={() => setIsChatOpen(true)}
        >
          <MessageCircle className="h-6 w-6" />
        </div>
      )}

      {/* Chat Window */}
      {isChatOpen && (
        <div className="fixed bottom-4 right-4 w-96 bg-white border border-gray-300 rounded-lg shadow-lg">
          <Card className="border-t-4 border-t-primary shadow-lg">
            <CardHeader className="bg-gradient-to-r from-primary/10 to-transparent flex justify-between items-center">
              <CardTitle className="flex items-center">
                <Bot className="mr-2 text-primary" /> Sprint Assistant
                
              </CardTitle>
              <Button size="icon" variant="ghost" onClick={() => setIsChatOpen(false)}>
                ✕
              </Button>
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

                  {isThinking && (
                    <div className="flex justify-start">
                      <div className="flex items-center gap-2 bg-muted rounded-lg p-3">
                        <Loader className="animate-spin h-5 w-5 text-muted-foreground" />
                        <div className="text-sm text-muted-foreground">Thinking...</div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>
              <div className="p-4 border-t flex gap-2">
                <Input
                  placeholder="Ask a question about this sprint..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                  className="flex-1"
                  disabled={false} // You might want to disable this while waiting for bot response
                />
                <Button size="icon" onClick={handleSendMessage} disabled={false}> {/* Disable button while waiting */}
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};

export default SprintChatbot;