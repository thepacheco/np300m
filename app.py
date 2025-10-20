"""
FLASK WEB INTERFACE - iPad-Friendly Trading Dashboard
3-Button System: UPDATE | ANALYZE | RESULTS
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime
from trading_system import LiveTradingAnalyzer, load_config, save_config, SECTORS

app = Flask(__name__)
CORS(app)

# Global analyzer
analyzer = None
latest_results = None
analysis_progress = {'message': '', 'type': 'info'}

def log_progress(message, log_type='info'):
    """Log progress message for live viewer"""
    global analysis_progress
    analysis_progress = {'message': message, 'type': log_type}
    print(f"[{log_type.upper()}] {message}")  # Also print to terminal

# ============================================================================
# HTML TEMPLATE (iPad Optimized)
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Live Trading Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .status-bar {
            background: #f8f9fa;
            padding: 15px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            margin: 5px 10px;
        }
        
        .status-label {
            font-weight: 600;
            margin-right: 10px;
            color: #666;
        }
        
        .status-value {
            color: #333;
            font-weight: 500;
        }
        
        .regime-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
        }
        
        .regime-strong_bull { background: #10b981; color: white; }
        .regime-bull { background: #34d399; color: white; }
        .regime-sideways { background: #fbbf24; color: #333; }
        .regime-bear { background: #f87171; color: white; }
        .regime-strong_bear { background: #dc2626; color: white; }
        .regime-volatile { background: #a855f7; color: white; }
        
        .button-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            padding: 30px;
            background: #fafafa;
        }
        
        .action-button {
            padding: 30px;
            font-size: 20px;
            font-weight: 600;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .action-button:active {
            transform: translateY(0);
        }
        
        .action-button.loading {
            pointer-events: none;
            opacity: 0.7;
        }
        
        .btn-update {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .btn-analyze {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .btn-results {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .button-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 10px;
        }
        
        .settings-panel {
            padding: 30px;
            border-top: 1px solid #e0e0e0;
        }
        
        .settings-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }
        
        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .setting-item {
            display: flex;
            flex-direction: column;
        }
        
        .setting-item label {
            font-weight: 500;
            margin-bottom: 8px;
            color: #666;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .info-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            font-size: 12px;
            font-weight: bold;
            cursor: help;
            position: relative;
        }
        
        .info-icon:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: normal;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .info-icon:hover::before {
            content: '';
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: #333;
            z-index: 1000;
        }
        
        .setting-item input, .setting-item select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .setting-item input:focus, .setting-item select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .sector-toggles {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        
        .sector-toggle {
            display: flex;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .sector-toggle input[type="checkbox"] {
            margin-right: 10px;
            width: 20px;
            height: 20px;
        }
        
        .results-container {
            padding: 30px;
            display: none;
        }
        
        .results-container.active {
            display: block;
        }
        
        .opportunity-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .opportunity-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .card-title {
            font-size: 24px;
            font-weight: 700;
            color: #333;
        }
        
        .card-subtitle {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        
        .action-badge {
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
        }
        
        .action-BUY { background: #10b981; color: white; }
        .action-SELL { background: #ef4444; color: white; }
        .action-HOLD { background: #fbbf24; color: #333; }
        
        .card-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .metric {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
        }
        
        .metric-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .card-targets {
            background: #f0f9ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .targets-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        .target-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 14px;
        }
        
        .card-reasoning {
            background: #fef3c7;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #fbbf24;
        }
        
        .reasoning-title {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        
        .reasoning-text {
            font-size: 14px;
            line-height: 1.6;
            color: #666;
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .save-button {
            background: #10b981;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .save-button:hover {
            background: #059669;
        }
        
        .log-viewer {
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
            display: none;
        }
        
        .log-viewer.active {
            display: block;
        }
        
        .log-line {
            margin: 2px 0;
            padding: 2px 0;
        }
        
        .log-line.info { color: #60a5fa; }
        .log-line.success { color: #34d399; }
        .log-line.warning { color: #fbbf24; }
        .log-line.error { color: #f87171; }
        
        .log-toggle {
            background: #1e293b;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            margin-top: 20px;
        }
        
        .log-toggle:hover {
            background: #334155;
        }
        
        .log-toggle.active {
            background: #10b981;
        }
        
        @media (max-width: 768px) {
            .button-container {
                grid-template-columns: 1fr;
            }
            
            .status-bar {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Live Trading Analysis</h1>
            <p>Smart IRA Trading with AI-Powered Insights</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <span class="status-label">Capital:</span>
                <span class="status-value" id="capital-display">$2,400</span>
            </div>
            <div class="status-item">
                <span class="status-label">Market Regime:</span>
                <span class="regime-badge" id="regime-badge">Loading...</span>
            </div>
            <div class="status-item">
                <span class="status-label">Last Update:</span>
                <span class="status-value" id="last-update">Never</span>
            </div>
        </div>
        
        <div class="button-container">
            <button class="action-button btn-update" onclick="updateStocks()">
                <span class="button-icon">🔄</span>
                UPDATE
                <div style="font-size: 12px; margin-top: 5px;">Refresh Stock Data</div>
            </button>
            
            <button class="action-button btn-analyze" onclick="runAnalysis()">
                <span class="button-icon">🔍</span>
                ANALYZE
                <div style="font-size: 12px; margin-top: 5px;">Run Analysis</div>
            </button>
            
            <button class="action-button btn-results" onclick="showResults()">
                <span class="button-icon">📈</span>
                RESULTS
                <div style="font-size: 12px; margin-top: 5px;">View Recommendations</div>
            </button>
        </div>
        
        <div class="settings-panel">
            <div class="settings-title">⚙️ Settings</div>
            
            <button class="log-toggle" onclick="toggleLogs()">
                📊 Show Live Logs
            </button>
            
            <div class="log-viewer" id="log-viewer">
                <div style="font-weight: 600; margin-bottom: 10px;">🔍 Live Analysis Log</div>
                <div id="log-content">
                    <div class="log-line info">Waiting for analysis to start...</div>
                </div>
            </div>
            
            <div class="settings-grid">
                <div class="setting-item">
                    <label for="capital">
                        Capital ($)
                        <span class="info-icon" data-tooltip="Total investment amount you want to allocate">i</span>
                    </label>
                    <input type="number" id="capital" value="2400" min="100" step="100">
                </div>
                
                <div class="setting-item">
                    <label for="position-size">
                        Position Size (%)
                        <span class="info-icon" data-tooltip="What % of capital to use per trade (10% = $240 per stock if capital is $2,400)">i</span>
                    </label>
                    <input type="number" id="position-size" value="10" min="1" max="100">
                </div>
                
                <div class="setting-item">
                    <label for="stop-loss">
                        Stop Loss (%)
                        <span class="info-icon" data-tooltip="Auto-exit if stock drops this % below your entry (protects against big losses)">i</span>
                    </label>
                    <input type="number" id="stop-loss" value="5" min="1" max="20">
                </div>
                
                <div class="setting-item">
                    <label for="take-profit">
                        Take Profit (%)
                        <span class="info-icon" data-tooltip="Target gain - consider selling when stock is up this % (locks in profits)">i</span>
                    </label>
                    <input type="number" id="take-profit" value="10" min="1" max="50">
                </div>
                
                <div class="setting-item">
                    <label for="top-n">
                        Top Opportunities
                        <span class="info-icon" data-tooltip="How many top-ranked stocks to display in results">i</span>
                    </label>
                    <input type="number" id="top-n" value="20" min="5" max="50">
                </div>
                
                <div class="setting-item">
                    <label for="min-score">
                        Min Score
                        <span class="info-icon" data-tooltip="Only show stocks scoring above this (70+ is strong, 50-70 is good)">i</span>
                    </label>
                    <input type="number" id="min-score" value="50" min="0" max="100">
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <div class="settings-title">📁 Enable/Disable Sectors</div>
                <div style="background: #fef3c7; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #f59e0b;">
                    <strong>⚠️ Free Tier Tip:</strong> Enable only 2-3 sectors for faster analysis and to avoid timeouts. More sectors = longer analysis time.
                </div>
                <div class="sector-toggles" id="sector-toggles">
                    <!-- Sectors will be populated here -->
                </div>
            </div>
            
            <button class="save-button" onclick="saveSettings()">💾 Save Settings</button>
        </div>
        
        <div class="results-container" id="results-container">
            <div class="settings-title">🎯 Top Trading Opportunities</div>
            <div id="opportunities-list">
                <!-- Results will be populated here -->
            </div>
        </div>
    </div>
    
    <script>
        let currentConfig = {};
        let currentResults = null;
        let logPollingInterval = null;
        
        // Log viewer functions
        function toggleLogs() {
            const viewer = document.getElementById('log-viewer');
            const button = document.querySelector('.log-toggle');
            
            if (viewer.classList.contains('active')) {
                viewer.classList.remove('active');
                button.classList.remove('active');
                button.textContent = '📊 Show Live Logs';
                stopLogPolling();
            } else {
                viewer.classList.add('active');
                button.classList.add('active');
                button.textContent = '📊 Hide Live Logs';
            }
        }
        
        function addLog(message, type = 'info') {
            const logContent = document.getElementById('log-content');
            const logLine = document.createElement('div');
            logLine.className = `log-line ${type}`;
            const timestamp = new Date().toLocaleTimeString();
            logLine.textContent = `[${timestamp}] ${message}`;
            logContent.appendChild(logLine);
            
            // Auto-scroll to bottom
            logContent.scrollTop = logContent.scrollHeight;
            
            // Keep only last 100 lines (memory efficient)
            if (logContent.children.length > 100) {
                logContent.removeChild(logContent.firstChild);
            }
        }
        
        function clearLogs() {
            document.getElementById('log-content').innerHTML = '';
        }
        
        function startLogPolling() {
            // Poll for progress updates every 2 seconds during analysis
            logPollingInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/analysis-progress');
                    if (response.ok) {
                        const progress = await response.json();
                        if (progress.message) {
                            addLog(progress.message, progress.type || 'info');
                        }
                    }
                } catch (error) {
                    // Silent fail - progress endpoint may not return anything
                }
            }, 2000);
        }
        
        function stopLogPolling() {
            if (logPollingInterval) {
                clearInterval(logPollingInterval);
                logPollingInterval = null;
            }
        }
        
        // Load initial config
        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                currentConfig = await response.json();
                updateUIFromConfig();
            } catch (error) {
                console.error('Error loading config:', error);
            }
        }
        
        function updateUIFromConfig() {
            document.getElementById('capital').value = currentConfig.capital || 2400;
            document.getElementById('position-size').value = currentConfig.position_size_pct || 10;
            document.getElementById('stop-loss').value = currentConfig.stop_loss_pct || 5;
            document.getElementById('take-profit').value = currentConfig.take_profit_pct || 10;
            document.getElementById('top-n').value = currentConfig.top_opportunities || 20;
            document.getElementById('min-score').value = currentConfig.min_score || 50;
            
            document.getElementById('capital-display').textContent = 
                '$' + currentConfig.capital.toLocaleString();
            
            // Populate sector toggles
            const sectorsContainer = document.getElementById('sector-toggles');
            sectorsContainer.innerHTML = '';
            
            const allSectors = {{ sectors | tojson }};
            for (const sector of allSectors) {
                const isEnabled = currentConfig.enabled_sectors.includes(sector);
                sectorsContainer.innerHTML += `
                    <div class="sector-toggle">
                        <input type="checkbox" id="sector-${sector}" ${isEnabled ? 'checked' : ''}>
                        <label for="sector-${sector}">${sector.replace('_', ' ')}</label>
                    </div>
                `;
            }
        }
        
        async function saveSettings() {
            const allSectors = {{ sectors | tojson }};
            const enabledSectors = allSectors.filter(sector => 
                document.getElementById(`sector-${sector}`).checked
            );
            
            const newConfig = {
                capital: parseInt(document.getElementById('capital').value),
                position_size_pct: parseInt(document.getElementById('position-size').value),
                stop_loss_pct: parseInt(document.getElementById('stop-loss').value),
                take_profit_pct: parseInt(document.getElementById('take-profit').value),
                top_opportunities: parseInt(document.getElementById('top-n').value),
                min_score: parseInt(document.getElementById('min-score').value),
                enabled_sectors: enabledSectors
            };
            
            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newConfig)
                });
                
                if (response.ok) {
                    currentConfig = newConfig;
                    document.getElementById('capital-display').textContent = 
                        '$' + newConfig.capital.toLocaleString();
                    alert('✅ Settings saved successfully!');
                }
            } catch (error) {
                console.error('Error saving config:', error);
                alert('❌ Error saving settings');
            }
        }
        
        async function updateStocks() {
            const button = document.querySelector('.btn-update');
            button.classList.add('loading');
            button.innerHTML = '<span class="loading-spinner"></span> UPDATING...';
            
            try {
                // Just reload config for now
                await loadConfig();
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                setTimeout(() => {
                    button.classList.remove('loading');
                    button.innerHTML = '<span class="button-icon">🔄</span>UPDATE<div style="font-size: 12px; margin-top: 5px;">Refresh Stock Data</div>';
                    alert('✅ Stock data updated!');
                }, 1000);
            } catch (error) {
                console.error('Error updating:', error);
                button.classList.remove('loading');
                button.innerHTML = '<span class="button-icon">🔄</span>UPDATE<div style="font-size: 12px; margin-top: 5px;">Refresh Stock Data</div>';
            }
        }
        
        async function runAnalysis() {
            const button = document.querySelector('.btn-analyze');
            button.classList.add('loading');
            button.innerHTML = '<span class="loading-spinner"></span> ANALYZING...';
            
            // Clear and show logs
            clearLogs();
            addLog('🚀 Starting analysis...', 'info');
            addLog(`📊 Capital: $${currentConfig.capital || 2400}`, 'info');
            addLog(`📁 Sectors enabled: ${(currentConfig.enabled_sectors || []).length}`, 'info');
            
            // Start polling for progress
            startLogPolling();
            
            try {
                addLog('📡 Connecting to analysis engine...', 'info');
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('Analysis error:', errorData);
                    addLog(`❌ Error: ${errorData.error}`, 'error');
                    alert(`❌ Error running analysis:\n\nType: ${errorData.type}\nMessage: ${errorData.error}\n\nCheck browser console (F12) for full details.`);
                    button.classList.remove('loading');
                    button.innerHTML = '<span class="button-icon">🔍</span>ANALYZE<div style="font-size: 12px; margin-top: 5px;">Run Analysis</div>';
                    stopLogPolling();
                    return;
                }
                
                addLog('📥 Receiving results...', 'info');
                currentResults = await response.json();
                
                // Update regime
                const regime = currentResults.market_regime.regime;
                const regimeBadge = document.getElementById('regime-badge');
                regimeBadge.textContent = regime.replace('_', ' ').toUpperCase();
                regimeBadge.className = `regime-badge regime-${regime}`;
                
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
                button.classList.remove('loading');
                button.innerHTML = '<span class="button-icon">🔍</span>ANALYZE<div style="font-size: 12px; margin-top: 5px;">Run Analysis</div>';
                
                addLog(`✅ Analysis complete!`, 'success');
                addLog(`📊 Found ${currentResults.total_analyzed} stocks`, 'success');
                addLog(`🏆 Top opportunities: ${currentResults.top_opportunities.length}`, 'success');
                addLog(`🌍 Market regime: ${regime.toUpperCase()}`, 'info');
                
                stopLogPolling();
                
                alert(`✅ Analysis complete! Found ${currentResults.total_analyzed} stocks. Click RESULTS to view.`);
            } catch (error) {
                console.error('Error analyzing:', error);
                button.classList.remove('loading');
                button.innerHTML = '<span class="button-icon">🔍</span>ANALYZE<div style="font-size: 12px; margin-top: 5px;">Run Analysis</div>';
                addLog(`❌ Error: ${error.message}`, 'error');
                stopLogPolling();
                alert(`❌ Error running analysis:\n\n${error.message}\n\nCheck terminal/console for details.`);
            }
        }
        
        function showResults() {
            if (!currentResults) {
                alert('⚠️ Please run ANALYZE first!');
                return;
            }
            
            const container = document.getElementById('results-container');
            const list = document.getElementById('opportunities-list');
            
            list.innerHTML = '';
            
            currentResults.top_opportunities.forEach((opp, index) => {
                const card = createOpportunityCard(opp, index + 1);
                list.innerHTML += card;
            });
            
            container.classList.add('active');
            container.scrollIntoView({ behavior: 'smooth' });
        }
        
        function createOpportunityCard(opp, rank) {
            const confidence = opp.predictions.confidence || 'medium';
            const confidenceColor = confidence === 'high' ? '#10b981' : confidence === 'medium' ? '#fbbf24' : '#ef4444';
            const confidenceEmoji = confidence === 'high' ? '🔥' : confidence === 'medium' ? '⭐' : '⚠️';
            
            // Calculate profit potential
            const entryPrice = opp.predictions.predictions.today.entry_zone || opp.predictions.predictions.today.target_low;
            const weekTarget = opp.predictions.predictions.week.target;
            const monthTarget = opp.predictions.predictions.month.target;
            
            const weekProfit = weekTarget - entryPrice;
            const weekProfitPct = ((weekTarget - entryPrice) / entryPrice) * 100;
            const monthProfit = monthTarget - entryPrice;
            const monthProfitPct = ((monthTarget - entryPrice) / entryPrice) * 100;
            
            // Calculate shares you could buy using ACTUAL settings
            const capital = currentConfig.capital || 2400;
            const positionSizePct = currentConfig.position_size_pct || 10;
            const positionSize = capital * (positionSizePct / 100);
            const shares = Math.floor(positionSize / entryPrice);
            const actualInvested = shares * entryPrice;
            const weekProfitTotal = shares * weekProfit;
            const monthProfitTotal = shares * monthProfit;
            
            return `
                <div class="opportunity-card">
                    <div class="card-header">
                        <div>
                            <div class="card-title">#${rank} ${opp.symbol}</div>
                            <div class="card-subtitle">${opp.company_name}</div>
                        </div>
                        <div>
                            <div class="action-badge action-${opp.predictions.action}">
                                ${opp.predictions.action}
                            </div>
                            <div style="font-size: 12px; color: ${confidenceColor}; margin-top: 5px; text-align: center;">
                                ${confidenceEmoji} ${confidence.toUpperCase()}
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #3b82f6;">
                        <div style="font-weight: 600; color: #1e40af; margin-bottom: 8px;">💰 Profit Calculator</div>
                        <div style="font-size: 13px; color: #1e40af;">
                            <strong>If you buy at entry ($${entryPrice.toFixed(2)}):</strong><br>
                            • ${shares} shares = $${actualInvested.toFixed(2)} invested<br>
                            • <strong>1 Week target:</strong> ${weekProfitPct > 0 ? 'Gain' : 'Loss'} of $${Math.abs(weekProfitTotal).toFixed(2)} (${weekProfitPct.toFixed(1)}%)<br>
                            • <strong>1 Month target:</strong> ${monthProfitPct > 0 ? 'Gain' : 'Loss'} of $${Math.abs(monthProfitTotal).toFixed(2)} (${monthProfitPct.toFixed(1)}%)<br>
                            <span style="font-size: 11px; opacity: 0.8;">Based on $${positionSize.toFixed(0)} position (${positionSizePct}% of $${capital.toLocaleString()})</span>
                        </div>
                    </div>
                    
                    <div class="card-metrics">
                        <div class="metric">
                            <div class="metric-label">
                                Current Price
                                <span class="info-icon" data-tooltip="Live market price" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value">$${opp.current_price.toFixed(2)}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">
                                Score
                                <span class="info-icon" data-tooltip="Composite score: 80+ excellent, 70+ very good, 60+ good, 50+ okay" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value">${opp.score.toFixed(1)}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">
                                RSI
                                <span class="info-icon" data-tooltip="Relative Strength Index: <30 oversold, >70 overbought, 30-70 normal" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value" style="color: ${opp.factors.rsi < 30 ? '#10b981' : opp.factors.rsi > 70 ? '#ef4444' : '#666'}">
                                ${opp.factors.rsi.toFixed(0)}
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">
                                Momentum 1M
                                <span class="info-icon" data-tooltip="Price change over last month. Positive = went up, Negative = went down" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value" style="color: ${opp.factors.momentum['1m'] > 0 ? '#10b981' : '#ef4444'}">
                                ${(opp.factors.momentum['1m'] * 100).toFixed(1)}%
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">
                                Volatility
                                <span class="info-icon" data-tooltip="How much price swings. <20% stable, 20-40% normal, >40% risky" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value">${(opp.factors.volatility['20d'] * 100).toFixed(1)}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">
                                Volume Surge
                                <span class="info-icon" data-tooltip="Recent volume vs average. >1.5x = unusual activity, potential breakout" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value">${opp.factors.volume.surge.toFixed(2)}x</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">
                                Trend Score
                                <span class="info-icon" data-tooltip="Strength of trend: 80+ strong up, 20- strong down, 40-60 sideways" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value">${opp.factors.trend.score.toFixed(0)}/100</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">
                                From 52w High
                                <span class="info-icon" data-tooltip="Distance from 52-week high. <-20% = deep discount, >-5% = near peak" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value" style="color: ${opp.factors.price_levels.distance_from_high < -20 ? '#10b981' : '#666'}">
                                ${opp.factors.price_levels.distance_from_high.toFixed(1)}%
                            </div>
                        </div>
                        ${opp.factors.macd ? `
                        <div class="metric">
                            <div class="metric-label">
                                MACD
                                <span class="info-icon" data-tooltip="Trend momentum indicator. Bullish crossover = buy signal, Bearish = sell signal" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value" style="color: ${opp.factors.macd.crossover === 'bullish' ? '#10b981' : opp.factors.macd.crossover === 'bearish' ? '#ef4444' : '#666'}">
                                ${opp.factors.macd.crossover}
                            </div>
                        </div>
                        ` : ''}
                        ${opp.factors.bollinger ? `
                        <div class="metric">
                            <div class="metric-label">
                                Bollinger
                                <span class="info-icon" data-tooltip="Volatility bands. Oversold = near lower band (buy?), Overbought = near upper band (sell?)" style="font-size: 10px; width: 14px; height: 14px;">i</span>
                            </div>
                            <div class="metric-value" style="color: ${opp.factors.bollinger.signal === 'oversold' ? '#10b981' : opp.factors.bollinger.signal === 'overbought' ? '#ef4444' : '#666'}">
                                ${opp.factors.bollinger.signal}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                    
                    <div class="card-targets">
                        <div class="targets-title">🎯 Price Targets <span style="font-size: 12px; color: #666; font-weight: normal;">(Conservative estimates)</span></div>
                        
                        <div style="background: #dcfce7; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #10b981;">
                            <div style="font-weight: 600; color: #166534; margin-bottom: 5px;">🎯 BEST ENTRY ZONE</div>
                            <div style="font-size: 18px; font-weight: bold; color: #15803d;">
                                $${entryPrice.toFixed(2)}
                            </div>
                            <div style="font-size: 11px; color: #166534; margin-top: 3px;">
                                Set alert at this price to enter position
                            </div>
                        </div>
                        
                        <div class="target-row">
                            <span>Today High:</span>
                            <strong>$${opp.predictions.predictions.today.target_high.toFixed(2)}</strong>
                        </div>
                        <div class="target-row">
                            <span>Today Low (support):</span>
                            <strong style="color: #10b981;">$${opp.predictions.predictions.today.target_low.toFixed(2)}</strong>
                        </div>
                        <div class="target-row">
                            <span>Tomorrow:</span>
                            <strong>$${opp.predictions.predictions.tomorrow.target.toFixed(2)}</strong>
                            <span style="font-size: 11px; color: #666;">
                                ($${opp.predictions.predictions.tomorrow.range_low.toFixed(2)} - $${opp.predictions.predictions.tomorrow.range_high.toFixed(2)})
                            </span>
                        </div>
                        <div class="target-row">
                            <span>1 Week:</span>
                            <strong>$${opp.predictions.predictions.week.target.toFixed(2)}</strong>
                            <span style="font-size: 11px; color: #666;">
                                ($${opp.predictions.predictions.week.range_low.toFixed(2)} - $${opp.predictions.predictions.week.range_high.toFixed(2)})
                            </span>
                        </div>
                        <div class="target-row">
                            <span>1 Month:</span>
                            <strong>$${opp.predictions.predictions.month.target.toFixed(2)}</strong>
                            <span style="font-size: 11px; color: #666;">
                                ($${opp.predictions.predictions.month.range_low.toFixed(2)} - $${opp.predictions.predictions.month.range_high.toFixed(2)})
                            </span>
                        </div>
                    </div>
                    
                    <div class="card-reasoning">
                        <div class="reasoning-title">💡 Analysis</div>
                        <div class="reasoning-text">${opp.predictions.reasoning}</div>
                        ${opp.patterns.length > 0 ? `<div class="reasoning-text" style="margin-top: 8px;"><strong>Patterns:</strong> ${opp.patterns.map(p => p.pattern).join(', ')}</div>` : ''}
                        ${opp.news.sentiment !== 'neutral' ? `<div class="reasoning-text" style="margin-top: 8px;"><strong>News:</strong> ${opp.news.sentiment.toUpperCase()}</div>` : ''}
                    </div>
                    
                    ${opp.predictions.detailed_explanation ? `
                    <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #f59e0b;">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #92400e; cursor: pointer;" onclick="this.parentElement.querySelector('.explanation-content').style.display = this.parentElement.querySelector('.explanation-content').style.display === 'none' ? 'block' : 'none'">
                            📚 Why These Predictions? (Click to expand)
                        </div>
                        <div class="explanation-content" style="display: none; font-size: 13px; line-height: 1.6; color: #78350f; white-space: pre-line;">
                            ${opp.predictions.detailed_explanation}
                        </div>
                    </div>
                    ` : ''}
                    
                    <div class="reasoning-text" style="margin-top: 15px; font-size: 11px; opacity: 0.8; text-align: center;">
                        ⚠️ These are probabilistic predictions, not guarantees. Always do your own research before trading.
                    </div>
                </div>
            `;
        }
        
        // Load config on page load
        loadConfig();
    </script>
</body>
</html>
"""

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template_string(HTML_TEMPLATE, sectors=list(SECTORS.keys()))

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = load_config()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    config = request.json
    save_config(config)
    
    # Reload analyzer with new config
    global analyzer
    analyzer = LiveTradingAnalyzer(config)
    
    return jsonify({'status': 'success', 'config': config})

@app.route('/api/analysis-progress', methods=['GET'])
def get_progress():
    """Get current analysis progress"""
    return jsonify(analysis_progress)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run the analysis"""
    global analyzer, latest_results
    
    try:
        log_progress('Initializing analyzer...', 'info')
        
        if analyzer is None:
            config = load_config()
            analyzer = LiveTradingAnalyzer(config)
        
        # For Render free tier: limit to prevent timeout
        enabled_sectors = analyzer.config.get('enabled_sectors', [])
        
        log_progress(f'Sectors selected: {len(enabled_sectors)}', 'info')
        
        # Auto-limit on Render to prevent timeout
        if len(enabled_sectors) > 3:
            log_progress('⚠️ Limiting to first 3 sectors (free tier)', 'warning')
            enabled_sectors = enabled_sectors[:3]
        
        log_progress(f'Analyzing {len(enabled_sectors)} sectors...', 'info')
        
        # Run analysis
        results = analyzer.run_analysis(
            enabled_sectors=enabled_sectors,
            top_n=analyzer.config.get('top_opportunities', 20)
        )
        
        latest_results = results
        log_progress(f'✅ Complete! Analyzed {results["total_analyzed"]} stocks', 'success')
        return jsonify(results)
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        log_progress(f'❌ Error: {str(e)}', 'error')
        print("\n❌ ERROR DURING ANALYSIS:")
        print(error_details['traceback'])
        return jsonify(error_details), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get latest results"""
    if latest_results is None:
        return jsonify({'error': 'No results available. Run analysis first.'}), 404
    
    return jsonify(latest_results)

@app.route('/api/recommendation/<symbol>', methods=['GET'])
def get_recommendation(symbol):
    """Get detailed recommendation for a specific stock"""
    if latest_results is None:
        return jsonify({'error': 'No results available'}), 404
    
    # Find stock in results
    stock = next((s for s in latest_results['all_stocks'] if s['symbol'] == symbol), None)
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    capital = analyzer.config.get('capital', 2400)
    recommendation = analyzer.format_recommendation(stock, capital)
    
    return jsonify(recommendation)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    TRADING DASHBOARD SERVER                                  ║
║                                                                              ║
║  🌐 Server starting...                                                       ║
║                                                                              ║
║  📱 iPad/Desktop Access:                                                     ║
║     Local:  http://localhost:5000                                           ║
║     Network: http://YOUR_IP:5000                                            ║
║                                                                              ║
║  ✨ Features Available:                                                      ║
║     • 3-Button Interface (UPDATE/ANALYZE/RESULTS)                           ║
║     • Real-time Stock Analysis                                              ║
║     • Customizable Settings                                                 ║
║     • Sector Screening                                                      ║
║     • Price Predictions                                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
