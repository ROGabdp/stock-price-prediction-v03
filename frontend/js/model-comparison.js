/**
 * 模型比較模組
 * 處理模型選擇、比較請求、結果視覺化
 */

import { apiGet, apiPost } from './api.js';

// DOM 元素
const comparisonForm = document.getElementById('comparison-form');
const modelCheckboxes = document.getElementById('model-checkboxes');
const compareBtn = document.getElementById('compare-btn');
const resultCard = document.getElementById('result-card');
const bestModelInfo = document.getElementById('best-model-info');
const comparisonTableContainer = document.getElementById('comparison-table-container');

let currentChart = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadModels();
    setupComparisonHandler();
});

/**
 * 載入模型列表
 */
async function loadModels() {
    try {
        const response = await apiGet('/models');
        const models = response.data || [];

        // 過濾出狀態為 ready 的模型
        const readyModels = models.filter(m => m.status === 'ready');

        if (readyModels.length === 0) {
            modelCheckboxes.innerHTML = '<p style="color: #7f8c8d;">尚無可比較的模型</p>';
            compareBtn.disabled = true;
            return;
        }

        // 建立 checkbox 列表
        modelCheckboxes.innerHTML = '';

        readyModels.forEach(model => {
            const checkboxDiv = document.createElement('div');
            checkboxDiv.style.marginBottom = '0.5rem';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `model-${model.modelId}`;
            checkbox.value = model.modelId;
            checkbox.style.marginRight = '0.5rem';

            const label = document.createElement('label');
            label.htmlFor = `model-${model.modelId}`;
            label.style.cursor = 'pointer';
            label.textContent = `${model.modelName} (預測 ${model.predictionDays} 天, 驗證損失: ${model.metrics.valLoss.toFixed(4)})`;

            checkboxDiv.appendChild(checkbox);
            checkboxDiv.appendChild(label);
            modelCheckboxes.appendChild(checkboxDiv);
        });

    } catch (error) {
        showAlert('載入模型列表失敗: ' + error.message, 'error');
    }
}

/**
 * 設定比較處理
 */
function setupComparisonHandler() {
    comparisonForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 取得選中的模型 ID
        const checkboxes = modelCheckboxes.querySelectorAll('input[type="checkbox"]:checked');
        const modelIds = Array.from(checkboxes).map(cb => cb.value);

        if (modelIds.length < 2) {
            showAlert('請至少選擇 2 個模型', 'error');
            return;
        }

        if (modelIds.length > 10) {
            showAlert('最多只能同時比較 10 個模型', 'error');
            return;
        }

        // 禁用按鈕
        compareBtn.disabled = true;
        compareBtn.textContent = '比較中...';

        try {
            // 執行比較
            const response = await apiPost('/models/compare', {
                modelIds: modelIds,
            });

            const result = response.data;

            // 顯示結果
            displayComparisonResult(result);

            showAlert('比較完成！', 'success');

        } catch (error) {
            showAlert('比較失敗: ' + error.message, 'error');
        } finally {
            compareBtn.disabled = false;
            compareBtn.textContent = '開始比較';
        }
    });
}

/**
 * 顯示比較結果
 */
function displayComparisonResult(result) {
    // 顯示結果卡片
    resultCard.classList.remove('hidden');

    // 顯示最佳模型資訊
    displayBestModelInfo(result.bestModel);

    // 渲染效能比較圖表
    renderMetricsChart(result.models);

    // 渲染詳細比較表格
    renderComparisonTable(result.models);

    // 捲動到結果
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

/**
 * 顯示最佳模型資訊
 */
function displayBestModelInfo(bestModel) {
    const html = `
        <strong style="font-size: 1.1rem;">🏆 推薦模型: ${bestModel.modelName}</strong><br>
        <div style="margin-top: 0.5rem;">
            驗證損失 (Val Loss): ${bestModel.valLoss.toFixed(4)}<br>
            驗證 MAE (Val MAE): ${bestModel.valMAE.toFixed(4)}
        </div>
    `;
    bestModelInfo.innerHTML = html;
}

/**
 * 渲染效能指標圖表
 */
function renderMetricsChart(models) {
    // 銷毀舊圖表
    if (currentChart) {
        currentChart.destroy();
    }

    const ctx = document.getElementById('metrics-chart').getContext('2d');

    // 準備資料
    const modelNames = models.map(m => m.modelName);
    const valLosses = models.map(m => m.metrics.valLoss);
    const valMAEs = models.map(m => m.metrics.valMAE);

    // 建立圖表
    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: modelNames,
            datasets: [
                {
                    label: '驗證損失 (Val Loss)',
                    data: valLosses,
                    backgroundColor: 'rgba(231, 76, 60, 0.7)',
                    borderColor: '#e74c3c',
                    borderWidth: 1,
                    yAxisID: 'y',
                },
                {
                    label: '驗證 MAE (Val MAE)',
                    data: valMAEs,
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: '#3498db',
                    borderWidth: 1,
                    yAxisID: 'y',
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '模型效能指標比較 (數值越低越好)',
                    font: {
                        size: 14,
                    },
                },
                legend: {
                    display: true,
                    position: 'top',
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '誤差值',
                    },
                },
            },
        },
    });
}

/**
 * 渲染詳細比較表格
 */
function renderComparisonTable(models) {
    let html = '<table style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr style="background: #ecf0f1;">';
    html += '<th style="padding: 0.75rem; text-align: left;">模型名稱</th>';
    html += '<th style="padding: 0.75rem; text-align: center;">預測天數</th>';
    html += '<th style="padding: 0.75rem; text-align: center;">訓練損失</th>';
    html += '<th style="padding: 0.75rem; text-align: center;">驗證損失</th>';
    html += '<th style="padding: 0.75rem; text-align: center;">訓練 MAE</th>';
    html += '<th style="padding: 0.75rem; text-align: center;">驗證 MAE</th>';
    html += '<th style="padding: 0.75rem; text-align: left;">資料檔案</th>';
    html += '<th style="padding: 0.75rem; text-align: center;">訓練時間</th>';
    html += '</tr></thead><tbody>';

    models.forEach(model => {
        html += '<tr style="border-bottom: 1px solid #ecf0f1;">';
        html += `<td style="padding: 0.75rem;"><strong>${model.modelName}</strong></td>`;
        html += `<td style="padding: 0.75rem; text-align: center;">${model.predictionDays}</td>`;
        html += `<td style="padding: 0.75rem; text-align: center;">${model.metrics.trainLoss.toFixed(4)}</td>`;
        html += `<td style="padding: 0.75rem; text-align: center;">${model.metrics.valLoss.toFixed(4)}</td>`;
        html += `<td style="padding: 0.75rem; text-align: center;">${model.metrics.trainMAE.toFixed(4)}</td>`;
        html += `<td style="padding: 0.75rem; text-align: center;">${model.metrics.valMAE.toFixed(4)}</td>`;
        html += `<td style="padding: 0.75rem;">${model.dataFileName}</td>`;
        html += `<td style="padding: 0.75rem; text-align: center;">${new Date(model.trainedAt).toLocaleString('zh-TW')}</td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';

    comparisonTableContainer.innerHTML = html;
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
