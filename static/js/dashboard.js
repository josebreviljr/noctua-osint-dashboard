// Noctua Dashboard JavaScript

let urgencyChart, topicsChart;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
    loadFilterOptions();
    setupAutoRefresh();
    setupResizeHandler();
});

function initializeCharts() {
    // Urgency Distribution Chart
    const urgencyCtx = document.getElementById('urgencyChart').getContext('2d');
    urgencyChart = new Chart(urgencyCtx, {
        type: 'doughnut',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    });

    // Topics Chart
    const topicsCtx = document.getElementById('topicsChart').getContext('2d');
    topicsChart = new Chart(topicsCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Articles',
                data: [],
                backgroundColor: '#3b82f6',
                borderColor: '#2563eb',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    });
}

function setupEventListeners() {
    // Collect Data Button
    document.getElementById('collectBtn').addEventListener('click', function() {
        // Collect 5 articles per feed by default
        collectData(5);
    });

    // Export CSV Button
    document.getElementById('exportBtn').addEventListener('click', function() {
        exportCSV();
    });

    // Filters
    document.getElementById('urgencyFilter').addEventListener('change', filterReports);
    document.getElementById('topicFilter').addEventListener('change', filterReports);
    document.getElementById('regionFilter').addEventListener('change', filterReports);
}

function loadFilterOptions() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
            populateFilterOptions(data);
        })
        .catch(error => console.error('Error loading data:', error));
}

function updateCharts(data) {
    // Update urgency chart
    if (data.summary.urgency_distribution) {
        const urgencyData = [
            data.summary.urgency_distribution.high || 0,
            data.summary.urgency_distribution.medium || 0,
            data.summary.urgency_distribution.low || 0
        ];
        urgencyChart.data.datasets[0].data = urgencyData;
        urgencyChart.update();
    }

    // Update topics chart
    if (data.summary.top_topics) {
        const topics = Object.keys(data.summary.top_topics);
        const counts = Object.values(data.summary.top_topics);
        topicsChart.data.labels = topics;
        topicsChart.data.datasets[0].data = counts;
        topicsChart.update();
    }
}

function populateFilterOptions(data) {
    const topicFilter = document.getElementById('topicFilter');
    const regionFilter = document.getElementById('regionFilter');
    
    // Get unique topics and regions from reports
    const topics = new Set();
    const regions = new Set();
    
    data.reports.forEach(report => {
        if (report.topic) topics.add(report.topic);
        if (report.region) regions.add(report.region);
    });
    
    // Populate topic filter
    topics.forEach(topic => {
        const option = document.createElement('option');
        option.value = topic;
        option.textContent = topic;
        topicFilter.appendChild(option);
    });
    
    // Populate region filter
    regions.forEach(region => {
        const option = document.createElement('option');
        option.value = region;
        option.textContent = region;
        regionFilter.appendChild(option);
    });
}

function collectData(maxArticles) {
    const collectBtn = document.getElementById('collectBtn');
    const originalText = collectBtn.innerHTML;
    
    // Show loading state on the main button
    collectBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Collecting...';
    collectBtn.disabled = true;
    
    fetch('/api/collect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ max_articles: parseInt(maxArticles) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Success! ' + data.message, 'success');
            // Reload dashboard data after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error collecting data', 'error');
    })
    .finally(() => {
        // Reset button
        collectBtn.innerHTML = originalText;
        collectBtn.disabled = false;
    });
}

function exportCSV() {
    const exportBtn = document.getElementById('exportBtn');
    const originalText = exportBtn.innerHTML;
    
    // Show loading state
    exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Exporting...';
    exportBtn.disabled = true;
    
    fetch('/export/csv')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Success! ' + data.message, 'success');
            } else {
                showNotification('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error exporting data', 'error');
        })
        .finally(() => {
            // Reset button state
            exportBtn.innerHTML = originalText;
            exportBtn.disabled = false;
        });
}

function filterReports() {
    const urgency = document.getElementById('urgencyFilter').value;
    const topic = document.getElementById('topicFilter').value;
    const region = document.getElementById('regionFilter').value;
    
    const params = new URLSearchParams();
    if (urgency) params.append('urgency', urgency);
    if (topic) params.append('topic', topic);
    if (region) params.append('region', region);
    params.append('limit', 50);
    
    fetch(`/api/reports?${params}`)
        .then(response => response.json())
        .then(data => {
            updateReportsDisplay(data.reports);
        })
        .catch(error => console.error('Error filtering reports:', error));
}

function updateReportsDisplay(reports) {
    const container = document.getElementById('reportsContainer');
    container.innerHTML = '';
    
    if (reports.length === 0) {
        container.innerHTML = '<div class="p-6 text-center text-gray-500">No reports found matching the selected filters.</div>';
        return;
    }
    
    reports.forEach(report => {
        const urgencyClass = report.urgency === 'high' ? 'bg-red-100 text-red-800' :
                           report.urgency === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                           'bg-green-100 text-green-800';
        
        const reportHtml = `
            <div class="p-6 hover:bg-gray-50 transition-colors">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="px-2 py-1 text-xs font-medium rounded-full ${urgencyClass}">
                                ${report.urgency.charAt(0).toUpperCase() + report.urgency.slice(1)}
                            </span>
                            <span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                                ${report.topic}
                            </span>
                            <span class="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">
                                ${report.region}
                            </span>
                        </div>
                        <h4 class="text-lg font-medium text-gray-900 mb-2">
                            ${report.original_article.title}
                        </h4>
                        <p class="text-gray-600 mb-3">${report.summary}</p>
                        <div class="flex items-center text-sm text-gray-500 space-x-4">
                            <span><i class="fas fa-calendar mr-1"></i>${report.analyzed_at.substring(0, 10)}</span>
                            <a href="${report.original_article.link}" target="_blank" class="source-link">
                                <i class="fas fa-link mr-1"></i>${report.original_article.source.substring(0, 30)}...
                                <i class="fas fa-external-link-alt external-icon"></i>
                            </a>
                            <span><i class="fas fa-chart-line mr-1"></i>Confidence: ${report.confidence.charAt(0).toUpperCase() + report.confidence.slice(1)}</span>
                        </div>
                    </div>
                    <div class="ml-4">
                        <a href="/report/${report.id}" class="text-blue-600 hover:text-blue-800">
                            <i class="fas fa-external-link-alt"></i>
                        </a>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += reportHtml;
    });
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function setupAutoRefresh() {
    // Refresh dashboard data every 5 minutes
    setInterval(() => {
        loadFilterOptions();
    }, 5 * 60 * 1000);
}

function setupResizeHandler() {
    // Handle window resize to maintain chart sizing
    window.addEventListener('resize', function() {
        if (urgencyChart) {
            urgencyChart.resize();
        }
        if (topicsChart) {
            topicsChart.resize();
        }
    });
} 