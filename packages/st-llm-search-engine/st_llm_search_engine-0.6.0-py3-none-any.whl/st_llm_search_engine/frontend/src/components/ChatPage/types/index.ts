export interface Message {
  id: string;
  role: "user" | "bot";
  content: string;
  created_at: string;
}

export interface ChatPageProps {
  apiUrl: string;
}

export interface MessageCache {
  messages: Message[];
  timestamp: number;
}

export interface MessageListProps {
  messages: Message[];
  isThinking: boolean;
  error: string;
  searchId: string;
  onErrorClear: () => void;
}

export interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isThinking: boolean;
}

export interface MessageItemProps {
  message: Message;
  isUser: boolean;
}

export interface ThinkingIndicatorProps {
  isVisible: boolean;
}

export interface ErrorMessageProps {
  message: string;
  onClear: () => void;
  isVisible: boolean;
}

export interface WelcomeMessageProps {
  isVisible: boolean;
}

export interface UseMessagesReturn {
  messages: Message[];
  isLoading: boolean;
  isThinking: boolean;
  error: string;
  sendUserMessage: (content: string) => Promise<void>;
  sendBotMessage: (content: string) => Promise<void>;
  clearError: () => void;
  clearMessages: () => void;
  refreshMessages: () => Promise<void>;
  validateCache: () => void;
  setThinking: (value: boolean) => void;
}
