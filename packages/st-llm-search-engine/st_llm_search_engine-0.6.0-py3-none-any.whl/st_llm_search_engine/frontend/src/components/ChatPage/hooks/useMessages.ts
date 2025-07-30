import { useState, useEffect, useCallback, useRef } from 'react';
import { Message, MessageCache, UseMessagesReturn } from '../types';
import { fetchWithKey } from '../../../utils/fetchWithKey';

// 快取過期時間 - 1小時
const CACHE_EXPIRY = 60 * 60 * 1000;

// 內存快取
const messageCache: Record<string, { messages: Message[], timestamp: number }> = {};

export const useMessages = (
  apiUrl: string,
  sessionId: string,
  searchId: string
): UseMessagesReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // 追蹤是否有外部調用的清空消息
  const hasExternalClearRef = useRef<boolean>(false);
  // 追蹤上一次的searchId
  const previousSearchIdRef = useRef<string | null>(null);

  // 獲取快取鍵
  const getCacheKey = useCallback(() => {
    return `messages_${sessionId}_${searchId}`;
  }, [sessionId, searchId]);

  // 保存消息到sessionStorage
  const saveMessages = useCallback((updatedMessages: Message[]) => {
    if (!sessionId || !searchId) {
      console.debug(`[useMessages] sessionId或searchId未提供，無法保存訊息`);
      return;
    }

    const cacheKey = getCacheKey();
    try {
      // 保存到sessionStorage
      sessionStorage.setItem(cacheKey, JSON.stringify(updatedMessages));
      console.debug(`[useMessages] 已保存${updatedMessages.length}條訊息到sessionStorage, key=${cacheKey}`);
    } catch (error) {
      console.error(`[useMessages] 保存訊息到sessionStorage失敗:`, error);
    }
  }, [sessionId, searchId, getCacheKey]);

  // 更新內存快取
  const updateCache = useCallback((updatedMessages: Message[]) => {
    const cacheKey = getCacheKey();

    // 更新內存快取
    messageCache[cacheKey] = {
      messages: updatedMessages,
      timestamp: Date.now()
    };

    // 同時更新sessionStorage
    saveMessages(updatedMessages);

    console.debug(`[useMessages] 已更新快取 ${cacheKey}, 共 ${updatedMessages.length} 條消息`);
  }, [getCacheKey, saveMessages]);

  // 獲取 AI 回應
  const getLLMResponse = useCallback(async (userQuery: string = "") => {
    try {
      setIsThinking(true);
      setError(null);
      console.debug(`[useMessages] 開始獲取 AI 回應，查詢: "${userQuery.substring(0, 30)}..."`);

      // 從技術文件規範的請求方式
      const response = await fetchWithKey(
        `${apiUrl}/api/message/llm?session_id=${sessionId}&search_id=${searchId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userQuery })
        }
      );

      console.debug(`[useMessages] AI 回應 API 響應狀態: ${response.status}`);

      if (response.ok) {
        const data = await response.json();
        console.debug(`[useMessages] 收到 AI 回應數據:`, data);

        // 直接處理回應數據而非重新加載所有消息
        let botContent = '';

        // 嘗試獲取內容，處理不同的數據格式
        if (typeof data === 'object' && data !== null) {
          if (typeof data.content === 'string') {
            botContent = data.content;
          } else if (typeof data.response === 'string') {
            botContent = data.response;
          } else if (typeof data.message === 'string') {
            botContent = data.message;
          } else {
            // 如果沒有找到可識別的字段，將整個響應轉為 JSON 字符串
            botContent = JSON.stringify(data);
          }
        } else if (typeof data === 'string') {
          botContent = data;
        } else {
          botContent = "無法解析 AI 回應";
        }

        console.debug(`[useMessages] 處理後的 AI 回應內容: "${botContent.substring(0, 50)}..."`);

        // 如果成功獲取到回應，則將其保存為 bot 消息
        if (botContent) {
          // 直接保存 bot 消息到 API 以確保持久化
          const botSaveResponse = await fetchWithKey(
            `${apiUrl}/api/message?session_id=${sessionId}&search_id=${searchId}`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ role: 'bot', content: botContent })
            }
          );

          console.debug(`[useMessages] 保存 bot 消息 API 響應狀態: ${botSaveResponse.status}`);

          if (botSaveResponse.ok) {
            const botData = await botSaveResponse.json();
            console.debug(`[useMessages] 保存 bot 消息返回數據:`, botData);

            // 使用返回的數據 ID，而不是生成臨時 ID
            const botMessage: Message = {
              id: botData.id || `bot-${Date.now()}`,
              role: 'bot',
              content: botContent,
              created_at: botData.created_at || new Date().toISOString()
            };

            // 添加 bot 消息到 UI 並更新快取
            setMessages(prevMessages => {
              const updatedMessages = [...prevMessages, botMessage];
              console.debug(`[useMessages] 添加 bot 消息到 UI，現有消息數: ${updatedMessages.length}`);

              // 保存到快取
              updateCache(updatedMessages);

              return updatedMessages;
            });
          } else {
            console.error(`[useMessages] 保存 bot 消息失敗: ${botSaveResponse.status}`);
            setError("無法保存 AI 回應，請稍後再試");
          }
        } else {
          console.error(`[useMessages] AI 回應內容為空`);
          setError("收到空的 AI 回應");
        }
      } else {
        console.error(`[useMessages] 獲取 AI 回應失敗: ${response.status}`);
        setError("無法獲取 AI 回應，請稍後再試");

        // 嘗試讀取錯誤詳情
        try {
          const errorData = await response.json();
          console.error(`[useMessages] 錯誤詳情:`, errorData);
        } catch (e) {
          // 忽略解析錯誤
        }
      }
    } catch (error) {
      console.error(`[useMessages] 獲取 AI 回應錯誤:`, error);
      setError("連接失敗，請檢查網絡");
    } finally {
      setIsThinking(false);
    }
  }, [apiUrl, sessionId, searchId, updateCache]);

  // 加載消息
  const loadMessages = useCallback(async () => {
    console.debug(`[useMessages] 嘗試載入訊息, sessionId=${sessionId}, searchId=${searchId}`);

    if (!sessionId || !searchId) {
      console.debug(`[useMessages] sessionId或searchId未提供，無法載入訊息`);
      setMessages([]);
      return;
    }

    // 如果是外部清空引起的，跳過本次載入
    if (hasExternalClearRef.current) {
      console.debug(`[useMessages] 檢測到外部清空操作，跳過自動載入`);
      hasExternalClearRef.current = false;
      return;
    }

    // 嘗試從sessionStorage獲取緩存的訊息
    const cacheKey = getCacheKey();
    try {
      // 檢查是否有被標記為已清空
      const clearMark = `${cacheKey}_cleared`;
      const isCleared = sessionStorage.getItem(clearMark) === 'true';

      // 檢查是否有實際消息數據
      const cachedMessages = sessionStorage.getItem(cacheKey);

      if (cachedMessages) {
        const parsedMessages = JSON.parse(cachedMessages);

        // 如果有實際數據，不管是否被標記為已清空，都使用這些數據
        if (parsedMessages && Array.isArray(parsedMessages) && parsedMessages.length > 0) {
          console.debug(`[useMessages] 從sessionStorage載入${parsedMessages.length}條訊息`);

          // 如果之前被標記為已清空，但現在要顯示，則移除清空標記
          if (isCleared) {
            sessionStorage.removeItem(clearMark);
            console.debug(`[useMessages] 移除了清空標記 ${clearMark}`);
          }

          setMessages(parsedMessages);
          return;
        }
      }

      // 如果被標記為已清空且沒有有效數據，顯示空列表
      if (isCleared) {
        console.debug(`[useMessages] 檢測到 ${cacheKey} 被標記為已清空，顯示空消息列表`);
        setMessages([]);
        return;
      }
    } catch (error) {
      console.error(`[useMessages] 從sessionStorage載入訊息失敗:`, error);
    }

    // 如果沒有快取或發生錯誤，從API獲取
    setIsLoading(true);
    try {
      const response = await fetchWithKey(
        `${apiUrl}/api/message?session_id=${sessionId}&search_id=${searchId}`
      );

      if (response.ok) {
        const data = await response.json();
        const parsedMessages = Array.isArray(data) ? data : [];

        // 設置訊息並更新快取
        setMessages(parsedMessages);
        updateCache(parsedMessages);

        console.debug(`[useMessages] 從API載入${parsedMessages.length}條訊息`);
      } else {
        console.error(`[useMessages] 載入訊息失敗: ${response.status}`);
        setError("無法加載對話歷史");
      }
    } catch (error) {
      console.error(`[useMessages] 載入訊息出錯:`, error);
      setError("連接服務器失敗，請檢查網絡");
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, sessionId, searchId, getCacheKey, updateCache]);

  // 發送用戶消息
  const sendUserMessage = useCallback(async (content: string) => {
    if (!sessionId || !searchId) {
      console.debug(`[useMessages] sessionId或searchId未提供，無法發送訊息`);
      setError("無法發送訊息，請重新整理頁面");
      return;
    }

    const tempId = `temp-${Date.now()}`;
    const userMessage: Message = {
      id: tempId,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };

    // 添加用戶訊息到UI
    setMessages(prevMessages => {
      const newMessages = [...prevMessages, userMessage];
      updateCache(newMessages);
      return newMessages;
    });

    setIsThinking(true);
    setError(null);

    try {
      const response = await fetchWithKey(
        `${apiUrl}/api/message?session_id=${sessionId}&search_id=${searchId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ role: 'user', content })
        }
      );

      if (response.ok) {
        const data = await response.json();

        // 用實際ID替換臨時ID
        setMessages(prevMessages => {
          const updatedMessages = prevMessages.map(m =>
            m.id === tempId ? { ...m, id: data.id || m.id } : m
          );

          // 保存更新後的訊息
          updateCache(updatedMessages);

          return updatedMessages;
        });

        // 等待bot回應
        await getLLMResponse(content);
      } else {
        setError("發送訊息失敗，請重試");
        console.error(`[useMessages] 發送訊息失敗: ${response.status}`);
      }
    } catch (error) {
      setError("連接服務器失敗，請檢查網絡");
      console.error(`[useMessages] 發送訊息出錯:`, error);
    } finally {
      setIsThinking(false);
    }
  }, [apiUrl, sessionId, searchId, updateCache, getLLMResponse]);

  // 發送機器人消息
  const sendBotMessage = useCallback(async (content: string) => {
    if (!sessionId || !searchId) {
      console.debug(`[useMessages] sessionId或searchId未提供，無法發送bot訊息`);
      return;
    }

    try {
      const response = await fetchWithKey(
        `${apiUrl}/api/message?session_id=${sessionId}&search_id=${searchId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ role: 'bot', content })
        }
      );

      if (response.ok) {
        const data = await response.json();

        const botMessage: Message = {
          id: data.id || `bot-${Date.now()}`,
          role: 'bot',
          content,
          created_at: new Date().toISOString()
        };

        // 添加bot訊息到UI
        setMessages(prevMessages => {
          const updatedMessages = [...prevMessages, botMessage];

          // 保存更新後的訊息
          updateCache(updatedMessages);

          return updatedMessages;
        });

        return data;
      } else {
        console.error(`[useMessages] 發送bot訊息失敗: ${response.status}`);
      }
    } catch (error) {
      console.error(`[useMessages] 發送bot訊息出錯:`, error);
    }
  }, [apiUrl, sessionId, searchId, updateCache]);

  // 清空錯誤信息
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // 驗證快取一致性
  const validateCache = useCallback(() => {
    // 如果檢測到不一致，可以調用 loadMessages 強制刷新
    console.debug(`[useMessages] 驗證快取，sessionId=${sessionId}, searchId=${searchId}`);
    loadMessages();
  }, [loadMessages]);

  // 當 sessionId 變更時強制刷新
  useEffect(() => {
    console.debug(`[useMessages] sessionId 變更，強制刷新`);
    loadMessages();
  }, [sessionId, loadMessages]);

  // 當 searchId 變更時載入對應對話
  useEffect(() => {
    // 避免初始化或重複的searchId變更
    if (previousSearchIdRef.current === searchId) {
      return;
    }

    console.debug(`[useMessages] searchId 變更為 ${searchId}，載入對應對話`);

    // 更新前一次searchId引用
    previousSearchIdRef.current = searchId;

    // 清除可能存在的清空標記，確保重新訪問時能正確加載
    const cacheKey = getCacheKey();
    const clearMark = `${cacheKey}_cleared`;
    if (sessionStorage.getItem(clearMark) === 'true') {
      // 檢查是否有實際數據
      try {
        const cachedMessages = sessionStorage.getItem(cacheKey);
        if (cachedMessages) {
          const parsedMessages = JSON.parse(cachedMessages);
          if (Array.isArray(parsedMessages) && parsedMessages.length > 0) {
            // 如果有數據，則移除清空標記
            sessionStorage.removeItem(clearMark);
            console.debug(`[useMessages] 搜索變更: 移除了清空標記 ${clearMark}`);
          }
        }
      } catch (error) {
        console.error(`[useMessages] 檢查sessionStorage數據時出錯:`, error);
      }
    }

    // 如果不是通過外部清空引起的，則自動載入新消息
    if (!hasExternalClearRef.current) {
      loadMessages();
    }
  }, [searchId, loadMessages, getCacheKey]);

  // 添加清空消息的函數
  const clearMessages = useCallback(() => {
    console.debug(`[useMessages] 清空消息列表`);

    // 標記為外部清空
    hasExternalClearRef.current = true;

    // 清空消息和錯誤狀態
    setMessages([]);
    setError(null);

    // 不再自動清除 sessionStorage 中的消息
    // 只更新內存快取，保留 sessionStorage 中的數據
    const cacheKey = getCacheKey();
    messageCache[cacheKey] = {
      messages: [],
      timestamp: Date.now()
    };

    // 修改：不再清除 sessionStorage，改為添加標記
    // 獲取現有消息
    try {
      const cachedMessages = sessionStorage.getItem(cacheKey);
      if (cachedMessages) {
        // 只標記為已清空，而不實際刪除數據
        sessionStorage.setItem(`${cacheKey}_cleared`, 'true');
        console.debug(`[useMessages] 已標記 ${cacheKey} 為已清空，但保留了原始數據`);
      } else {
        // 如果沒有現有消息，則可以設置為空數組
        sessionStorage.setItem(cacheKey, JSON.stringify([]));
        console.debug(`[useMessages] 已創建空的消息數組 ${cacheKey}`);
      }
    } catch (error) {
      console.error(`[useMessages] 處理 sessionStorage 數據時出錯:`, error);
      // 出錯時作為後備方案設置空數組
      sessionStorage.setItem(cacheKey, JSON.stringify([]));
    }

    console.debug(`[useMessages] 已清空內存快取和UI消息列表，但保留了 sessionStorage 數據`);
  }, [getCacheKey]);

  return {
    messages,
    isLoading,
    isThinking,
    error,
    sendUserMessage,
    sendBotMessage,
    clearError,
    clearMessages, // 暴露清空消息的函數
    refreshMessages: loadMessages,
    validateCache,
    setThinking: (value: boolean) => setIsThinking(value)
  };
};
