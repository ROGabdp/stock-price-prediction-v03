/**
 * API 呼叫封裝模組
 * 提供 Fetch API 封裝、錯誤處理、baseURL 配置
 */

// API 基礎 URL
const BASE_URL = 'http://localhost:5000/api';

/**
 * API 回應介面
 * @typedef {Object} ApiResponse
 * @property {boolean} success - 是否成功
 * @property {*} data - 回應資料
 * @property {string} [error] - 錯誤訊息
 */

/**
 * 發送 GET 請求
 * @param {string} endpoint - API 端點 (例如: '/models')
 * @returns {Promise<ApiResponse>} API 回應
 */
async function apiGet(endpoint) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP 錯誤: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('GET 請求失敗:', error);
        throw error;
    }
}

/**
 * 發送 POST 請求
 * @param {string} endpoint - API 端點
 * @param {Object} body - 請求 body
 * @returns {Promise<ApiResponse>} API 回應
 */
async function apiPost(endpoint, body) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP 錯誤: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('POST 請求失敗:', error);
        throw error;
    }
}

/**
 * 發送 POST 請求（FormData，用於檔案上傳）
 * @param {string} endpoint - API 端點
 * @param {FormData} formData - FormData 物件
 * @returns {Promise<ApiResponse>} API 回應
 */
async function apiPostFormData(endpoint, formData) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData,
            // 不設定 Content-Type，讓瀏覽器自動設定（包含 boundary）
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP 錯誤: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('POST FormData 請求失敗:', error);
        throw error;
    }
}

/**
 * 發送 DELETE 請求
 * @param {string} endpoint - API 端點
 * @returns {Promise<ApiResponse>} API 回應
 */
async function apiDelete(endpoint) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP 錯誤: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error('DELETE 請求失敗:', error);
        throw error;
    }
}

/**
 * 檢查伺服器健康狀態
 * @returns {Promise<boolean>} 伺服器是否正常
 */
async function checkServerHealth() {
    try {
        const response = await apiGet('/health');
        return response.success !== false;
    } catch (error) {
        console.error('伺服器健康檢查失敗:', error);
        return false;
    }
}

// 匯出 API 函式
export { apiGet, apiPost, apiPostFormData, apiDelete, checkServerHealth };
