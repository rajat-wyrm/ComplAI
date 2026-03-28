"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Send, MessageSquare, FileText, User, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { getHistory, chatWithDocument } from "@/lib/api";
import type { Document } from "@/types";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const { toast } = useToast();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const data = await getHistory();
        setDocuments(data.documents || []);
      } catch (error) {
        console.error("Failed to fetch documents:", error);
      }
    };
    fetchDocuments();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !selectedDoc) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await chatWithDocument(selectedDoc, input, sessionId || undefined);
      setSessionId(response.session_id);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat failed:", error);
      toast({
        title: "Error",
        description: "Failed to get response. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const selectedDocument = documents.find((d) => d.document_id === selectedDoc);

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold gradient-text">AI Chat Assistant</h1>
        <p className="text-muted-foreground mt-2">
          Ask questions about your compliance documents and get instant AI insights
        </p>
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-3">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-1"
        >
          <Card className="glass-card sticky top-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Select Document
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select value={selectedDoc} onValueChange={setSelectedDoc}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a document to chat about" />
                </SelectTrigger>
                <SelectContent>
                  {documents.length === 0 ? (
                    <SelectItem value="none" disabled>
                      No documents uploaded yet
                    </SelectItem>
                  ) : (
                    documents.map((doc) => (
                      <SelectItem key={doc.document_id} value={doc.document_id}>
                        <div className="flex flex-col">
                          <span>{doc.filename}</span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(doc.upload_date).toLocaleDateString()}
                          </span>
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>

              {selectedDocument && (
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-sm font-medium mb-1">Selected Document</p>
                  <p className="text-sm text-muted-foreground">{selectedDocument.filename}</p>
                  {selectedDocument.risk_score && (
                    <div className="mt-2 flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Risk Score:</span>
                      <span className={`text-xs font-medium ${
                        selectedDocument.risk_score >= 70 ? "text-red-500" :
                        selectedDocument.risk_score >= 40 ? "text-yellow-500" : "text-green-500"
                      }`}>
                        {selectedDocument.risk_score}%
                      </span>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <Card className="glass-card h-[600px] flex flex-col">
            <CardHeader className="border-b border-white/10">
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-primary" />
                Conversation
              </CardTitle>
            </CardHeader>

            <ScrollArea className="flex-1 p-4" ref={scrollRef}>
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    {selectedDoc
                      ? "Ask questions about your document"
                      : "Select a document to start chatting"}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.role === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-white/10"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          {message.role === "user" ? (
                            <User className="h-3 w-3" />
                          ) : (
                            <MessageSquare className="h-3 w-3" />
                          )}
                          <span className="text-xs opacity-70">
                            {message.role === "user" ? "You" : "AI Assistant"}
                          </span>
                        </div>
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className="text-xs opacity-50 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-white/10 rounded-lg p-3">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>

            <div className="p-4 border-t border-white/10">
              <div className="flex gap-2">
                <Input
                  placeholder={
                    selectedDoc
                      ? "Ask about compliance risks, recommendations, or specific sections..."
                      : "Select a document first"
                  }
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={!selectedDoc || loading}
                  className="flex-1"
                />
                <Button
                  onClick={handleSend}
                  disabled={!selectedDoc || !input.trim() || loading}
                  size="icon"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Powered by DeepSeek AI • Real-time document analysis
              </p>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
