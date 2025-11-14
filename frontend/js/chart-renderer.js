/**
 * 圖表渲染模組
 * 使用 Chart.js 繪製歷史股價與預測股價
 */

/**
 * 渲染預測圖表
 * @param {string} canvasId - Canvas 元素 ID
 * @param {Array} historicalData - 歷史資料
 * @param {Array} predictions - 預測資料
 * @returns {Chart} Chart.js 實例
 */
function renderPredictionChart(canvasId, historicalData, predictions) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // 準備歷史資料
    const historicalDates = historicalData.map(d => d.date);
    const historicalPrices = historicalData.map(d => d.close);

    // 準備預測資料
    const predictionDates = predictions.map(d => d.date);
    const predictionPrices = predictions.map(d => d.predictedClose);

    // 合併日期軸
    const allDates = [...historicalDates, ...predictionDates];

    // 建立資料集
    const datasets = [
        {
            label: '歷史股價',
            data: [...historicalPrices, ...Array(predictions.length).fill(null)],
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.1,
        },
        {
            label: '預測股價',
            data: [...Array(historicalData.length).fill(null), ...predictionPrices],
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            borderWidth: 2,
            borderDash: [5, 5],  // 虛線
            pointRadius: 3,
            tension: 0.1,
        },
    ];

    // 建立圖表
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                title: {
                    display: true,
                    text: '股價走勢預測',
                    font: {
                        size: 16,
                    },
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(2);
                            }
                            return label;
                        },
                    },
                },
                legend: {
                    display: true,
                    position: 'top',
                },
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: '日期',
                    },
                    ticks: {
                        maxTicksLimit: 10,
                    },
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: '股價',
                    },
                },
            },
        },
    });

    return chart;
}

/**
 * 渲染預測詳情表格
 * @param {Array} predictions - 預測資料
 * @returns {string} HTML 字串
 */
function renderPredictionTable(predictions) {
    let html = '<table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">';
    html += '<thead><tr style="background: #ecf0f1;">';
    html += '<th style="padding: 0.75rem; text-align: left;">日期</th>';
    html += '<th style="padding: 0.75rem; text-align: right;">預測收盤價</th>';
    html += '<th style="padding: 0.75rem; text-align: right;">漲跌機率</th>';
    html += '<th style="padding: 0.75rem; text-align: right;">變化幅度</th>';
    html += '<th style="padding: 0.75rem; text-align: center;">趨勢</th>';
    html += '</tr></thead><tbody>';

    predictions.forEach(pred => {
        const upProb = (pred.upProbability * 100).toFixed(1);
        const changePercent = pred.changePercent.toFixed(2);
        const trend = pred.changePercent > 0 ? '📈 上漲' : '📉 下跌';
        const trendColor = pred.changePercent > 0 ? '#27ae60' : '#e74c3c';

        html += '<tr style="border-bottom: 1px solid #ecf0f1;">';
        html += `<td style="padding: 0.75rem;">${pred.date}</td>`;
        html += `<td style="padding: 0.75rem; text-align: right;">${pred.predictedClose.toFixed(2)}</td>`;
        html += `<td style="padding: 0.75rem; text-align: right;">${upProb}%</td>`;
        html += `<td style="padding: 0.75rem; text-align: right; color: ${trendColor};">${changePercent}%</td>`;
        html += `<td style="padding: 0.75rem; text-align: center; color: ${trendColor};">${trend}</td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}

export { renderPredictionChart, renderPredictionTable };
