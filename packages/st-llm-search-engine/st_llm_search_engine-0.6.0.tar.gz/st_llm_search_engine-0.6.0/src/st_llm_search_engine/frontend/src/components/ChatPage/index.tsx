import React, { useState, useEffect, useCallback, useRef, forwardRef, useImperativeHandle } from 'react';
import { getSessionId } from '../../utils/session';
import { ChatPageProps } from './types';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import { useMessages } from './hooks/useMessages';
import { SavedSearch } from '../SavedSearchList/types';
import { fetchWithKey } from '../../utils/fetchWithKey';
import SavedSearchExecution from './components/SavedSearchExecution';

const ChatPage: React.FC<ChatPageProps> = ({ apiUrl }) => {
  // 每次加載頁面都會獲取新的 sessionId，確保每個標籤頁有獨立的 session
  const [sessionId] = useState<string>(() => getSessionId());
  const [searchId, setSearchId] = useState<string>("999");
  const [input, setInput] = useState("");
  const [currentSearch, setCurrentSearch] = useState<SavedSearch | null>(null);
  const previousSearchIdRef = useRef<string>("999");
  // 用於處理搜索切換的鎖定狀態
  const isSwitchingSearchRef = useRef<boolean>(false);
  // 用於追蹤搜索切換後的渲染
  const searchSwitchCountRef = useRef<number>(0);
  // 本地思考狀態，直接管理而不依賴 isThinking
  const [isLocalThinking, setIsLocalThinking] = useState<boolean>(false);
  // 追蹤思考狀態的變更時間
  const lastThinkingChangeRef = useRef<number>(Date.now());
  // 新增 ref 用於調用 SavedSearchExecution 的 executeSearch
  const savedSearchExecutionRef = useRef<any>(null);

  // 直接操作DOM顯示思考狀態
  const showThinkingDirectly = useCallback((show: boolean) => {
    // 先找到消息列表底部的加載指示器
    const thinkingIndicators = document.querySelectorAll('.thinking-indicator');
    if (thinkingIndicators.length > 0) {
      thinkingIndicators.forEach(indicator => {
        (indicator as HTMLElement).style.display = show ? 'flex' : 'none';
      });
      console.log(`[DOM] 直接設置思考指示器顯示狀態: ${show ? '顯示' : '隱藏'}`);
    } else {
      console.log(`[DOM] 找不到思考指示器元素`);
      // 如果找不到指示器，可能頁面還沒完全加載，嘗試延遲設置
      setTimeout(() => {
        const indicators = document.querySelectorAll('.thinking-indicator');
        if (indicators.length > 0) {
          indicators.forEach(indicator => {
            (indicator as HTMLElement).style.display = show ? 'flex' : 'none';
          });
          console.log(`[DOM] 延遲後設置思考指示器顯示狀態: ${show ? '顯示' : '隱藏'}`);
        }
      }, 100);
    }

    // 同時嘗試切換消息輸入框的禁用狀態
    const inputBox = document.querySelector('.message-input textarea');
    if (inputBox) {
      (inputBox as HTMLTextAreaElement).disabled = show;
      console.log(`[DOM] 設置輸入框禁用狀態: ${show}`);
    }

    // 嘗試添加/移除全局CSS類以顯示加載狀態
    if (show) {
      document.body.classList.add('is-thinking');
    } else {
      document.body.classList.remove('is-thinking');
    }

    return show; // 返回狀態以便後續使用
  }, []);

  // 包裝 setThinking 函數，添加調試日誌和直接操作DOM
  const setThinkingWithLog = useCallback((value: boolean) => {
    // 記錄上一次變更的時間
    const now = Date.now();
    const timeSinceLastChange = now - lastThinkingChangeRef.current;
    lastThinkingChangeRef.current = now;

    console.log(`[DEBUG-ChatPage] 設置思考狀態: ${value}，之前的狀態: ${isLocalThinking}, 距離上次變更: ${timeSinceLastChange}ms`);

    // 無論React狀態如何，立即直接操作DOM
    showThinkingDirectly(value);

    // 更新React狀態
    setIsLocalThinking(value);

    // 使用 setTimeout 檢查狀態是否已更新
    setTimeout(() => {
      console.log(`[DEBUG-ChatPage] 思考狀態設置後檢查: ${isLocalThinking}, 實際新值: ${value}`);
      // 再次確保DOM狀態正確
      showThinkingDirectly(value);
    }, 50);

    return value; // 返回值以便鏈式調用
  }, [isLocalThinking, showThinkingDirectly]);

  // 監聽思考狀態變化
  useEffect(() => {
    console.log(`[DEBUG-ChatPage] 思考狀態變更: ${isLocalThinking}`);

    // 確保DOM狀態與React狀態同步
    showThinkingDirectly(isLocalThinking);

  }, [isLocalThinking, showThinkingDirectly]);

  // 從 URL 獲取 searchId (如果有)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sid = urlParams.get('search_id');
    if (sid) setSearchId(sid);
    console.debug(`[ChatPage] 初始化頁面，sessionId=${sessionId}, searchId=${sid || 'none'}`);
  }, []);

  // 當從 URL 獲取到 searchId 時，主動獲取對應的 search 詳細信息
  useEffect(() => {
    // 避免重複的請求
    if (searchId === previousSearchIdRef.current) {
      return;
    }

    // 更新前一個searchId的引用
    previousSearchIdRef.current = searchId;

    const fetchSearchInfo = async () => {
      if (searchId === "999" || !sessionId) return;

      // 檢查是否已經有 currentSearch，這裡只做初步檢查
      // 如果已有 currentSearch 並且 ID 匹配，則不再獲取
      if (currentSearch && currentSearch.id.toString() === searchId) {
        console.debug(`[ChatPage] 已有 currentSearch (ID: ${searchId})，無需重新獲取`);
        return;
      }

      console.debug(`[ChatPage] 開始獲取 searchId=${searchId} 的詳細信息`);
      try {
        // 獲取所有保存的搜索
        const response = await fetchWithKey(`${apiUrl}/api/saved_search?session_id=${sessionId}`);
        if (!response.ok) {
          throw new Error(`獲取搜索列表失敗: ${response.status}`);
        }

        const data = await response.json();
        let searches = Array.isArray(data) ? data : (Array.isArray(data.searches) ? data.searches : []);

        // 查找匹配 searchId 的搜索
        const foundSearch = searches.find(s => s.id.toString() === searchId);

        if (foundSearch) {
          console.debug(`[ChatPage] 找到 searchId=${searchId} 的搜索: ${foundSearch.title}`);
          setCurrentSearch(foundSearch);
        } else {
          console.error(`[ChatPage] 未找到 searchId=${searchId} 的搜索`);
        }
      } catch (error) {
        console.error(`[ChatPage] 獲取搜索詳細信息失敗:`, error);
      }
    };

    fetchSearchInfo();
  }, [searchId, sessionId, apiUrl, currentSearch]);

  // 記錄 sessionId 到控制台，幫助調試
  useEffect(() => {
    console.debug(`[ChatPage] 當前 sessionId: ${sessionId}`);
  }, [sessionId]);

  // 使用自定義 hook 處理消息
  const {
    messages,
    isLoading,
    isThinking,
    error,
    sendUserMessage,
    sendBotMessage,
    clearError,
    clearMessages,
    refreshMessages,
    validateCache,
  } = useMessages(apiUrl, sessionId, searchId);

  // 處理發送消息
  const handleSend = () => {
    if (!input.trim()) return;
    console.debug(`[ChatPage] 發送消息: ${input.substring(0, 30)}...`);
    sendUserMessage(input);
    setInput("");
  };

  // 設置消息內容
  const handleInputChange = (value: string) => {
    setInput(value);
  };

  // 監聽 switchSearch 事件
  useEffect(() => {
    const handleSwitchSearch = async (event: CustomEvent) => {
      const { searchId: newSearchId, search } = event.detail;
      console.debug(`[ChatPage] 接收到切換搜索事件: ${newSearchId}`);

      // 如果已經是當前搜索，則不進行處理
      if (newSearchId === searchId) {
        console.debug(`[ChatPage] 搜索未變更，跳過處理`);
        return;
      }

      // 如果已經在切換過程中，防止重複操作
      if (isSwitchingSearchRef.current) {
        console.debug(`[ChatPage] 正在處理另一個搜索切換，跳過當前請求`);
        return;
      }

      // 標記為正在切換
      isSwitchingSearchRef.current = true;
      searchSwitchCountRef.current += 1;

      try {
        // 檢查切換目標的搜索是否有被錯誤標記為清空
        const targetCacheKey = `messages_${sessionId}_${newSearchId}`;
        const clearMark = `${targetCacheKey}_cleared`;

        try {
          // 檢查是否有清空標記
          if (sessionStorage.getItem(clearMark) === 'true') {
            // 檢查是否實際上有數據
            const cachedMessages = sessionStorage.getItem(targetCacheKey);
            if (cachedMessages) {
              const parsedMessages = JSON.parse(cachedMessages);
              if (Array.isArray(parsedMessages) && parsedMessages.length > 0) {
                // 如果有數據，則移除清空標記
                sessionStorage.removeItem(clearMark);
                console.debug(`[ChatPage] 切換搜索: 移除了清空標記 ${clearMark}`);
              }
            }
          }
        } catch (error) {
          console.error(`[ChatPage] 檢查sessionStorage數據時出錯:`, error);
        }

        // 先設置搜索對象，再設置搜索ID
        console.debug(`[ChatPage] 設置新的搜索對象: ${search.title} (ID: ${newSearchId})`);
        setCurrentSearch(search);

        // 增加一個小延遲，確保UI能夠先更新
        await new Promise(resolve => setTimeout(resolve, 10));

        // 再清空消息列表
        console.debug(`[ChatPage] 清空消息列表`);
        clearMessages();

        // 最後設置搜索ID，這會觸發 useMessages 重新加載消息
        console.debug(`[ChatPage] 設置新的搜索ID: ${newSearchId}`);
        setSearchId(newSearchId);
      } finally {
        // 使用一個短暫的延遲再解鎖，確保組件有足夠時間更新
        setTimeout(() => {
          console.debug(`[ChatPage] 搜索切換完成，解除鎖定狀態`);
          isSwitchingSearchRef.current = false;
        }, 200);
      }
    };

    window.addEventListener('switchSearch', handleSwitchSearch as EventListener);
    return () => {
      window.removeEventListener('switchSearch', handleSwitchSearch as EventListener);
    };
  }, [searchId, clearMessages, sessionId]);

  // 檢查快取數據結構與後端一致性
  useEffect(() => {
    // 每次 search_id 變更時驗證快取
    console.debug(`[ChatPage] searchId 變更，驗證快取: ${searchId}`);
    validateCache();
  }, [searchId, validateCache]);

  // 監聽消息變化
  useEffect(() => {
    console.debug(`[ChatPage] 消息列表更新，現有 ${messages.length} 條消息`);
  }, [messages]);

  // 監聽 forceExecuteSearch 事件 - 用於強制清空後重新執行
  useEffect(() => {
    const handleForceExecute = async (event: CustomEvent) => {
      const { searchId: newSearchId, search, forceClean } = event.detail;
      console.debug(`[ChatPage] 接收到強制執行搜索事件: ${newSearchId}, forceClean: ${forceClean}`);

      // 如果已經在切換過程中，防止重複操作
      if (isSwitchingSearchRef.current) {
        console.debug(`[ChatPage] 正在處理另一個搜索切換，跳過當前請求`);
        return;
      }

      // 標記為正在切換
      isSwitchingSearchRef.current = true;
      searchSwitchCountRef.current += 1;

      try {
        // 直接刪除與此搜索相關的所有 sessionStorage
        if (forceClean) {
          // 清除 API 中的消息
          try {
            console.debug(`[ChatPage] 正在清除 API 中的消息，sessionId=${sessionId}, searchId=${newSearchId}`);
            const clearResponse = await fetchWithKey(
              `${apiUrl}/api/message/?session_id=${sessionId}&search_id=${newSearchId}`,
              { method: 'DELETE' }
            );

            if (clearResponse.ok) {
              console.debug(`[ChatPage] 成功清除 API 中的消息`);
            } else {
              console.error(`[ChatPage] 清除 API 消息失敗: ${clearResponse.status}`);
            }
          } catch (error) {
            console.error(`[ChatPage] 清除 API 消息出錯:`, error);
          }

          // 清除所有相關的 sessionStorage
          Object.keys(sessionStorage).forEach(key => {
            if (key.includes(`_${newSearchId}`) || key.endsWith(`_${newSearchId}`)) {
              console.debug(`[ChatPage] 刪除 sessionStorage 項目: ${key}`);
              sessionStorage.removeItem(key);
            }
          });
        }

        // 先設置搜索對象，再設置搜索ID
        console.debug(`[ChatPage] 設置新的搜索對象: ${search.title} (ID: ${newSearchId})`);
        setCurrentSearch(search);

        // 增加一個小延遲，確保UI能夠先更新
        await new Promise(resolve => setTimeout(resolve, 10));

        // 強制清空消息列表
        console.debug(`[ChatPage] 強制清空消息列表`);
        clearMessages();

        // 最後設置搜索ID，這會觸發 useMessages 重新加載消息
        console.debug(`[ChatPage] 設置新的搜索ID: ${newSearchId}`);
        setSearchId(newSearchId);
        // 新增：如果 ref 存在且有 forceExecute 方法，直接調用
        setTimeout(() => {
          if (savedSearchExecutionRef.current && typeof savedSearchExecutionRef.current.forceExecute === 'function') {
            console.debug('[ChatPage] 直接調用 SavedSearchExecution.forceExecute');
            savedSearchExecutionRef.current.forceExecute();
          }
        }, 100);
      } finally {
        // 使用一個短暫的延遲再解鎖，確保組件有足夠時間更新
        setTimeout(() => {
          console.debug(`[ChatPage] 搜索切換完成，解除鎖定狀態`);
          isSwitchingSearchRef.current = false;
        }, 200);
      }
    };

    window.addEventListener('forceExecuteSearch', handleForceExecute as EventListener);
    return () => {
      window.removeEventListener('forceExecuteSearch', handleForceExecute as EventListener);
    };
  }, [apiUrl, sessionId, clearMessages]);

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      width: "calc(100% - 288px)", // 減去 Sidebar 的寬度
      marginLeft: "288px", // 從 Sidebar 右側開始
      height: "100vh",
      position: "relative",
      background: "#222",
      overflow: "hidden"
    }}>
      {/* 使用SavedSearchExecution組件處理保存的搜索 */}
      {!isSwitchingSearchRef.current && searchId !== "999" && currentSearch && (
        <SavedSearchExecution
          key={`search-execution-${searchId}-${searchSwitchCountRef.current}`}
          apiUrl={apiUrl}
          sessionId={sessionId}
          searchId={searchId}
          currentSearch={currentSearch}
          sendBotMessage={sendBotMessage}
          setThinking={setThinkingWithLog}
          messages={messages}
          isLoading={isLoading}
          isThinking={isLocalThinking}
          clearMessages={clearMessages}
        />
      )}

      {/* 消息列表 */}
      <MessageList
        messages={messages}
        isThinking={isLocalThinking}
        error={error}
        searchId={searchId}
        onErrorClear={clearError}
      />

      {/* 消息輸入框 */}
      <MessageInput
        value={input}
        onChange={handleInputChange}
        onSend={handleSend}
        isThinking={isLocalThinking}
      />

      {/* 全局CSS動畫 */}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        body.is-thinking .message-input {
          opacity: 0.7;
        }
      `}} />
    </div>
  );
};

export default ChatPage;
