import React, { useCallback, useEffect, useState, useRef } from 'react';
import { SavedSearch } from '../../SavedSearchList/types';
import { fetchWithKey } from '../../../utils/fetchWithKey';
import { Message } from '../types';

interface SavedSearchExecutionProps {
  apiUrl: string;
  sessionId: string;
  searchId: string;
  currentSearch: SavedSearch | null;
  sendBotMessage: (content: string) => Promise<void>;
  setThinking: (value: boolean) => void;
  messages: Message[];
  isLoading: boolean;
  isThinking: boolean;
  clearMessages: () => void;
}

interface RecordCountResult {
  count: number;
  total: number;
  start_datetime: string;
  end_datetime: string;
  source: string;
  kol: string;
}

// 在內存中存儲KOL數據快取
const kolDataCountCache: Record<string, { data: RecordCountResult, timestamp: number }> = {};
const CACHE_EXPIRY = 10 * 60 * 1000; // 10分鐘過期

// 鎖機制相關常數
const LOCK_EXPIRY = 30 * 1000; // 30秒鎖過期
const LOCK_PREFIX = 'search_execution_lock_'; // 鎖的前綴

/**
 * 嘗試獲取執行鎖
 * @param lockKey 鎖的唯一標識
 * @returns 是否成功獲取鎖
 */
const acquireLock = (lockKey: string): boolean => {
  const now = Date.now();
  const lockData = sessionStorage.getItem(lockKey);

  if (lockData) {
    // 如果鎖存在，檢查是否過期
    const lockInfo = JSON.parse(lockData);
    if (now < lockInfo.expires) {
      // 鎖未過期，獲取失敗
      console.debug(`[SavedSearchExecution] 鎖 ${lockKey} 已被占用，獲取失敗`);
      return false;
    }
  }

  // 鎖不存在或已過期，獲取新鎖
  const lockInfo = {
    acquired: now,
    expires: now + LOCK_EXPIRY,
    requestId: Math.random().toString(36).substring(2, 9) // 生成隨機的請求ID
  };

  sessionStorage.setItem(lockKey, JSON.stringify(lockInfo));
  console.debug(`[SavedSearchExecution] 成功獲取鎖 ${lockKey}，過期時間: ${new Date(lockInfo.expires).toISOString()}`);
  return true;
};

/**
 * 釋放執行鎖
 * @param lockKey 鎖的唯一標識
 */
const releaseLock = (lockKey: string): void => {
  sessionStorage.removeItem(lockKey);
  console.debug(`[SavedSearchExecution] 已釋放鎖 ${lockKey}`);
};

const SavedSearchExecution: React.FC<SavedSearchExecutionProps> = ({
  apiUrl,
  sessionId,
  searchId,
  currentSearch,
  sendBotMessage,
  setThinking,
  messages,
  isLoading,
  isThinking,
  clearMessages
}) => {
  // 追蹤已經發送歡迎訊息的搜索ID
  const welcomeSentRef = useRef<Set<string>>(new Set());
  const [isExecuting, setIsExecuting] = useState(false);
  const executionLockKey = useRef(`${LOCK_PREFIX}${sessionId}_${searchId}`);
  // 追蹤是否已經清空消息
  const [hasCleared, setHasCleared] = useState(false);
  const previousSearchIdRef = useRef<string | null>(null);
  // 保存當前處理的搜索信息，用於檢查是否匹配
  const processingSearchRef = useRef<{id: string, title: string} | null>(null);
  // 是否已經發送消息
  const [hasSentMessages, setHasSentMessages] = useState(false);
  // 追蹤執行階段
  const [executionPhase, setExecutionPhase] = useState<'idle' | 'kol-data' | 'llm-response'>('idle');

  // 在組件掛載時設置標誌
  useEffect(() => {
    console.debug(`[SavedSearchExecution] 組件已掛載，searchId=${searchId}, title=${currentSearch?.title}`);
    return () => {
      console.debug(`[SavedSearchExecution] 組件已卸載，searchId=${searchId}, title=${currentSearch?.title}`);
    };
  }, []);

  // 當 searchId 或 currentSearch 變更時，記錄日誌
  useEffect(() => {
    if (currentSearch) {
      console.debug(`[SavedSearchExecution] searchId 或 currentSearch 變更，searchId=${searchId}, title=${currentSearch.title}`);
    }
  }, [searchId, currentSearch]);

  // 查詢記錄數量
  const fetchRecordCount = useCallback(async (search: SavedSearch, signal?: AbortSignal): Promise<RecordCountResult> => {
    try {
      const { query } = search;
      const memCacheKey = `${sessionId}-${search.id}`;
      const sessionCacheKey = `kol_data_count_${sessionId}_${search.id}`;
      console.debug(`[SavedSearchExecution] 查詢記錄數量, 搜索: ${search.title}, 搜索ID: ${search.id}`);

      // 1. 先檢查內存快取
      const cachedData = kolDataCountCache[memCacheKey];
      if (cachedData && Date.now() - cachedData.timestamp < CACHE_EXPIRY) {
        console.debug('[SavedSearchExecution] 從內存快取讀取記錄數量數據');
        return cachedData.data;
      }

      // 2. 檢查 sessionStorage 快取
      const sessionCachedStr = sessionStorage.getItem(sessionCacheKey);
      if (sessionCachedStr) {
        try {
          const sessionCached = JSON.parse(sessionCachedStr);
          if (Date.now() - sessionCached.timestamp < CACHE_EXPIRY) {
            console.debug('[SavedSearchExecution] 從 sessionStorage 快取讀取記錄數量數據');

            // 同時更新內存快取
            kolDataCountCache[memCacheKey] = {
              data: sessionCached.data,
              timestamp: sessionCached.timestamp
            };

            return sessionCached.data;
          }
        } catch (e) {
          console.warn('[SavedSearchExecution] sessionStorage 快取數據解析失敗:', e);
        }
      }

      // 3. 都沒有快取或快取已過期，從API查詢
      console.debug('[SavedSearchExecution] 從API查詢記錄數量');

      // 創建請求選項
      const fetchOptions: RequestInit = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: search.title,
          time: query.time,
          source: query.source,
          tags: query.tags,
          query: query.query,
          n: query.n,
          range: query.range
        })
      };

      // 如果提供了signal，添加到options中
      if (signal) {
        fetchOptions.signal = signal;
      }

      const response = await fetchWithKey(
        `${apiUrl}/api/redis/kol-data-count`,
        fetchOptions
      );

      if (response.ok) {
        const data = await response.json();
        console.debug(`[SavedSearchExecution] 記錄數量結果:`, data);

        // 處理後端返回的數據格式
        const result = {
          count: data.count || 0,
          total: data.count || 0,
          start_datetime: data.start_datetime || "未知",
          end_datetime: data.end_datetime || "未知",
          source: query.source === 0 ? '全部' : query.source === 1 ? 'Facebook' : 'Threads',
          kol: query.tags && query.tags.includes('All') ? 'All' : query.tags.join(', ')
        };

        // 同時更新內存快取和 sessionStorage 快取
        const cacheData = {
          data: result,
          timestamp: Date.now()
        };

        kolDataCountCache[memCacheKey] = cacheData;
        sessionStorage.setItem(sessionCacheKey, JSON.stringify(cacheData));
        console.debug(`[SavedSearchExecution] 已更新快取：內存 ${memCacheKey} 和 sessionStorage ${sessionCacheKey}`);

        return result;
      } else {
        console.error(`[SavedSearchExecution] 查詢記錄數量失敗: ${response.status}`);
        // 預設的返回數據
        return {
          count: 0,
          total: 0,
          start_datetime: "未知",
          end_datetime: "未知",
          source: query.source === 0 ? '全部' : query.source === 1 ? 'Facebook' : 'Threads',
          kol: query.tags && query.tags.includes('All') ? 'All' : query.tags.join(', ')
        };
      }
    } catch (error) {
      // 如果是AbortError，則向上拋出以便caller可以處理
      if (error.name === 'AbortError') {
        throw error;
      }

      console.error('[SavedSearchExecution] 查詢記錄數量出錯:', error);
      const { query } = search;
      return {
        count: 0,
        total: 0,
        start_datetime: "未知",
        end_datetime: "未知",
        source: query.source === 0 ? '全部' : query.source === 1 ? 'Facebook' : 'Threads',
        kol: query.tags && query.tags.includes('All') ? 'All' : query.tags.join(', ')
      };
    }
  }, [apiUrl, sessionId]);

  // 查詢 KOL 資料
  const fetchKolData = useCallback(async (search: SavedSearch, signal?: AbortSignal) => {
    try {
      const { query } = search;
      console.debug(`[SavedSearchExecution] 查詢 KOL 資料, 搜索: ${search.title}`);

      // 設置執行階段為 kol-data
      setExecutionPhase('kol-data');
      console.log(`[DEBUG-KOL] 設置執行階段為 kol-data, 當前思考狀態: isThinking=${isThinking}`);

      // 設置思考狀態 - 直接使用 true 值，不依賴狀態更新
      setThinking(true);
      console.log(`[DEBUG-KOL] 設置思考狀態為 true`);

      console.debug(`[SavedSearchExecution] 正在思考中...獲取 KOL 資料`);

      // 創建請求選項
      const fetchOptions: RequestInit = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: search.title,
          time: query.time,
          source: query.source,
          tags: query.tags,
          query: query.query,
          n: query.n,
          range: query.range
        })
      };

      // 如果提供了signal，添加到options中
      if (signal) {
        fetchOptions.signal = signal;
      }

      // 根據技術文件使用正確的 API 端點和參數
      console.log(`[DEBUG-KOL] 發送 KOL 資料請求前思考狀態: isThinking=${isThinking}`);
      const response = await fetchWithKey(
        `${apiUrl}/api/redis/kol-data?session_id=${sessionId}&search_id=${searchId}`,
        fetchOptions
      );

      if (response.ok) {
        const data = await response.json();
        console.debug(`[SavedSearchExecution] KOL 資料查詢成功`);
        console.log(`[DEBUG-KOL] KOL 資料查詢成功後思考狀態: isThinking=${isThinking}`);

        // 檢查響應格式 - 根據文檔，應該是 markdown 字符串
        let markdownTable = "";
        if (typeof data === 'string') {
          // 直接使用返回的 markdown 字符串
          markdownTable = data;
        } else if (typeof data === 'object' && data.markdown) {
          // 如果返回包裝在 markdown 字段中
          markdownTable = data.markdown;
        } else {
          // 未知格式，嘗試將整個響應轉為 JSON 字符串
          markdownTable = "```json\n" + JSON.stringify(data, null, 2) + "\n```";
        }

        // 發送資料表格消息 - 但這裡不需要再發送到後端
        await sendBotMessage(markdownTable);
        console.log(`[DEBUG-KOL] 資料表格消息發送後思考狀態: isThinking=${isThinking}`);

        // 重要：不要在這裡設置 setThinking(false)，保持思考狀態
        // 直到 LLM 響應完成

        return true; // 返回成功標誌
      } else {
        console.error(`[SavedSearchExecution] 查詢 KOL 資料失敗: ${response.status}`);
        try {
          const errorData = await response.json();
          console.error('[SavedSearchExecution] 錯誤詳情:', errorData);
        } catch (e) {
          // 忽略錯誤
        }
        await sendBotMessage("抱歉，查詢 KOL 資料時發生錯誤，請稍後再試。");

        // 結束思考狀態
        console.log(`[DEBUG-KOL] 查詢失敗，結束思考狀態前: isThinking=${isThinking}`);
        setExecutionPhase('idle');
        setThinking(false);
        console.log(`[DEBUG-KOL] 查詢失敗，結束思考狀態後`);
        return false; // 返回失敗標誌
      }
    } catch (error) {
      // 如果是AbortError，則向上拋出以便caller可以處理
      if (error.name === 'AbortError') {
        console.debug(`[SavedSearchExecution] KOL 資料請求被取消`);
        setExecutionPhase('idle');
        setThinking(false);
        throw error;
      }

      console.error('[SavedSearchExecution] 查詢 KOL 資料出錯:', error);
      await sendBotMessage("抱歉，查詢 KOL 資料時發生錯誤，請稍後再試。");
      setExecutionPhase('idle');
      setThinking(false);
      return false; // 返回失敗標誌
    }
  }, [apiUrl, sendBotMessage, setThinking, sessionId, searchId, isThinking, executionPhase]);

  // 獲取 LLM 的回應
  const fetchLLMResponse = useCallback(async (search: SavedSearch, signal?: AbortSignal) => {
    try {
      const { query } = search;
      console.debug(`[SavedSearchExecution] 開始獲取 LLM 回應，searchId=${searchId}`);

      // 如果沒有查詢語句，直接返回默認消息
      if (!query.query) {
        console.debug(`[SavedSearchExecution] 沒有查詢語句，返回默認消息`);
        await sendBotMessage("資料已經提供了，你有想詢問什麼的都可以在下面問哦！");
        setExecutionPhase('idle');
        setThinking(false);
        return;
      }

      // 設置執行階段為 llm-response
      setExecutionPhase('llm-response');

      // 強制設置思考狀態為 true
      setThinking(true);
      console.log(`[DEBUG] LLM 回應強制設置思考狀態為 true`);

      console.debug(`[SavedSearchExecution] 正在思考中...處理 LLM 回應，查詢語句: ${query.query}`);

      // 創建請求選項
      const fetchOptions: RequestInit = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.query })
      };

      // 如果提供了signal，添加到options中
      if (signal) {
        fetchOptions.signal = signal;
      }

      // 發送 LLM 請求
      console.log(`[DEBUG] 發送 LLM 請求前思考狀態: isThinking=${isThinking}`);
      const response = await fetchWithKey(
        `${apiUrl}/api/message/kol-data-llm?session_id=${sessionId}&search_id=${searchId}`,
        fetchOptions
      );

      if (response.ok) {
        const data = await response.json();
        console.debug(`[SavedSearchExecution] LLM 回應成功:`, data);
        console.log(`[DEBUG] LLM 回應成功後思考狀態: isThinking=${isThinking}`);

        // 處理 LLM 回應
        let content = "";
        if (typeof data === 'object' && data.content) {
          content = data.content;
        } else if (typeof data === 'string') {
          content = data;
        } else {
          content = JSON.stringify(data);
        }

        // 發送 LLM 回應
        await sendBotMessage(content);

        // 添加結尾提示消息
        await sendBotMessage("你還有想詢問什麼的都可以在下面續問哦！");
      } else {
        console.error(`[SavedSearchExecution] LLM 回應請求失敗: ${response.status}`);
        await sendBotMessage("抱歉，我無法分析這些數據。你有其他問題嗎？");
      }

      // 完成所有處理，結束思考狀態
      console.log(`[DEBUG] LLM 回應完成前思考狀態: isThinking=${isThinking}`);
      setExecutionPhase('idle');
      setThinking(false);
      console.log(`[DEBUG] LLM 回應完成後思考狀態設置為 false`);
    } catch (error) {
      // 如果是AbortError，則向上拋出以便caller可以處理
      if (error.name === 'AbortError') {
        console.debug(`[SavedSearchExecution] LLM 請求被取消`);
        setExecutionPhase('idle');
        setThinking(false);
        throw error;
      }

      console.error('[SavedSearchExecution] 獲取 LLM 回應出錯:', error);
      await sendBotMessage("抱歉，處理數據時發生錯誤，請稍後再試。");
      setExecutionPhase('idle');
      setThinking(false);
    }
  }, [apiUrl, sessionId, searchId, sendBotMessage, setThinking, isThinking]);

  // 生成歡迎訊息
  const generateWelcomeMessage = useCallback((search: SavedSearch, result: RecordCountResult) => {
    const { title } = search;
    const recordCount = result.count || 0;

    // 根據記錄數量選擇不同的訊息
    if (recordCount > 0) {
      return `嗨！我找到了「${title}」的搜索資料啦！🎯✨

• 📅 這批資料的時間範圍是： ${result.start_datetime} ~ ${result.end_datetime}
• 💁 資料來源：${result.source || '全部'}
• 📊 涵蓋KOL：${result.kol || 'All'}

總共有 ${recordCount} 筆資料，我將呈現所有資料給你，請稍後！`;
    } else {
      return `嗨！我找到了「${title}」的搜索資料啦！🎯✨

• 📅 這批資料的時間範圍是： ${result.start_datetime} ~ ${result.end_datetime}
• 💁 資料來源：${result.source || '全部'}
• 📊 涵蓋KOL：${result.kol || 'All'}

總共有 0 筆資料，請確認是否資料庫裡已抓取該時間段與條件的資料，或是左側挑其他的搜尋條件執行！`;
    }
  }, []);

  // 檢查是否已經有歡迎訊息
  const hasWelcomeMessage = useCallback((currentSearch: SavedSearch, messages: Message[]) => {
    return messages.some(msg =>
      msg.role === 'bot' && msg.content.includes(`我找到了「${currentSearch.title}」的搜索資料啦！`)
    );
  }, []);

  // 執行搜索流程的更新
  const executeSearch = useCallback(async (currentProcessingSearchId: string, currentProcessingSearchTitle: string) => {
    // 嘗試獲取鎖
    if (!acquireLock(executionLockKey.current)) {
      // 獲取鎖失敗，可能有其他請求正在處理
      console.debug(`[SavedSearchExecution] 無法獲取執行鎖，跳過本次執行`);
      return;
    }

    try {
      setIsExecuting(true);
      console.debug(`[SavedSearchExecution] 成功獲取鎖，開始執行搜索: ${currentProcessingSearchId}, 標題: ${currentProcessingSearchTitle}`);

      // 標記為已發送，避免重複發送
      welcomeSentRef.current.add(currentProcessingSearchId);

      // 查詢記錄數量
      const recordCountResult = await fetchRecordCount(currentSearch!);
      console.debug(`[SavedSearchExecution] 記錄數量結果:`, recordCountResult);

      // 創建歡迎訊息
      const welcomeMessage = generateWelcomeMessage(currentSearch!, recordCountResult);
      console.debug(`[SavedSearchExecution] 為搜索 ${currentProcessingSearchId} 創建歡迎訊息`);
      await sendBotMessage(welcomeMessage);
      setHasSentMessages(true);

      // 如果有記錄，自動查詢 KOL 資料並呈現
      if (recordCountResult.count > 0) {
        // 設置思考狀態為 true
        setThinking(true);
        console.log(`[DEBUG-EXECUTE] 開始執行 KOL 查詢前，設置思考狀態為 true`);

        // 查詢 KOL 資料
        const kolDataSuccess = await fetchKolData(currentSearch!);
        setHasSentMessages(true);

        // 如果 KOL 數據查詢成功，繼續獲取 LLM 回應
        if (kolDataSuccess) {
          console.debug(`[SavedSearchExecution] KOL 資料查詢成功，即將獲取 LLM 回應`);

          // 檢查當前思考狀態
          console.log(`[DEBUG-EXECUTE] KOL 資料查詢成功後，LLM 回應前: isThinking=${isThinking}, executionPhase=${executionPhase}`);

          // 確保思考狀態為 true
          setThinking(true);
          setExecutionPhase('llm-response');
          console.log(`[DEBUG-EXECUTE] 重新設置思考狀態為 true, executionPhase=llm-response`);

          await fetchLLMResponse(currentSearch!);
        }
      }
    } catch (error) {
      console.error('[SavedSearchExecution] 執行搜索出錯:', error);
      // 出錯時，從已發送列表中移除，以便下次可以重試
      welcomeSentRef.current.delete(currentProcessingSearchId);
      // 確保思考狀態被關閉
      setExecutionPhase('idle');
      setThinking(false);
    } finally {
      // 釋放鎖
      releaseLock(executionLockKey.current);
      setIsExecuting(false);
      // 確保思考狀態被關閉
      setExecutionPhase('idle');
      setThinking(false);
    }
  }, [fetchRecordCount, generateWelcomeMessage, fetchKolData, fetchLLMResponse, currentSearch, sendBotMessage, setThinking, isThinking, executionPhase]);

  // 當 searchId 變更時，處理搜索執行邏輯
  useEffect(() => {
    // 如果是初始頁面或沒有當前搜索信息，則跳過
    if (searchId === "999" || !currentSearch) {
      console.debug(`[SavedSearchExecution] 跳過執行: searchId=${searchId} 是初始值或沒有 currentSearch`);
      return;
    }

    // 檢查searchId是否真的變更了，避免重複執行
    if (previousSearchIdRef.current === searchId) {
      console.debug(`[SavedSearchExecution] 跳過執行: searchId=${searchId} 與前一次相同`);
      return;
    }

    // 更新前一個searchId的引用
    previousSearchIdRef.current = searchId;

    // 更新鎖的key
    executionLockKey.current = `${LOCK_PREFIX}${sessionId}_${searchId}`;

    console.debug(`[SavedSearchExecution] searchId變更為${searchId}，開始處理，標題:${currentSearch.title}`);

    // 清空消息列表，避免舊消息與新消息混合 - 只清空一次
    if (!hasCleared) {
      clearMessages();
      setHasCleared(true);
    }

    // 檢查是否已經在 welcomeSentRef 中標記為已發送
    if (welcomeSentRef.current.has(searchId)) {
      console.debug(`[SavedSearchExecution] 已在記憶體中標記搜索 ${searchId} 的歡迎訊息，跳過執行`);
      return;
    }

    // 檢查消息列表中是否已經有此搜索的歡迎訊息
    const hasWelcome = messages.some(msg =>
      msg.role === 'bot' && msg.content.includes(`我找到了「${currentSearch.title}」的搜索資料啦！`)
    );
    if (hasWelcome) {
      console.debug(`[SavedSearchExecution] 消息列表中已有搜索 ${searchId} 的歡迎訊息，標記為已發送並跳過執行`);
      welcomeSentRef.current.add(searchId);
      return;
    }

    // 當 messages 加載完成後執行，不要在isLoading時執行
    if (!isLoading) {
      console.debug(`[SavedSearchExecution] messages已加載完成，開始執行搜索`);
      // 保存當前要處理的搜索信息
      const currentProcessingSearchId = searchId;
      const currentProcessingSearchTitle = currentSearch.title;

      processingSearchRef.current = {
        id: currentProcessingSearchId,
        title: currentProcessingSearchTitle
      };

      // 執行搜索
      executeSearch(currentProcessingSearchId, currentProcessingSearchTitle);
    } else {
      console.debug(`[SavedSearchExecution] messages還在加載中，暫不執行搜索`);
    }

    // 當組件卸載或searchId變更時清理
    return () => {
      console.debug(`[SavedSearchExecution] 清理舊的搜索執行，searchId=${searchId}`);
      // 確保思考狀態被關閉
      setExecutionPhase('idle');
      setThinking(false);
    };
  }, [searchId, sessionId, currentSearch, isLoading, messages, clearMessages, hasCleared, executeSearch, setThinking]);

  // 監視執行階段變化
  useEffect(() => {
    console.debug(`[SavedSearchExecution] 執行階段變更為: ${executionPhase}`);

    // 確保思考狀態與執行階段同步
    if (executionPhase !== 'idle' && !isThinking) {
      console.debug(`[SavedSearchExecution] 執行階段不為 idle 但思考狀態未開啟，重新設置`);
      setThinking(true);
    } else if (executionPhase === 'idle' && isThinking) {
      console.debug(`[SavedSearchExecution] 執行階段為 idle 但思考狀態仍開啟，關閉思考狀態`);
      setThinking(false);
    }
  }, [executionPhase, isThinking, setThinking]);

  // 當搜索ID變更時，重置hasCleared狀態
  useEffect(() => {
    setHasCleared(false);
    setHasSentMessages(false);
  }, [searchId]);

  // 監視消息列表變化
  useEffect(() => {
    if (messages.length > 0 && !hasSentMessages) {
      console.debug(`[SavedSearchExecution] 檢測到消息列表已有 ${messages.length} 條消息，但組件尚未發送過消息`);
    }
  }, [messages, hasSentMessages]);

  // 組件卸載時清理
  useEffect(() => {
    return () => {
      // 如果組件卸載，釋放可能持有的鎖
      if (executionLockKey.current) {
        releaseLock(executionLockKey.current);
      }
      // 清除所有引用
      processingSearchRef.current = null;
    };
  }, []);

  // 監聽 forceExecuteSearch event，收到就強制執行 executeSearch
  useEffect(() => {
    const handler = (event: CustomEvent) => {
      if (
        event.detail &&
        event.detail.searchId === searchId &&
        event.detail.forceClean
      ) {
        console.debug('[SavedSearchExecution] 收到 forceExecuteSearch event, 強制執行 executeSearch');
        executeSearch(searchId, currentSearch?.title || '');
      }
    };
    window.addEventListener('forceExecuteSearch', handler as EventListener);
    return () => window.removeEventListener('forceExecuteSearch', handler as EventListener);
  }, [searchId, currentSearch, executeSearch]);

  return null; // 這是一個邏輯組件，不需要渲染UI
};

export default SavedSearchExecution;
