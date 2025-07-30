import React, { useRef, useEffect } from 'react';
import { MessageListProps } from '../types';
import MessageItem from './MessageItem';
import ThinkingIndicator from './ThinkingIndicator';
import ErrorMessage from './ErrorMessage';
import WelcomeMessage from './WelcomeMessage';

const MessageList: React.FC<MessageListProps> = ({
  messages,
  isThinking,
  error,
  searchId,
  onErrorClear
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const thinkingRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const messageContainerRef = useRef<HTMLDivElement>(null);

  // 滾動到底部 (消息變化時)
  useEffect(() => {
    if (bottomRef.current) {
      // 先滾動到底部
      bottomRef.current.scrollIntoView({ behavior: 'auto' });

      // 如果正在思考中，則額外向上滾動一些，讓思考指示器顯示
      if (isThinking && messageContainerRef.current) {
        const container = messageContainerRef.current.parentElement;
        if (container) {
          // 向上滾動約100像素，使思考指示器完全可見
          container.scrollTop -= 120;
          console.log('[MessageList] 消息變化後向上滾動120px');
        }
      }
    }
  }, [messages, isThinking]);

  // 監控思考狀態變化
  useEffect(() => {
    if (isThinking) {
      console.log('[MessageList] 思考狀態開始');

      // 思考狀態開始時，強制向上滾動一些距離
      if (messageContainerRef.current) {
        const container = messageContainerRef.current.parentElement;
        if (container) {
          // 先滾動到底部，然後向上移動一段距離
          if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: 'auto' });
          }

          // 延遲一點，確保底部滾動已完成
          setTimeout(() => {
            if (container) {
              // 向上滾動約100像素，使思考指示器完全可見
              container.scrollTop -= 150;
              console.log('[MessageList] 思考狀態開始時向上滾動150px');
            }
          }, 50);
        }
      }
    }
  }, [isThinking]);

  const showWelcome = searchId === "999" && messages.length === 0 && !isThinking;

  return (
    <div
      ref={listRef}
      className="message-list-container"
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        padding: '24px 0',
        paddingBottom: '160px',
        background: '#222',
        height: '100%',
        width: '100%',
        position: 'relative'
      }}
    >
      <WelcomeMessage isVisible={showWelcome} />

      <div
        ref={messageContainerRef}
        style={{
          width: '80%',
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          visibility: showWelcome ? 'hidden' : 'visible',
          minHeight: isThinking ? '100px' : 'auto',
          position: 'relative'
        }}
      >
        {messages.map((message) => (
          <MessageItem
            key={message.id}
            message={message}
            isUser={message.role === 'user'}
          />
        ))}

        {/* 移除底部思考指示器，只保留頂部漂浮的 */}
        <div
          ref={thinkingRef}
          style={{
            minHeight: '40px',
            position: 'relative',
            marginTop: '16px',
            paddingBottom: '20px',
            display: 'none', // 隱藏原本在底部的思考指示器
          }}
          className="thinking-indicator-container"
        >
          {/* 完全移除ThinkingIndicator組件的使用 */}
        </div>

        <ErrorMessage
          message={error}
          onClear={onErrorClear}
          isVisible={!!error}
        />

        <div
          ref={bottomRef}
          style={{ height: '150px', width: '100%' }}
          className="bottom-marker"
        />
      </div>

      {/* 浮動的思考指示器 - 當思考狀態開始時顯示在視窗頂部 */}
      {isThinking && (
        <div
          className="floating-thinking-indicator"
          style={{
            position: 'fixed', // 改為fixed以確保總是在視窗中央
            top: 'auto',
            bottom: '120px',
            left: '0',
            width: '100%',
            display: 'flex',
            justifyContent: 'center',
            zIndex: 1000,
            pointerEvents: 'none',
          }}
        >
          <div
            style={{
              backgroundColor: 'rgba(68, 68, 68, 0.95)',
              color: 'white',
              padding: '10px 20px',
              borderRadius: '20px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              fontWeight: 'bold',
              animation: 'pulse 2s infinite',
            }}
          >
            <div
              style={{
                width: '16px',
                height: '16px',
                border: '3px solid #fff',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                marginRight: '10px',
                animation: 'spin 1s linear infinite',
              }}
            ></div>
            <span>正在思考中</span>
            <span style={{ marginLeft: 4, animation: 'ellipsis 1.5s infinite' }}>...</span>
          </div>
        </div>
      )}

      {/* 全局輔助樣式 */}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes ellipsis {
          0% { opacity: 0.3; }
          50% { opacity: 1; }
          100% { opacity: 0.3; }
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4); }
          70% { box-shadow: 0 0 0 8px rgba(255, 255, 255, 0); }
          100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
        }

        /* 確保思考指示器在任何情況下都能被看到 */
        .floating-thinking-indicator {
          opacity: 1 !important;
          visibility: visible !important;
        }
      `}} />
    </div>
  );
};

export default MessageList;
