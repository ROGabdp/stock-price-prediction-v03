/**
 * 前端工具模組
 * 提供日期格式化、錯誤提示、載入中狀態、表單驗證等輔助函式
 */

/**
 * 格式化日期為 YYYY-MM-DD
 * @param {Date|string} date - 日期物件或字串
 * @returns {string} 格式化後的日期字串
 */
export function formatDate(date) {
    if (!date) return '';

    const d = typeof date === 'string' ? new Date(date) : date;

    if (isNaN(d.getTime())) {
        return '';
    }

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
}

/**
 * 格式化日期時間為本地化字串
 * @param {Date|string} datetime - 日期時間物件或字串
 * @returns {string} 格式化後的日期時間字串
 */
export function formatDateTime(datetime) {
    if (!datetime) return '';

    const d = typeof datetime === 'string' ? new Date(datetime) : datetime;

    if (isNaN(d.getTime())) {
        return '';
    }

    return d.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
}

/**
 * 顯示提示訊息
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 (success, error, warning, info)
 * @param {number} duration - 顯示時間（毫秒），預設 5000ms
 */
export function showAlert(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.maxWidth = '500px';
    alertDiv.style.padding = '1rem';
    alertDiv.style.borderRadius = '4px';
    alertDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
    alertDiv.style.animation = 'slideInRight 0.3s ease-out';

    // 設定背景顏色
    const colors = {
        success: { bg: '#d4edda', color: '#155724', border: '#c3e6cb' },
        error: { bg: '#f8d7da', color: '#721c24', border: '#f5c6cb' },
        warning: { bg: '#fff3cd', color: '#856404', border: '#ffeaa7' },
        info: { bg: '#d1ecf1', color: '#0c5460', border: '#bee5eb' },
    };

    const colorScheme = colors[type] || colors.info;
    alertDiv.style.background = colorScheme.bg;
    alertDiv.style.color = colorScheme.color;
    alertDiv.style.border = `1px solid ${colorScheme.border}`;

    document.body.appendChild(alertDiv);

    // 自動移除
    setTimeout(() => {
        alertDiv.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => alertDiv.remove(), 300);
    }, duration);
}

/**
 * 顯示載入中狀態
 * @param {HTMLElement} element - 要顯示載入狀態的元素
 * @param {boolean} loading - 是否載入中
 * @param {string} loadingText - 載入中顯示的文字
 */
export function setLoading(element, loading, loadingText = '載入中...') {
    if (!element) return;

    if (loading) {
        element.disabled = true;
        element.dataset.originalText = element.textContent;
        element.textContent = loadingText;
        element.style.opacity = '0.6';
        element.style.cursor = 'not-allowed';
    } else {
        element.disabled = false;
        element.textContent = element.dataset.originalText || element.textContent;
        element.style.opacity = '1';
        element.style.cursor = 'pointer';
    }
}

/**
 * 驗證表單欄位
 * @param {HTMLFormElement} form - 表單元素
 * @returns {Object} { isValid: boolean, errors: string[] }
 */
export function validateForm(form) {
    const errors = [];

    if (!form) {
        return { isValid: false, errors: ['表單不存在'] };
    }

    // 檢查必填欄位
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value || field.value.trim() === '') {
            const label = form.querySelector(`label[for="${field.id}"]`);
            const fieldName = label ? label.textContent.replace('*', '').trim() : field.name;
            errors.push(`${fieldName} 為必填欄位`);
        }
    });

    // 檢查數字欄位
    const numberFields = form.querySelectorAll('input[type="number"]');

    numberFields.forEach(field => {
        if (field.value && isNaN(Number(field.value))) {
            const label = form.querySelector(`label[for="${field.id}"]`);
            const fieldName = label ? label.textContent.replace('*', '').trim() : field.name;
            errors.push(`${fieldName} 必須為數字`);
        }

        // 檢查 min/max
        if (field.value) {
            const value = Number(field.value);
            if (field.min && value < Number(field.min)) {
                const label = form.querySelector(`label[for="${field.id}"]`);
                const fieldName = label ? label.textContent.replace('*', '').trim() : field.name;
                errors.push(`${fieldName} 不可小於 ${field.min}`);
            }
            if (field.max && value > Number(field.max)) {
                const label = form.querySelector(`label[for="${field.id}"]`);
                const fieldName = label ? label.textContent.replace('*', '').trim() : field.name;
                errors.push(`${fieldName} 不可大於 ${field.max}`);
            }
        }
    });

    return {
        isValid: errors.length === 0,
        errors: errors,
    };
}

/**
 * 格式化檔案大小
 * @param {number} bytes - 檔案大小（bytes）
 * @returns {string} 格式化後的大小字串
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    if (!bytes) return 'N/A';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 清空表單
 * @param {HTMLFormElement} form - 表單元素
 */
export function clearForm(form) {
    if (!form) return;
    form.reset();
}

/**
 * 確認對話框
 * @param {string} message - 確認訊息
 * @returns {boolean} 使用者是否確認
 */
export function confirmAction(message) {
    return confirm(message);
}

/**
 * 顯示/隱藏元素
 * @param {HTMLElement} element - 元素
 * @param {boolean} visible - 是否顯示
 */
export function setVisible(element, visible) {
    if (!element) return;

    if (visible) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

/**
 * 防抖函式
 * @param {Function} func - 要執行的函式
 * @param {number} wait - 等待時間（毫秒）
 * @returns {Function} 防抖後的函式
 */
export function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
