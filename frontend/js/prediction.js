/**
 * 預測邏輯模組
 * 處理表單提交、API 呼叫、圖表渲染
 */

import { apiGet, apiPost } from './api.js';
import { renderPredictionChart, renderPredictionTable } from './chart-renderer.js';

// DOM 元素
const predictionForm = document.getElementById('prediction-form');
const modelSelect = document.getElementById('model-select');
const dataFileSelect = document.getElementById('data-file-select');
const startDateInput = document.getElementById('start-date');
const predictBtn = document.getElementById('predict-btn');
const resultCard = document.getElementById('result-card');
const modelInfoDiv = document.getElementById('model-info');

let currentChart = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadModels();
    loadDataFiles();
    setupFormHandler();
    setupModelSelectHandler();
});

/**
 * 載入模型列表
 */
async function loadModels() {
    try {
        const response = await apiGet('/models');
        const models = response.data || [];

        modelSelect.innerHTML = '<option value="">-- 請選擇已訓練的模型 --</option>';

        if (models.length === 0) {
            modelSelect.innerHTML += '<option value="" disabled>尚無已訓練模型</option>';
            return;
        }

        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.modelId;
            option.textContent = `${model.modelName} (預測 ${model.predictionDays} 天)`;
            option.dataset.model = JSON.stringify(model);
            modelSelect.appendChild(option);
        });
    } catch (error) {
        showAlert('載入模型失敗: ' + error.message, 'error');
    }
}

/**
 * 載入資料檔案列表
 */
async function loadDataFiles() {
    try {
        const response = await apiGet('/data/files');
        const dataFiles = response.data || [];

        dataFileSelect.innerHTML = '<option value="">-- 請選擇資料檔案 --</option>';

        if (dataFiles.length === 0) {
            dataFileSelect.innerHTML += '<option value="" disabled>尚無資料檔案</option>';
            return;
        }

        dataFiles.forEach(file => {
            const option = document.createElement('option');
            option.value = file.fileId;
            option.textContent = `${file.fileName} (${file.dateRange.start} ~ ${file.dateRange.end})`;
            dataFileSelect.appendChild(option);
        });
    } catch (error) {
        showAlert('載入資料檔案失敗: ' + error.message, 'error');
    }
}

/**
 * 設定模型選擇處理
 */
function setupModelSelectHandler() {
    modelSelect.addEventListener('change', (e) => {
        if (e.target.value) {
            const modelData = JSON.parse(e.target.selectedOptions[0].dataset.model);
            displayModelInfo(modelData);
        } else {
            modelInfoDiv.classList.add('hidden');
        }
    });
}

/**
 * 顯示模型資訊
 */
function displayModelInfo(model) {
    const html = `
        <strong>模型資訊:</strong><br>
        訓練時間: ${new Date(model.trainedAt).toLocaleString('zh-TW')}<br>
        預測天數: ${model.predictionDays} 天<br>
        驗證損失: ${model.metrics.valLoss.toFixed(4)}<br>
        驗證 MAE: ${model.metrics.valMAE.toFixed(4)}
    `;
    modelInfoDiv.innerHTML = html;
    modelInfoDiv.classList.remove('hidden');
}

/**
 * 設定表單處理
 */
function setupFormHandler() {
    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const modelId = modelSelect.value;
        const dataFileId = dataFileSelect.value;
        const startDate = startDateInput.value;

        if (!modelId || !dataFileId || !startDate) {
            showAlert('請填寫所有必要欄位', 'error');
            return;
        }

        // 禁用按鈕
        predictBtn.disabled = true;
        predictBtn.textContent = '預測中...';

        try {
            // 執行預測
            const response = await apiPost('/predict', {
                modelId,
                dataFileId,
                startDate,
            });

            const result = response.data;

            // 顯示結果
            displayPredictionResult(result);

            showAlert('預測完成！', 'success');
        } catch (error) {
            showAlert('預測失敗: ' + error.message, 'error');
        } finally {
            predictBtn.disabled = false;
            predictBtn.textContent = '開始預測';
        }
    });
}

/**
 * 顯示預測結果
 */
function displayPredictionResult(result) {
    // 顯示結果卡片
    resultCard.classList.remove('hidden');

    // 銷毀舊圖表
    if (currentChart) {
        currentChart.destroy();
    }

    // 渲染圖表
    currentChart = renderPredictionChart(
        'prediction-chart',
        result.historicalData,
        result.predictions
    );

    // 渲染預測詳情表格
    const tableHtml = renderPredictionTable(result.predictions);
    document.getElementById('prediction-details').innerHTML = tableHtml;

    // 顯示元資料
    const metadataHtml = `
        <strong>預測資訊:</strong><br>
        模型: ${result.requestInfo.modelName}<br>
        預測天數: ${result.requestInfo.predictionDays} 天<br>
        預測時間: ${new Date(result.metadata.predictedAt).toLocaleString('zh-TW')}<br>
        執行耗時: ${result.metadata.executionTime} 秒
    `;
    document.getElementById('result-metadata').innerHTML = metadataHtml;

    // 捲動到結果
    resultCard.scrollIntoView({ behavior: 'smooth' });
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
