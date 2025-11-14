/**
 * 模型訓練邏輯模組
 * 處理訓練表單提交、API 呼叫、進度輪詢、結果顯示
 */

import { apiGet, apiPost } from './api.js';

// 全域變數
let currentTaskId = null;
let progressInterval = null;

// DOM 元素
const trainingForm = document.getElementById('training-form');
const dataFileSelect = document.getElementById('data-file-select');
const modelNameInput = document.getElementById('model-name');
const predictionDaysInput = document.getElementById('prediction-days');
const startTrainingBtn = document.getElementById('start-training-btn');
const progressCard = document.getElementById('training-progress-card');
const resultCard = document.getElementById('training-result-card');
const modelsListDiv = document.getElementById('models-list');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadDataFiles();
    loadModels();
    setupFormHandler();
});

/**
 * 載入資料檔案列表
 */
async function loadDataFiles() {
    try {
        const response = await apiGet('/data/files');
        const dataFiles = response.data || [];

        dataFileSelect.innerHTML = '<option value="">-- 請選擇資料檔案 --</option>';

        if (dataFiles.length === 0) {
            dataFileSelect.innerHTML += '<option value="" disabled>尚無資料檔案，請先上傳</option>';
            return;
        }

        dataFiles.forEach(file => {
            const option = document.createElement('option');
            option.value = file.fileId;
            option.textContent = `${file.fileName} (${file.rowCount} 筆資料)`;
            dataFileSelect.appendChild(option);
        });
    } catch (error) {
        showAlert('載入資料檔案失敗: ' + error.message, 'error');
    }
}

/**
 * 載入已訓練模型列表
 */
async function loadModels() {
    try {
        const response = await apiGet('/models');
        const models = response.data || [];

        if (models.length === 0) {
            modelsListDiv.innerHTML = '<p style="color: #7f8c8d;">尚未訓練任何模型</p>';
            return;
        }

        let html = '<table style="width: 100%; border-collapse: collapse;">';
        html += '<thead><tr style="background: #ecf0f1;">';
        html += '<th style="padding: 0.75rem; text-align: left;">模型名稱</th>';
        html += '<th style="padding: 0.75rem; text-align: left;">訓練時間</th>';
        html += '<th style="padding: 0.75rem; text-align: left;">預測天數</th>';
        html += '<th style="padding: 0.75rem; text-align: left;">驗證損失</th>';
        html += '<th style="padding: 0.75rem; text-align: left;">狀態</th>';
        html += '</tr></thead><tbody>';

        models.forEach(model => {
            const trainedAt = new Date(model.trainedAt).toLocaleString('zh-TW');
            html += '<tr style="border-bottom: 1px solid #ecf0f1;">';
            html += `<td style="padding: 0.75rem;">${model.modelName}</td>`;
            html += `<td style="padding: 0.75rem;">${trainedAt}</td>`;
            html += `<td style="padding: 0.75rem;">${model.predictionDays} 天</td>`;
            html += `<td style="padding: 0.75rem;">${model.metrics.valLoss.toFixed(4)}</td>`;
            html += `<td style="padding: 0.75rem;"><span style="color: #27ae60;">● 就緒</span></td>`;
            html += '</tr>';
        });

        html += '</tbody></table>';
        modelsListDiv.innerHTML = html;
    } catch (error) {
        modelsListDiv.innerHTML = '<p style="color: #e74c3c;">載入模型失敗: ' + error.message + '</p>';
    }
}

/**
 * 設定表單處理
 */
function setupFormHandler() {
    trainingForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const dataFileId = dataFileSelect.value;
        const modelName = modelNameInput.value.trim();
        const predictionDays = parseInt(predictionDaysInput.value);

        if (!dataFileId || !modelName || !predictionDays) {
            showAlert('請填寫所有必要欄位', 'error');
            return;
        }

        // 禁用表單
        startTrainingBtn.disabled = true;
        startTrainingBtn.textContent = '啟動中...';

        try {
            // 啟動訓練
            const response = await apiPost('/models/train', {
                dataFileId,
                modelName,
                predictionDays,
            });

            currentTaskId = response.data.taskId;

            // 顯示進度卡片
            progressCard.classList.remove('hidden');
            resultCard.classList.add('hidden');

            document.getElementById('task-id').textContent = currentTaskId;

            // 開始輪詢進度
            startProgressPolling();

            showAlert('訓練任務已啟動！', 'success');
        } catch (error) {
            showAlert('啟動訓練失敗: ' + error.message, 'error');
            startTrainingBtn.disabled = false;
            startTrainingBtn.textContent = '開始訓練';
        }
    });
}

/**
 * 開始輪詢訓練進度
 */
function startProgressPolling() {
    // 清除舊的輪詢
    if (progressInterval) {
        clearInterval(progressInterval);
    }

    // 每 2 秒輪詢一次
    progressInterval = setInterval(async () => {
        try {
            const response = await apiGet(`/models/training/tasks/${currentTaskId}`);
            const task = response.data;

            updateProgress(task);

            // 若訓練完成或失敗，停止輪詢
            if (task.status === 'completed' || task.status === 'failed') {
                clearInterval(progressInterval);
                handleTrainingComplete(task);
            }
        } catch (error) {
            console.error('輪詢進度失敗:', error);
        }
    }, 2000);
}

/**
 * 更新進度顯示
 */
function updateProgress(task) {
    document.getElementById('task-status').textContent = getStatusText(task.status);

    if (task.progress) {
        document.getElementById('current-epoch').textContent = task.progress.currentEpoch;
        document.getElementById('total-epochs').textContent = task.progress.totalEpochs;
        document.getElementById('train-loss').textContent = task.progress.currentLoss.toFixed(4);
        document.getElementById('val-loss').textContent = task.progress.currentValLoss.toFixed(4);
    }
}

/**
 * 處理訓練完成
 */
function handleTrainingComplete(task) {
    // 隱藏進度
    document.getElementById('training-spinner').classList.add('hidden');

    // 顯示結果
    resultCard.classList.remove('hidden');

    if (task.status === 'completed') {
        const resultHtml = `
            <div class="alert alert-success">
                ✅ 訓練完成！
            </div>
            <p><strong>模型 ID:</strong> ${task.resultModelId}</p>
            <p><strong>訓練時間:</strong> ${task.duration.toFixed(2)} 秒</p>
            <p>模型已儲存，可在「預測執行」頁面使用</p>
        `;
        document.getElementById('result-info').innerHTML = resultHtml;

        // 重新載入模型列表
        setTimeout(loadModels, 1000);
    } else {
        const resultHtml = `
            <div class="alert alert-error">
                ❌ 訓練失敗
            </div>
            <p><strong>錯誤訊息:</strong> ${task.error}</p>
        `;
        document.getElementById('result-info').innerHTML = resultHtml;
    }

    // 重新啟用表單
    startTrainingBtn.disabled = false;
    startTrainingBtn.textContent = '開始訓練';
}

/**
 * 取得狀態文字
 */
function getStatusText(status) {
    const statusMap = {
        'pending': '等待中',
        'running': '訓練中',
        'completed': '已完成',
        'failed': '失敗',
    };
    return statusMap[status] || status;
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
