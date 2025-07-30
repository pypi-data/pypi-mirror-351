import React, { useEffect } from 'react';
import { ThinkingIndicatorProps } from '../types';

const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({ isVisible }) => {
  // 使用ref來存儲元素引用
  const indicatorRef = React.useRef<HTMLDivElement>(null);

  // 使用useEffect來在挂載後和isVisible變化時直接設置DOM樣式
  useEffect(() => {
    if (indicatorRef.current) {
      // 強制設置顯示狀態
      indicatorRef.current.style.display = isVisible ? 'flex' : 'none';
      indicatorRef.current.style.opacity = isVisible ? '1' : '0';

      // 嘗試將元素滾動到可視區域
      if (isVisible) {
        try {
          indicatorRef.current.scrollIntoView({ behavior: 'auto', block: 'end' });
        } catch (e) {
          console.error('滾動到思考指示器失敗', e);
        }
      }
    }
  }, [isVisible]);

  return (
    <div
      ref={indicatorRef}
      className="thinking-indicator"
      style={{
        color: '#fff',
        marginTop: 8,
        marginLeft: 12,
        display: isVisible ? 'flex' : 'none',
        alignItems: 'center',
        padding: '12px 20px',
        backgroundColor: '#444',
        borderRadius: '18px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
        position: 'relative',
        zIndex: 100,
        width: 'fit-content',
        opacity: isVisible ? 1 : 0,
        transition: 'opacity 0.2s ease-in-out',
        fontWeight: 'bold',
        animation: isVisible ? 'pulse 2s infinite' : 'none',
      }}
    >
      {/* 添加旋轉加載圖標 */}
      <div
        className="spinner"
        style={{
          width: '16px',
          height: '16px',
          border: '3px solid #fff',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          marginRight: '10px',
          animation: 'spin 1s linear infinite'
        }}
      ></div>

      <span>正在思考中</span>
      <span className="thinking-dots" style={{
        marginLeft: 4,
        animation: 'ellipsis 1.5s infinite',
      }}>...</span>

      <style>
        {`
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

          .thinking-dots {
            animation: ellipsis 1.5s infinite;
          }

          .spinner {
            animation: spin 1s linear infinite;
          }

          /* 確保思考指示器在任何情況下都能被看到 */
          .thinking-indicator {
            z-index: 100 !important;
            opacity: 1 !important;
            visibility: visible !important;
          }
        `}
      </style>
    </div>
  );
};

export default ThinkingIndicator;
