/**
 * 資料管理模組
 * 處理檔案上傳、列表顯示、刪除
 */

import { apiGet } from './api.js';

// DOM 元素
const uploadForm = document.getElementById('upload-form');
const csvFileInput = document.getElementById('csv-file');
const uploadBtn = document.getElementById('upload-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const dataFilesTable = document.getElementById('data-files-table');
const dataFilesTbody = document.getElementById('data-files-tbody');
const noDataMessage = document.getElementById('no-data-message');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadDataFiles();
    setupUploadHandler();
});

/**
 * 載入資料檔案列表
 */
async function loadDataFiles() {
    try {
        // 顯示載入指示器
        loadingIndicator.classList.remove('hidden');
        dataFilesTable.classList.add('hidden');
        noDataMessage.classList.add('hidden');

        const response = await apiGet('/data/files');
        const dataFiles = response.data || [];

        if (dataFiles.length === 0) {
            noDataMessage.classList.remove('hidden');
        } else {
            renderDataFilesTable(dataFiles);
            dataFilesTable.classList.remove('hidden');
        }
    } catch (error) {
        showAlert('載入資料檔案失敗: ' + error.message, 'error');
        noDataMessage.classList.remove('hidden');
    } finally {
        loadingIndicator.classList.add('hidden');
    }
}

/**
 * 渲染資料檔案表格
 */
function renderDataFilesTable(dataFiles) {
    dataFilesTbody.innerHTML = '';

    // 按上傳時間倒序排列
    const sortedFiles = dataFiles.sort((a, b) => {
        return new Date(b.uploadedAt) - new Date(a.uploadedAt);
    });

    sortedFiles.forEach(file => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #ecf0f1';

        // 檔案名稱
        const nameCell = document.createElement('td');
        nameCell.style.padding = '0.75rem';
        nameCell.textContent = file.originalFileName || file.fileName;
        row.appendChild(nameCell);

        // 日期範圍
        const dateRangeCell = document.createElement('td');
        dateRangeCell.style.padding = '0.75rem';
        dateRangeCell.style.textAlign = 'center';
        dateRangeCell.textContent = `${file.dateRange.start} ~ ${file.dateRange.end}`;
        row.appendChild(dateRangeCell);

        // 資料筆數
        const rowCountCell = document.createElement('td');
        rowCountCell.style.padding = '0.75rem';
        rowCountCell.style.textAlign = 'center';
        rowCountCell.textContent = file.rowCount.toLocaleString();
        row.appendChild(rowCountCell);

        // 檔案大小
        const sizeCell = document.createElement('td');
        sizeCell.style.padding = '0.75rem';
        sizeCell.style.textAlign = 'center';
        sizeCell.textContent = formatFileSize(file.fileSizeBytes);
        row.appendChild(sizeCell);

        // 上傳時間
        const uploadedAtCell = document.createElement('td');
        uploadedAtCell.style.padding = '0.75rem';
        uploadedAtCell.style.textAlign = 'center';
        uploadedAtCell.textContent = new Date(file.uploadedAt).toLocaleString('zh-TW');
        row.appendChild(uploadedAtCell);

        // 狀態
        const statusCell = document.createElement('td');
        statusCell.style.padding = '0.75rem';
        statusCell.style.textAlign = 'center';
        const statusBadge = createStatusBadge(file.status);
        statusCell.appendChild(statusBadge);
        row.appendChild(statusCell);

        // 操作
        const actionCell = document.createElement('td');
        actionCell.style.padding = '0.75rem';
        actionCell.style.textAlign = 'center';

        if (file.status === 'valid') {
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-danger';
            deleteBtn.style.padding = '0.25rem 0.5rem';
            deleteBtn.style.fontSize = '0.875rem';
            deleteBtn.textContent = '刪除';
            deleteBtn.onclick = () => confirmDelete(file.fileId, file.originalFileName || file.fileName);
            actionCell.appendChild(deleteBtn);
        } else {
            actionCell.textContent = '-';
        }

        row.appendChild(actionCell);

        dataFilesTbody.appendChild(row);
    });
}

/**
 * 建立狀態徽章
 */
function createStatusBadge(status) {
    const badge = document.createElement('span');
    badge.style.padding = '0.25rem 0.5rem';
    badge.style.borderRadius = '4px';
    badge.style.fontSize = '0.875rem';
    badge.style.fontWeight = 'bold';

    if (status === 'valid') {
        badge.style.background = '#d4edda';
        badge.style.color = '#155724';
        badge.textContent = '有效';
    } else if (status === 'invalid') {
        badge.style.background = '#f8d7da';
        badge.style.color = '#721c24';
        badge.textContent = '無效';
    } else {
        badge.style.background = '#d1ecf1';
        badge.style.color = '#0c5460';
        badge.textContent = status;
    }

    return badge;
}

/**
 * 格式化檔案大小
 */
function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + ' B';
    } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(2) + ' KB';
    } else {
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }
}

/**
 * 設定上傳處理
 */
function setupUploadHandler() {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const file = csvFileInput.files[0];

        if (!file) {
            showAlert('請選擇檔案', 'error');
            return;
        }

        if (!file.name.endsWith('.csv')) {
            showAlert('請上傳 CSV 檔案', 'error');
            return;
        }

        // 禁用按鈕
        uploadBtn.disabled = true;
        uploadBtn.textContent = '上傳中...';

        try {
            // 建立 FormData
            const formData = new FormData();
            formData.append('file', file);

            // 上傳檔案
            const response = await fetch('http://localhost:5000/api/data/upload', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP 錯誤: ${response.status}`);
            }

            showAlert('檔案上傳成功！', 'success');

            // 清空表單
            uploadForm.reset();

            // 重新載入列表
            await loadDataFiles();

        } catch (error) {
            showAlert('上傳失敗: ' + error.message, 'error');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.textContent = '上傳檔案';
        }
    });
}

/**
 * 確認刪除
 */
function confirmDelete(fileId, fileName) {
    if (!confirm(`確定要刪除資料檔案「${fileName}」嗎？\n\n此操作無法復原。`)) {
        return;
    }

    deleteDataFile(fileId);
}

/**
 * 刪除資料檔案
 */
async function deleteDataFile(fileId) {
    try {
        const response = await fetch(`http://localhost:5000/api/data/files/${fileId}`, {
            method: 'DELETE',
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `HTTP 錯誤: ${response.status}`);
        }

        showAlert('資料檔案已刪除', 'success');

        // 重新載入列表
        await loadDataFiles();

    } catch (error) {
        showAlert('刪除失敗: ' + error.message, 'error');
    }
}

/**
 * 顯示提示訊息
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
