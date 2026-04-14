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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Stock Advisor</title>
    <style>
        /* ── Apple Design System ── */
        :root {
            --bg:           #F2F2F7;
            --bg-card:      #FFFFFF;
            --bg-grouped:   #EFEFF4;
            --label:        #000000;
            --label-2:      rgba(60,60,67,0.6);
            --label-3:      rgba(60,60,67,0.3);
            --sep:          rgba(60,60,67,0.29);
            --blue:         #007AFF;
            --blue-light:   rgba(0,122,255,0.12);
            --green:        #34C759;
            --green-light:  rgba(52,199,89,0.12);
            --red:          #FF3B30;
            --red-light:    rgba(255,59,48,0.12);
            --orange:       #FF9500;
            --orange-light: rgba(255,149,0,0.12);
            --yellow:       #FFCC00;
            --purple:       #AF52DE;
            --gray:         #8E8E93;
            --gray4:        #D1D1D6;
            --gray5:        #E5E5EA;
            --gray6:        #F2F2F7;
            --r-sm:  10px;
            --r-md:  14px;
            --r-lg:  18px;
            --r-xl:  24px;
            --shadow: 0 1px 4px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.06);
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.06);
        }

        * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }

        html { height:100%; }

        body {
            font-family: -apple-system, 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg);
            color: var(--label);
            min-height: 100%;
            -webkit-font-smoothing: antialiased;
        }

        /* ── Layout shell ── */
        .app-shell {
            display: flex;
            flex-direction: column;
            min-height: 100dvh;
            max-width: 1200px;
            margin: 0 auto;
        }

        /* ── Nav bar ── */
        .nav-bar {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(242,242,247,0.85);
            -webkit-backdrop-filter: blur(20px);
            backdrop-filter: blur(20px);
            padding: env(safe-area-inset-top, 0) 20px 0;
            border-bottom: 1px solid var(--sep);
        }
        .nav-inner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 52px;
        }
        .nav-title {
            font-size: 17px;
            font-weight: 600;
            letter-spacing: -0.4px;
        }
        .nav-chips {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        .chip {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }
        .chip-regime-strong_bull  { background: var(--green-light);  color: #1A7F35; }
        .chip-regime-bull         { background: var(--green-light);  color: #1A7F35; }
        .chip-regime-sideways     { background: var(--orange-light); color: #BF6900; }
        .chip-regime-bear         { background: var(--red-light);    color: #C0392B; }
        .chip-regime-strong_bear  { background: var(--red-light);    color: #C0392B; }
        .chip-regime-volatile     { background: rgba(175,82,222,.12);color: #8037AB; }
        .chip-regime-unknown      { background: var(--gray5);        color: var(--gray); }
        .chip-vix-greed           { background: var(--red-light);    color: #C0392B; }
        .chip-vix-neutral         { background: var(--gray5);        color: var(--gray); }
        .chip-vix-fear            { background: var(--orange-light); color: #BF6900; }
        .chip-vix-extreme_fear    { background: var(--red-light);    color: #C0392B; }
        .chip-vix-unknown         { background: var(--gray5);        color: var(--gray); }
        .chip-win  { background: var(--green-light); color: #1A7F35; }
        .icon-btn {
            width: 34px; height: 34px;
            border-radius: 17px;
            background: var(--blue-light);
            border: none; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            font-size: 16px; color: var(--blue);
            flex-shrink: 0;
        }

        /* ── Main content area ── */
        .main-content {
            flex: 1;
            padding: 20px 16px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        /* ── Hero card ── */
        .hero-card {
            background: var(--blue);
            border-radius: var(--r-xl);
            padding: 32px 24px;
            text-align: center;
            color: white;
        }
        .hero-eyebrow {
            font-size: 13px;
            font-weight: 500;
            opacity: 0.8;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .hero-title {
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }
        .hero-sub {
            font-size: 14px;
            opacity: 0.75;
            margin-bottom: 24px;
            line-height: 1.4;
        }
        .pick-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: white;
            color: var(--blue);
            font-size: 17px;
            font-weight: 700;
            padding: 16px 40px;
            border-radius: var(--r-xl);
            border: none;
            cursor: pointer;
            width: 100%;
            max-width: 320px;
            transition: opacity 0.15s, transform 0.1s;
            letter-spacing: -0.3px;
        }
        .pick-btn:active { opacity: 0.82; transform: scale(0.98); }
        .pick-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .pick-btn .spinner {
            width: 18px; height: 18px;
            border: 2.5px solid rgba(0,122,255,0.25);
            border-top-color: var(--blue);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            display: none;
        }
        .pick-btn.loading .btn-icon { display: none; }
        .pick-btn.loading .spinner  { display: block; }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── Section label ── */
        .section-label {
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.4px;
            margin-bottom: 12px;
            color: var(--label);
        }

        /* ── Decision card ── */
        .decision-card {
            background: var(--bg-card);
            border-radius: var(--r-xl);
            box-shadow: var(--shadow);
            overflow: hidden;
            display: none;
        }
        .decision-card.visible { display: block; }

        .decision-header {
            padding: 20px 20px 0;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .decision-ticker {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
        }
        .decision-company {
            font-size: 14px;
            color: var(--label-2);
            margin-top: 2px;
        }
        .action-pill {
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .pill-BUY  { background: var(--green-light); color: #1A7F35; }
        .pill-SELL { background: var(--red-light);   color: #C0392B; }
        .pill-HOLD { background: var(--orange-light);color: #BF6900; }

        /* Score bar */
        .score-section {
            padding: 16px 20px;
        }
        .score-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .score-label { font-size: 13px; color: var(--label-2); font-weight: 500; }
        .score-value { font-size: 15px; font-weight: 700; }
        .score-bar-track {
            height: 6px;
            background: var(--gray5);
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 6px;
        }
        .score-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.6s ease;
        }
        .score-sub-row {
            display: flex;
            gap: 12px;
            font-size: 12px;
            color: var(--label-2);
        }
        .score-sub-item { display: flex; flex-direction: column; gap: 2px; }
        .score-sub-num { font-weight: 600; color: var(--label); font-size: 13px; }

        /* Key numbers */
        .key-numbers {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1px;
            background: var(--sep);
            border-top: 1px solid var(--sep);
        }
        .kn-cell {
            background: var(--bg-card);
            padding: 14px 16px;
            text-align: center;
        }
        .kn-label { font-size: 11px; color: var(--label-2); font-weight: 500; margin-bottom: 4px; }
        .kn-value { font-size: 17px; font-weight: 700; }

        /* Risk panel */
        .risk-panel {
            margin: 0 16px 16px;
            background: var(--red-light);
            border-radius: var(--r-md);
            padding: 14px 16px;
        }
        .risk-panel.green { background: var(--green-light); }
        .risk-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .risk-title { font-size: 13px; font-weight: 700; color: var(--label); }
        .risk-explainer { font-size: 12px; color: var(--label-2); line-height: 1.5; margin-bottom: 8px; }
        .risk-numbers {
            display: flex;
            gap: 16px;
        }
        .risk-num { text-align: center; }
        .risk-num-label { font-size: 11px; color: var(--label-2); }
        .risk-num-value { font-size: 16px; font-weight: 700; }
        .risk-loss-value { color: var(--red); }
        .risk-gain-value { color: var(--green); }

        /* Why section */
        .why-section {
            padding: 0 16px 16px;
        }
        .why-title { font-size: 13px; font-weight: 700; color: var(--label); margin-bottom: 8px; }
        .why-item {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding: 6px 0;
            font-size: 13px;
            color: var(--label-2);
            line-height: 1.4;
            border-bottom: 1px solid var(--gray5);
        }
        .why-item:last-child { border-bottom: none; }
        .why-dot {
            width: 6px; height: 6px;
            border-radius: 3px;
            background: var(--blue);
            margin-top: 4px;
            flex-shrink: 0;
        }

        /* Targets */
        .targets-section {
            margin: 0 16px 16px;
            background: var(--gray6);
            border-radius: var(--r-md);
            overflow: hidden;
        }
        .targets-title { font-size: 12px; font-weight: 700; color: var(--label-2); padding: 10px 14px 6px; text-transform: uppercase; letter-spacing: 0.5px; }
        .target-row {
            display: flex;
            justify-content: space-between;
            padding: 9px 14px;
            font-size: 14px;
            border-top: 1px solid var(--sep);
        }
        .target-label { color: var(--label-2); }
        .target-value { font-weight: 600; }

        /* Warnings */
        .warn-pill {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: var(--orange-light);
            color: #BF6900;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
            margin: 0 16px 12px;
        }

        /* Outcome tracker */
        .outcome-section {
            padding: 0 16px 20px;
        }
        .outcome-title { font-size: 13px; font-weight: 700; color: var(--label-2); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.3px; }
        .outcome-btns { display: flex; gap: 8px; }
        .outcome-btn {
            flex: 1;
            padding: 11px;
            border-radius: var(--r-md);
            border: none;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.15s, transform 0.1s;
        }
        .outcome-btn:active { opacity: 0.8; transform: scale(0.97); }
        .outcome-win  { background: var(--green-light); color: #1A7F35; }
        .outcome-loss { background: var(--red-light);   color: #C0392B; }
        .outcome-even { background: var(--gray5);       color: var(--gray); }
        .outcome-thanks {
            background: var(--gray6);
            border-radius: var(--r-md);
            padding: 12px;
            font-size: 13px;
            color: var(--label-2);
            text-align: center;
            display: none;
        }

        /* ── Secondary actions ── */
        .actions-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .action-card {
            background: var(--bg-card);
            border-radius: var(--r-lg);
            box-shadow: var(--shadow-sm);
            padding: 18px 16px;
            border: none;
            cursor: pointer;
            text-align: left;
            transition: opacity 0.15s, transform 0.1s;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .action-card:active { opacity: 0.8; transform: scale(0.97); }
        .action-card-icon { font-size: 22px; margin-bottom: 6px; }
        .action-card-title { font-size: 15px; font-weight: 600; color: var(--label); }
        .action-card-sub   { font-size: 12px; color: var(--label-2); }
        .action-card.loading .action-card-title::after {
            content: '…'; animation: ellipsis 1s steps(3, end) infinite;
        }
        @keyframes ellipsis { 0%,100%{content:'.'} 33%{content:'..'} 66%{content:'...'} }

        /* ── Results list ── */
        .results-section { display: none; }
        .results-section.visible { display: block; }
        .result-card {
            background: var(--bg-card);
            border-radius: var(--r-lg);
            box-shadow: var(--shadow-sm);
            padding: 16px;
            margin-bottom: 12px;
            cursor: pointer;
        }
        .rc-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
        .rc-ticker { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; }
        .rc-company { font-size: 12px; color: var(--label-2); margin-top: 2px; }
        .rc-metrics {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-top: 12px;
        }
        .rc-metric { text-align: center; }
        .rc-metric-label { font-size: 10px; color: var(--label-2); font-weight: 500; }
        .rc-metric-value { font-size: 14px; font-weight: 600; margin-top: 2px; }
        .rc-detail {
            display: none;
            margin-top: 14px;
            padding-top: 14px;
            border-top: 1px solid var(--gray5);
        }
        .rc-detail.open { display: block; }
        .rc-reasoning {
            font-size: 13px;
            color: var(--label-2);
            line-height: 1.5;
            margin-bottom: 10px;
        }
        .rc-targets { background: var(--gray6); border-radius: var(--r-sm); padding: 10px 12px; }
        .rc-target-row { display: flex; justify-content: space-between; font-size: 13px; padding: 4px 0; }

        /* Fundamental / behavior pills */
        .signal-row {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }
        .signal-pill {
            background: var(--gray6);
            color: var(--label-2);
            font-size: 11px;
            font-weight: 500;
            padding: 3px 8px;
            border-radius: 20px;
        }
        .signal-pill.pos { background: var(--green-light); color: #1A7F35; }
        .signal-pill.neg { background: var(--red-light);   color: #C0392B; }

        /* ── Settings sheet ── */
        .sheet-overlay {
            display: none;
            position: fixed; inset: 0;
            background: rgba(0,0,0,0.4);
            z-index: 200;
            -webkit-backdrop-filter: blur(4px);
            backdrop-filter: blur(4px);
        }
        .sheet-overlay.open { display: flex; align-items: flex-end; justify-content: center; }
        .settings-sheet {
            background: var(--bg-card);
            border-radius: var(--r-xl) var(--r-xl) 0 0;
            width: 100%;
            max-width: 680px;
            max-height: 85dvh;
            overflow-y: auto;
            padding: 8px 0 env(safe-area-inset-bottom, 16px);
            animation: slideUp 0.28s ease;
        }
        @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
        .sheet-handle {
            width: 36px; height: 5px;
            background: var(--gray4);
            border-radius: 3px;
            margin: 8px auto 16px;
        }
        .sheet-title { font-size: 17px; font-weight: 700; text-align: center; margin-bottom: 20px; }
        .settings-group { margin: 0 16px 20px; }
        .settings-group-title { font-size: 12px; font-weight: 600; color: var(--label-2); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        .settings-list { background: var(--bg-card); border-radius: var(--r-md); border: 1px solid var(--sep); overflow: hidden; }
        .settings-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 13px 16px;
            border-bottom: 1px solid var(--sep);
        }
        .settings-row:last-child { border-bottom: none; }
        .settings-row-label { font-size: 15px; color: var(--label); }
        .settings-row input[type=number], .settings-row input[type=text] {
            border: none;
            outline: none;
            font-size: 15px;
            color: var(--blue);
            text-align: right;
            width: 90px;
            background: transparent;
            font-family: inherit;
        }
        .sector-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        .sector-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--gray6);
            padding: 10px 12px;
            border-radius: var(--r-sm);
            cursor: pointer;
            font-size: 14px;
        }
        .sector-pill input { margin: 0; accent-color: var(--blue); width: 18px; height: 18px; }
        .sheet-save {
            margin: 4px 16px 8px;
            width: calc(100% - 32px);
            padding: 15px;
            background: var(--blue);
            color: white;
            font-size: 17px;
            font-weight: 600;
            border: none;
            border-radius: var(--r-lg);
            cursor: pointer;
        }
        .sheet-save:active { opacity: 0.85; }

        /* ── Toast ── */
        .toast {
            position: fixed;
            bottom: calc(env(safe-area-inset-bottom, 0px) + 80px);
            left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.82);
            color: white;
            font-size: 14px;
            font-weight: 500;
            padding: 10px 20px;
            border-radius: 20px;
            z-index: 999;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            white-space: nowrap;
        }
        .toast.show { opacity: 1; }

        /* ── Landscape + iPad ── */
        @media (orientation: landscape) and (min-width: 700px) {
            .main-content {
                flex-direction: row;
                align-items: flex-start;
                padding: 20px;
            }
            .left-col {
                width: 360px;
                flex-shrink: 0;
                display: flex;
                flex-direction: column;
                gap: 16px;
                position: sticky;
                top: 72px;
            }
            .right-col {
                flex: 1;
                min-width: 0;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }
            .hero-card { padding: 24px 20px; }
            .hero-title { font-size: 22px; }
            .sheet-overlay { align-items: center; }
            .settings-sheet {
                border-radius: var(--r-xl);
                max-height: 90dvh;
                max-width: 500px;
                margin-bottom: 0;
            }
        }

        @media (min-width: 1024px) {
            .left-col { width: 420px; }
            .key-numbers { grid-template-columns: repeat(4, 1fr); }
        }

        /* ── Utilities ── */
        .green-text  { color: var(--green); }
        .red-text    { color: var(--red); }
        .blue-text   { color: var(--blue); }
        .orange-text { color: var(--orange); }
        .gray-text   { color: var(--label-2); }
        
    </style>
</head>
<body>

<div class="app-shell">

  <!-- ── Nav bar ── -->
  <header class="nav-bar">
    <div class="nav-inner">
      <span class="nav-title">Stock Advisor</span>
      <div class="nav-chips">
        <span class="chip chip-regime-unknown" id="regime-chip">Market</span>
        <span class="chip chip-vix-unknown"    id="vix-chip"   style="display:none">VIX</span>
        <span class="chip chip-win"            id="winrate-chip" style="display:none">—</span>
        <button class="icon-btn" onclick="openSettings()" title="Settings">⚙</button>
      </div>
    </div>
  </header>

  <!-- ── Main content ── -->
  <div class="main-content">

    <!-- ── LEFT COLUMN (hero + decision + actions) ── -->
    <div class="left-col">

      <!-- Hero -->
      <div class="hero-card">
        <div class="hero-eyebrow">AI-Powered Analysis</div>
        <div class="hero-title">What should I buy today?</div>
        <div class="hero-sub">Scans 500+ stocks using technicals, fundamentals &amp; human-behavior signals</div>
        <button class="pick-btn" id="pick-btn" onclick="pickForMe()">
          <span class="btn-icon">✦</span>
          <span class="btn-text">Pick For Me</span>
          <div class="spinner"></div>
        </button>
      </div>

      <!-- Decision card -->
      <div class="decision-card" id="decision-card">
        <div class="decision-header">
          <div>
            <div class="decision-ticker" id="d-ticker">—</div>
            <div class="decision-company" id="d-company"></div>
            <div id="d-near-earnings-warn" class="warn-pill" style="display:none;margin:8px 0 0;">
              ⚠ Earnings this week — elevated risk
            </div>
          </div>
          <div class="action-pill" id="d-action-pill">—</div>
        </div>

        <!-- Score bars -->
        <div class="score-section">
          <div class="score-row">
            <span class="score-label">Overall Score</span>
            <span class="score-value" id="d-score">—</span>
          </div>
          <div class="score-bar-track">
            <div class="score-bar-fill" id="d-score-bar" style="width:0%;background:var(--blue)"></div>
          </div>
          <div class="score-sub-row">
            <div class="score-sub-item">
              <span class="score-sub-label gray-text">Technical</span>
              <span class="score-sub-num" id="d-tech-score">—</span>
            </div>
            <div class="score-sub-item">
              <span class="score-sub-label gray-text">Fundamental</span>
              <span class="score-sub-num" id="d-fund-score">—</span>
            </div>
            <div class="score-sub-item">
              <span class="score-sub-label gray-text">Human Signals</span>
              <span class="score-sub-num" id="d-behav-score">—</span>
            </div>
            <div class="score-sub-item">
              <span class="score-sub-label gray-text">vs S&amp;P 500</span>
              <span class="score-sub-num" id="d-rs">—</span>
            </div>
          </div>
        </div>

        <!-- Key numbers: entry / stop / target -->
        <div class="key-numbers">
          <div class="kn-cell">
            <div class="kn-label">Entry Price</div>
            <div class="kn-value" id="d-entry">—</div>
          </div>
          <div class="kn-cell">
            <div class="kn-label">Stop Loss</div>
            <div class="kn-value red-text" id="d-stop">—</div>
          </div>
          <div class="kn-cell">
            <div class="kn-label">Take Profit</div>
            <div class="kn-value green-text" id="d-target">—</div>
          </div>
        </div>

        <!-- Risk panel -->
        <div style="padding:16px 16px 0">
          <div class="risk-panel" id="d-risk-panel">
            <div class="risk-header">
              <span class="risk-title">What if it's wrong?</span>
              <span id="d-weekly-trend" style="font-size:12px;font-weight:600"></span>
            </div>
            <p class="risk-explainer">
              The stop-loss is your safety net. If the stock falls to that price, 
              you exit automatically — limiting your loss to the amount below.
              The system tracks every trade outcome and surfaces what's working.
            </p>
            <div class="risk-numbers">
              <div class="risk-num">
                <div class="risk-num-label">Max Loss</div>
                <div class="risk-num-value risk-loss-value" id="d-max-loss">—</div>
              </div>
              <div class="risk-num">
                <div class="risk-num-label">Max Gain</div>
                <div class="risk-num-value risk-gain-value" id="d-max-gain">—</div>
              </div>
              <div class="risk-num">
                <div class="risk-num-label">Shares</div>
                <div class="risk-num-value" id="d-shares">—</div>
              </div>
              <div class="risk-num">
                <div class="risk-num-label">RSI</div>
                <div class="risk-num-value" id="d-rsi">—</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Why this stock -->
        <div class="why-section" style="margin-top:16px">
          <div class="why-title">Why this stock</div>
          <div id="d-why-list"></div>
        </div>

        <!-- Price targets -->
        <div class="targets-section">
          <div class="targets-title">Price Targets</div>
          <div class="target-row">
            <span class="target-label">Today range</span>
            <span class="target-value" id="d-today-range">—</span>
          </div>
          <div class="target-row">
            <span class="target-label">1-week target</span>
            <span class="target-value green-text" id="d-week">—</span>
          </div>
          <div class="target-row">
            <span class="target-label">1-month target</span>
            <span class="target-value green-text" id="d-month">—</span>
          </div>
        </div>

        <!-- News / patterns -->
        <div id="d-signals-row" class="signal-row" style="padding:0 16px 12px"></div>

        <!-- Outcome tracker -->
        <div class="outcome-section">
          <div class="outcome-title">Track this trade (builds your win rate)</div>
          <div class="outcome-btns" id="outcome-btns">
            <button class="outcome-btn outcome-win"  onclick="recordOutcome('win')">Win</button>
            <button class="outcome-btn outcome-even" onclick="recordOutcome('breakeven')">Break-even</button>
            <button class="outcome-btn outcome-loss" onclick="recordOutcome('loss')">Loss</button>
          </div>
          <div class="outcome-thanks" id="outcome-thanks">
            Logged ✓ — win rate updated in the header.
          </div>
          <p style="font-size:11px;color:var(--label-2);margin-top:8px;line-height:1.4">
            Over time the system uses your outcomes to fine-tune which signals matter most for your portfolio.
          </p>
        </div>
      </div>

      <!-- Secondary actions -->
      <div class="actions-row">
        <button class="action-card" id="btn-analyze" onclick="runAnalysis()">
          <div class="action-card-icon">🔍</div>
          <div class="action-card-title">Analyze All</div>
          <div class="action-card-sub">Scan enabled sectors</div>
        </button>
        <button class="action-card" onclick="toggleResults()">
          <div class="action-card-icon">📋</div>
          <div class="action-card-title">All Results</div>
          <div class="action-card-sub" id="results-count-label">Run analysis first</div>
        </button>
      </div>

    </div><!-- /left-col -->

    <!-- ── RIGHT COLUMN (all results) ── -->
    <div class="right-col">
      <div class="results-section" id="results-section">
        <div class="section-label" style="font-size:16px;color:var(--label-2)">All Results</div>
        <div id="results-list"></div>
      </div>
    </div>

  </div><!-- /main-content -->

</div><!-- /app-shell -->

<!-- ── Settings sheet ── -->
<div class="sheet-overlay" id="sheet-overlay" onclick="overlayClick(event)">
  <div class="settings-sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-title">Settings</div>

    <div class="settings-group">
      <div class="settings-group-title">Portfolio</div>
      <div class="settings-list">
        <div class="settings-row">
          <span class="settings-row-label">Capital ($)</span>
          <input type="number" id="s-capital" value="2400" min="100" step="100">
        </div>
        <div class="settings-row">
          <span class="settings-row-label">Position Size (%)</span>
          <input type="number" id="s-position" value="10" min="1" max="100">
        </div>
        <div class="settings-row">
          <span class="settings-row-label">Stop Loss (%)</span>
          <input type="number" id="s-stop" value="5" min="1" max="20">
        </div>
        <div class="settings-row">
          <span class="settings-row-label">Take Profit (%)</span>
          <input type="number" id="s-profit" value="10" min="1" max="50">
        </div>
        <div class="settings-row">
          <span class="settings-row-label">Top Results</span>
          <input type="number" id="s-topn" value="20" min="5" max="50">
        </div>
        <div class="settings-row">
          <span class="settings-row-label">Min Score</span>
          <input type="number" id="s-minscore" value="50" min="0" max="100">
        </div>
      </div>
    </div>

    <div class="settings-group">
      <div class="settings-group-title">Sectors (2-3 recommended)</div>
      <div class="sector-grid" id="sector-grid"></div>
    </div>

    <button class="sheet-save" onclick="saveSettings()">Save Settings</button>
  </div>
</div>

<!-- ── Toast ── -->
<div class="toast" id="toast"></div>

<script>
/* ── State ── */
let cfg = {};
let latestResults = null;
let currentPick = null;
let resultsVisible = false;

/* ── Boot ── */
(async function init() {
  await loadConfig();
  await refreshOutcomes();
})();

/* ── Config ── */
async function loadConfig() {
  try {
    const r = await fetch('/api/config');
    cfg = await r.json();
    applyConfigToSheet(cfg);
    updateCapitalDisplay();
  } catch(e) { console.error(e); }
}

function applyConfigToSheet(c) {
  document.getElementById('s-capital').value   = c.capital            || 2400;
  document.getElementById('s-position').value  = c.position_size_pct  || 10;
  document.getElementById('s-stop').value      = c.stop_loss_pct      || 5;
  document.getElementById('s-profit').value    = c.take_profit_pct    || 10;
  document.getElementById('s-topn').value      = c.top_opportunities  || 20;
  document.getElementById('s-minscore').value  = c.min_score          || 50;

  const sectors = {{ sectors | tojson }};
  const grid = document.getElementById('sector-grid');
  grid.innerHTML = '';
  sectors.forEach(s => {
    const on = (c.enabled_sectors || []).includes(s);
    grid.innerHTML += `
      <label class="sector-pill">
        <input type="checkbox" id="sec-${s}" ${on ? 'checked' : ''}>
        ${s.replace(/_/g,' ')}
      </label>`;
  });
}

function updateCapitalDisplay() {
  /* nothing in nav bar but win-rate chip updated elsewhere */
}

async function saveSettings() {
  const sectors = {{ sectors | tojson }};
  const enabled = sectors.filter(s => document.getElementById('sec-'+s)?.checked);
  const newCfg = {
    capital:            parseInt(document.getElementById('s-capital').value),
    position_size_pct:  parseInt(document.getElementById('s-position').value),
    stop_loss_pct:      parseInt(document.getElementById('s-stop').value),
    take_profit_pct:    parseInt(document.getElementById('s-profit').value),
    top_opportunities:  parseInt(document.getElementById('s-topn').value),
    min_score:          parseInt(document.getElementById('s-minscore').value),
    enabled_sectors:    enabled,
  };
  await fetch('/api/config', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(newCfg)
  });
  cfg = newCfg;
  closeSettings();
  toast('Settings saved');
}

/* ── Settings sheet ── */
function openSettings()  { document.getElementById('sheet-overlay').classList.add('open'); }
function closeSettings() { document.getElementById('sheet-overlay').classList.remove('open'); }
function overlayClick(e) { if (e.target === document.getElementById('sheet-overlay')) closeSettings(); }

/* ── Pick For Me ── */
async function pickForMe() {
  const btn = document.getElementById('pick-btn');
  btn.disabled = true;
  btn.classList.add('loading');
  btn.querySelector('.btn-text').textContent = 'Analyzing…';

  try {
    const r = await fetch('/api/pick', { method: 'POST' });
    const data = await r.json();

    if (!r.ok) { toast('Error: ' + (data.error || 'Unknown')); return; }

    currentPick = data.pick;
    renderDecisionCard(data);

    // Update regime chip
    if (data.market_regime) {
      const regime = data.market_regime.regime || 'unknown';
      const vix    = data.market_regime.vix;
      const fear   = data.market_regime.fear_level || 'unknown';
      const rc = document.getElementById('regime-chip');
      rc.textContent = regime.replace(/_/g,' ').toUpperCase();
      rc.className = 'chip chip-regime-' + regime;
      if (vix !== null && vix !== undefined) {
        const vc = document.getElementById('vix-chip');
        vc.textContent = 'VIX ' + vix.toFixed(0) + ' · ' + fear.replace(/_/g,' ');
        vc.className   = 'chip chip-vix-' + fear;
        vc.style.display = '';
      }
    }

  } catch(e) {
    toast('Network error — check server');
    console.error(e);
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.querySelector('.btn-text').textContent = 'Pick Again';
  }
}

function renderDecisionCard(data) {
  const p = data.pick;
  const card = document.getElementById('decision-card');

  document.getElementById('d-ticker').textContent  = p.symbol;
  document.getElementById('d-company').textContent = p.company_name + ' · ' + p.sector;

  const pill = document.getElementById('d-action-pill');
  pill.textContent = p.action;
  pill.className   = 'action-pill pill-' + p.action;

  /* Scores */
  const score = p.score;
  document.getElementById('d-score').textContent = score.toFixed(1) + ' / 100';
  const bar = document.getElementById('d-score-bar');
  bar.style.width = score + '%';
  bar.style.background = score >= 70 ? 'var(--green)' : score >= 55 ? 'var(--blue)' : 'var(--orange)';

  document.getElementById('d-tech-score').textContent  = p.tech_score.toFixed(0);
  document.getElementById('d-fund-score').textContent  = p.fundamental_score.toFixed(0);
  document.getElementById('d-behav-score').textContent = p.behavior_score.toFixed(0);

  const rs = p.rs_vs_spy;
  const rsEl = document.getElementById('d-rs');
  rsEl.textContent = (rs >= 0 ? '+' : '') + rs.toFixed(1) + '%';
  rsEl.className   = 'score-sub-num ' + (rs >= 0 ? 'green-text' : 'red-text');

  /* Key numbers */
  document.getElementById('d-entry').textContent  = '$' + p.current_price.toFixed(2);
  document.getElementById('d-stop').textContent   = '$' + p.stop_loss.toFixed(2);
  document.getElementById('d-target').textContent = '$' + p.take_profit.toFixed(2);

  /* Risk panel */
  document.getElementById('d-max-loss').textContent = '-$' + p.max_loss_dollars.toFixed(2);
  document.getElementById('d-max-gain').textContent = '+$' + p.max_gain_dollars.toFixed(2);
  document.getElementById('d-shares').textContent   = p.shares + ' shares';
  document.getElementById('d-rsi').textContent      = p.rsi.toFixed(0);

  const weekly = p.weekly_trend;
  const wEl = document.getElementById('d-weekly-trend');
  if (weekly && weekly !== 'unknown') {
    wEl.textContent  = '📅 Weekly ' + weekly;
    wEl.className    = weekly === 'bullish' ? 'green-text' : 'red-text';
  }

  /* Earnings warning */
  document.getElementById('d-near-earnings-warn').style.display = p.near_earnings ? '' : 'none';

  /* Why list */
  const bullets = buildWhyBullets(p);
  const whyEl = document.getElementById('d-why-list');
  whyEl.innerHTML = bullets.map(b =>
    `<div class="why-item"><div class="why-dot"></div><span>${b}</span></div>`
  ).join('');

  /* Targets */
  document.getElementById('d-today-range').textContent =
    '$' + p.targets.today_low.toFixed(2) + ' – $' + p.targets.today_high.toFixed(2);
  document.getElementById('d-week').textContent  = '$' + p.targets.week.toFixed(2);
  document.getElementById('d-month').textContent = '$' + p.targets.month.toFixed(2);

  /* Signal pills */
  const sigRow = document.getElementById('d-signals-row');
  sigRow.innerHTML = '';
  (p.key_signals || []).slice(0, 5).forEach(s => {
    const isNeg = /declin|high debt|negat|sell|expensive/i.test(s);
    sigRow.innerHTML += `<span class="signal-pill ${isNeg ? 'neg' : 'pos'}">${s}</span>`;
  });
  if (p.patterns?.length) {
    p.patterns.forEach(pt => {
      sigRow.innerHTML += `<span class="signal-pill">${pt}</span>`;
    });
  }
  if (p.news_sentiment && p.news_sentiment !== 'neutral') {
    const isNeg = p.news_sentiment === 'negative';
    sigRow.innerHTML += `<span class="signal-pill ${isNeg ? 'neg' : 'pos'}">News: ${p.news_sentiment}</span>`;
  }

  /* Reset outcome tracker */
  document.getElementById('outcome-btns').style.display    = 'flex';
  document.getElementById('outcome-thanks').style.display  = 'none';

  card.classList.add('visible');
  card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function buildWhyBullets(p) {
  const parts = [];
  /* Action rationale */
  if (p.action === 'BUY') {
    if (p.rsi < 35) parts.push(`RSI ${p.rsi.toFixed(0)} — oversold, potential bounce`);
    if (p.momentum_1m > 2) parts.push(`+${p.momentum_1m.toFixed(1)}% momentum last month — trend in your favor`);
    if (p.tech_score > 65) parts.push(`Technical score ${p.tech_score.toFixed(0)} — strong chart setup`);
  } else if (p.action === 'SELL') {
    if (p.rsi > 65) parts.push(`RSI ${p.rsi.toFixed(0)} — overbought, potential pullback`);
    if (p.momentum_1m < -2) parts.push(`${p.momentum_1m.toFixed(1)}% momentum — selling pressure active`);
  } else {
    parts.push('Mixed signals — waiting for a clearer entry or exit point');
  }
  if (p.rs_vs_spy > 3)  parts.push(`Outperforming S&P 500 by ${p.rs_vs_spy.toFixed(1)}% — market leader`);
  if (p.rs_vs_spy < -3) parts.push(`Underperforming S&P 500 by ${Math.abs(p.rs_vs_spy).toFixed(1)}% — lagging`);
  if (p.weekly_trend === 'bullish') parts.push('Weekly chart bullish — daily and weekly trends aligned');
  /* Fundamental */
  if (p.fundamental_score >= 65) parts.push(`Strong fundamentals (score ${p.fundamental_score.toFixed(0)}) — healthy business`);
  /* Analyst */
  if (p.behavior_score >= 65) parts.push(`Analyst &amp; institutional signals positive (score ${p.behavior_score.toFixed(0)})`);
  /* ATR stop */
  if (p.atr_14) parts.push(`Stop loss set at 2× ATR ($${p.atr_14.toFixed(2)} avg daily range) — adapts to this stock's volatility`);
  /* Near earnings */
  if (p.near_earnings) parts.push('Earnings due soon — extra caution advised, consider smaller position');
  return parts.slice(0, 6);
}

/* ── Outcome tracking ── */
async function recordOutcome(outcome) {
  if (!currentPick) return;
  const r = await fetch('/api/outcome', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      symbol:  currentPick.symbol,
      outcome: outcome,
      score:   currentPick.score,
      action:  currentPick.action,
    })
  });
  const data = await r.json();
  document.getElementById('outcome-btns').style.display   = 'none';
  document.getElementById('outcome-thanks').style.display = 'block';
  updateWinRateChip(data.win_rate, data.total_trades);
  toast(outcome === 'win' ? '✓ Win logged!' : outcome === 'loss' ? 'Loss logged — system learns from this.' : 'Break-even logged.');
}

async function refreshOutcomes() {
  try {
    const r = await fetch('/api/outcomes');
    const d = await r.json();
    if (d.total_trades > 0) updateWinRateChip(d.win_rate, d.total_trades);
  } catch(e) {}
}

function updateWinRateChip(rate, total) {
  const el = document.getElementById('winrate-chip');
  el.textContent = rate.toFixed(0) + '% wins (' + total + ' trades)';
  el.style.display = '';
}

/* ── Analyze All ── */
async function runAnalysis() {
  const btn = document.getElementById('btn-analyze');
  btn.classList.add('loading');
  btn.querySelector('.action-card-title').textContent = 'Analyzing…';

  try {
    const r = await fetch('/api/analyze', { method: 'POST', headers: {'Content-Type':'application/json'} });
    if (!r.ok) { const e = await r.json(); toast('Error: '+(e.error||'Server error')); return; }
    latestResults = await r.json();

    const count = latestResults.top_opportunities?.length || 0;
    document.getElementById('results-count-label').textContent = count + ' stocks found';
    toast('Analysis complete — ' + count + ' results');
  } catch(e) {
    toast('Network error');
  } finally {
    btn.classList.remove('loading');
    btn.querySelector('.action-card-title').textContent = 'Analyze All';
  }
}

/* ── All results ── */
function toggleResults() {
  if (!latestResults) { toast('Run Analyze All first'); return; }
  resultsVisible = !resultsVisible;
  const sec = document.getElementById('results-section');
  if (resultsVisible) {
    sec.classList.add('visible');
    renderAllResults();
    sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } else {
    sec.classList.remove('visible');
  }
}

function renderAllResults() {
  const list = document.getElementById('results-list');
  list.innerHTML = '';
  const opps = latestResults.top_opportunities || [];
  opps.forEach((opp, i) => {
    const action = opp.predictions?.action || 'HOLD';
    const score  = opp.score?.toFixed(1) || '—';
    const rsi    = opp.factors?.rsi?.toFixed(0) || '—';
    const mom    = opp.factors?.momentum?.['1m'];
    const momStr = mom !== undefined ? (mom*100).toFixed(1)+'%' : '—';
    const fund   = opp.fundamental?.score?.toFixed(0) || '—';
    const behav  = opp.behavior?.score?.toFixed(0) || '—';
    const rs     = opp.relative_strength_vs_spy;
    const rsStr  = rs !== undefined ? (rs>=0?'+':'')+( rs*100).toFixed(1)+'%' : '—';
    const entryPr = opp.current_price?.toFixed(2) || '—';
    const weekTgt = opp.predictions?.predictions?.week?.target?.toFixed(2) || '—';
    const reasoning = opp.predictions?.reasoning || '';

    list.innerHTML += `
      <div class="result-card" onclick="toggleDetail(this, ${i})">
        <div class="rc-top">
          <div>
            <div class="rc-ticker">${opp.symbol}</div>
            <div class="rc-company">${opp.company_name || ''}</div>
          </div>
          <div class="action-pill pill-${action}">${action}</div>
        </div>
        <div class="rc-metrics">
          <div class="rc-metric">
            <div class="rc-metric-label">Score</div>
            <div class="rc-metric-value">${score}</div>
          </div>
          <div class="rc-metric">
            <div class="rc-metric-label">RSI</div>
            <div class="rc-metric-value" style="color:${rsi<30?'var(--green)':rsi>70?'var(--red)':'inherit'}">${rsi}</div>
          </div>
          <div class="rc-metric">
            <div class="rc-metric-label">Momentum</div>
            <div class="rc-metric-value" style="color:${mom>0?'var(--green)':'var(--red)'}">${momStr}</div>
          </div>
          <div class="rc-metric">
            <div class="rc-metric-label">vs SPY</div>
            <div class="rc-metric-value" style="color:${rs>=0?'var(--green)':'var(--red)'}">${rsStr}</div>
          </div>
        </div>
        <div class="rc-detail" id="detail-${i}">
          <div class="rc-reasoning">${reasoning}</div>
          <div class="rc-targets">
            <div class="rc-target-row"><span>Entry</span><strong>$${entryPr}</strong></div>
            <div class="rc-target-row"><span>1-week target</span><strong class="green-text">$${weekTgt}</strong></div>
            <div class="rc-target-row"><span>Fundamental</span><strong>${fund}/100</strong></div>
            <div class="rc-target-row"><span>Human signals</span><strong>${behav}/100</strong></div>
          </div>
        </div>
      </div>`;
  });
}

function toggleDetail(card, idx) {
  const detail = document.getElementById('detail-' + idx);
  detail.classList.toggle('open');
}

/* ── Toast ── */
function toast(msg, ms = 2800) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), ms);
}
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

    stock = next((s for s in latest_results['all_stocks'] if s['symbol'] == symbol), None)

    if not stock:
        return jsonify({'error': 'Stock not found'}), 404

    capital = analyzer.config.get('capital', 2400)
    recommendation = analyzer.format_recommendation(stock, capital)

    return jsonify(recommendation)


@app.route('/api/pick', methods=['POST'])
def pick_best():
    """Return the single best trade right now across all analyzed stocks."""
    global analyzer, latest_results

    try:
        if analyzer is None:
            config = load_config()
            analyzer = LiveTradingAnalyzer(config)

        # Run fresh analysis if we have no data yet
        if latest_results is None:
            log_progress('Running analysis for Pick For Me…', 'info')
            enabled_sectors = analyzer.config.get('enabled_sectors', [])
            if len(enabled_sectors) > 3:
                enabled_sectors = enabled_sectors[:3]
            latest_results = analyzer.run_analysis(
                enabled_sectors=enabled_sectors,
                top_n=analyzer.config.get('top_opportunities', 20)
            )

        capital = analyzer.config.get('capital', 2400)

        # Find the highest-scored BUY; fall back to #1 overall
        best = None
        for opp in latest_results.get('top_opportunities', []):
            if opp.get('predictions', {}).get('action') == 'BUY':
                best = opp
                break
        if best is None and latest_results.get('top_opportunities'):
            best = latest_results['top_opportunities'][0]

        if best is None:
            return jsonify({'error': 'No stocks found. Enable more sectors and re-analyze.'}), 404

        rec = analyzer.format_recommendation(best, capital)

        # Risk calculations
        entry_price = best['current_price']
        stop_loss   = rec['stop_loss']
        take_profit = rec['take_profit']
        shares      = rec['shares']
        max_loss_dollars = round(shares * max(0, entry_price - stop_loss), 2)
        max_gain_dollars = round(shares * max(0, take_profit - entry_price), 2)
        max_loss_pct     = round((entry_price - stop_loss) / entry_price * 100, 2) if entry_price > 0 else 0

        # Fundamental + behavior signal bullets
        fundamental = best.get('fundamental', {})
        behavior    = best.get('behavior', {})
        key_signals = (
            fundamental.get('signals', [])[:3]
            + behavior.get('signals', [])[:3]
        )

        return jsonify({
            'pick': {
                'symbol':           best['symbol'],
                'company_name':     best['company_name'],
                'sector':           best.get('sector', ''),
                'action':           rec['action'],
                'current_price':    entry_price,
                'stop_loss':        stop_loss,
                'take_profit':      take_profit,
                'shares':           shares,
                'position_value':   rec['position_value'],
                'score':            round(best['score'], 1),
                'tech_score':       round(best.get('tech_score', best['score']), 1),
                'fundamental_score': round(fundamental.get('score', 50), 1),
                'behavior_score':   round(behavior.get('score', 50), 1),
                'rsi':              round(best['factors']['rsi'], 1),
                'momentum_1m':      round(best['factors']['momentum']['1m'] * 100, 1),
                'weekly_trend':     best['factors']['trend'].get('weekly', 'unknown'),
                'near_earnings':    best.get('near_earnings', False),
                'rs_vs_spy':        round(best.get('relative_strength_vs_spy', 0) * 100, 1),
                'max_loss_dollars': max_loss_dollars,
                'max_gain_dollars': max_gain_dollars,
                'max_loss_pct':     max_loss_pct,
                'reasoning':        rec['reasoning'],
                'key_signals':      key_signals,
                'patterns':         [p['pattern'] for p in best.get('patterns', [])],
                'news_sentiment':   best.get('news', {}).get('sentiment', 'neutral'),
                'targets': {
                    'today_high': round(best['predictions']['predictions']['today']['target_high'], 2),
                    'today_low':  round(best['predictions']['predictions']['today']['target_low'], 2),
                    'week':       round(best['predictions']['predictions']['week']['target'], 2),
                    'month':      round(best['predictions']['predictions']['month']['target'], 2),
                },
                'atr_14': rec.get('atr_14'),
                'regime': best.get('regime', ''),
            },
            'market_regime': latest_results['market_regime'],
            'analyzed_stocks': latest_results['total_analyzed'],
            'timestamp': latest_results['timestamp'],
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/outcome', methods=['POST'])
def record_outcome():
    """Record a trade outcome (win/loss/breakeven) for win-rate tracking."""
    data = request.json or {}
    symbol  = data.get('symbol', 'UNKNOWN')
    outcome = data.get('outcome', 'unknown')  # 'win' | 'loss' | 'breakeven'

    outcomes_file = 'trade_outcomes.json'
    outcomes = []
    if os.path.exists(outcomes_file):
        try:
            with open(outcomes_file) as f:
                outcomes = json.load(f)
        except Exception:
            outcomes = []

    outcomes.append({
        'symbol':    symbol,
        'outcome':   outcome,
        'score':     data.get('score'),
        'action':    data.get('action'),
        'timestamp': datetime.now().isoformat(),
    })

    with open(outcomes_file, 'w') as f:
        json.dump(outcomes, f, indent=2)

    wins  = sum(1 for o in outcomes if o['outcome'] == 'win')
    total = len(outcomes)
    return jsonify({
        'status':       'recorded',
        'win_rate':     round(wins / total * 100, 1) if total else 0,
        'total_trades': total,
        'wins':         wins,
    })


@app.route('/api/outcomes', methods=['GET'])
def get_outcomes():
    """Return win-rate stats and recent trade history."""
    outcomes_file = 'trade_outcomes.json'
    outcomes = []
    if os.path.exists(outcomes_file):
        try:
            with open(outcomes_file) as f:
                outcomes = json.load(f)
        except Exception:
            pass

    wins   = sum(1 for o in outcomes if o['outcome'] == 'win')
    losses = sum(1 for o in outcomes if o['outcome'] == 'loss')
    total  = len(outcomes)
    return jsonify({
        'outcomes':     outcomes[-20:],
        'win_rate':     round(wins / total * 100, 1) if total else 0,
        'total_trades': total,
        'wins':         wins,
        'losses':       losses,
    })

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
