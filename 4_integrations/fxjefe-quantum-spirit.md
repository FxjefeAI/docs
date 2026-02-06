---
title: FXJEFE Quantum Spirit
description: Repository layout and file inventory for FXJEFE-Quantum-Spirit.
index: 4
---

Use this reference to verify the expected repository structure and source file inventory for the FXJEFE-Quantum-Spirit project.

## Repository structure

```
FXJEFE-Quantum-Spirit/
├── .github/
│   └── workflows/
│       └── python-tests.yml          # GitHub Actions CI
├── docs/
│   ├── EVALUATION_FRAMEWORK_README.md
│   ├── EVALUATION_INTEGRATION_GUIDE.md
│   ├── EVALUATION_FRAMEWORK_COMPLETE.txt
│   ├── SETUP_GUIDE.md
│   ├── DEPLOYMENT_SUMMARY.txt
│   ├── TRACING_README.md
│   ├── FTMO_SECURE_SETUP_COMPLETE.md
│   └── claude_context_summary.txt
├── src/
│   ├── servers/                      # All server variants
│   │   ├── main_server.py
│   │   ├── ai_server.py
│   │   ├── ai_servernwew.py
│   │   ├── ml_server.py
│   │   ├── lstm_server.py
│   │   ├── fxjefe_main_server.py
│   │   ├── fxjefe_god_server_8080.py
│   │   ├── fxjefe_main_8080_fixed.py
│   │   ├── fxjefe_final_8080.py
│   │   ├── fxjefe_final_live_server.py
│   │   ├── fxjefe_final_working.py
│   │   ├── fxjefe_perfect_server.py
│   │   ├── fxjefe_perfect_final.py
│   │   ├── fxjefe_nr3_final.py
│   │   ├── fxjefe_flask_dev_server.py
│   │   ├── fxjefe_flask_ltdm_compat.py
│   │   ├── fxjefe_live_sentiment_server.py
│   │   ├── fxjefe_sentiment_server.py
│   │   ├── fxjefe_sentiment_server777.py
│   │   ├── fxjefe_sentiment_server888.py
│   │   ├── sentiment_api_8081.py
│   │   ├── fxjefe_xgboost_api.py
│   │   ├── fxjefe_xgboost_server.py
│   │   ├── fxjefe_zmq_server.py
│   │   └── test_server.py
│   ├── features/                     # Feature engineering & generation
│   │   ├── feature_engineering.py
│   │   ├── feature_engineerinnewg.py
│   │   ├── generate_features.py
│   │   ├── GenerateFeatures.py
│   │   ├── GenerateFeaturesHTTP.py
│   │   ├── GenerateFeaturesOllama.py
│   │   ├── generate_synthetic_features - Copy.py
│   │   └── FEATURE_DIAGNOSTIC.py
│   ├── models/                       # Model predictions & ensembles
│   │   ├── ensemble_predictions.py
│   │   ├── generate_signals_with_xgboost.py
│   │   ├── xgboost_predictions_api.py
│   │   └── model_test_script.py
│   ├── evaluation/                   # Evaluation framework
│   │   ├── evaluation_framework.py
│   │   ├── evaluation_integration.py
│   │   └── backtest_validation.py
│   ├── trading/                      # Trading & risk management
│   │   ├── trading_integration.py
│   │   ├── risk_managementnew.py
│   │   ├── process_trades.py
│   │   ├── mt5_signal_script.py
│   │   ├── mt5_data_syncNEW.py
│   │   ├── test_mt5_signals.py
│   │   ├── switch_account.py
│   │   ├── secure_mt5_manager.py
│   │   ├── setup_secure_ftmo.py
│   │   └── unlock_ftmo.py
│   ├── pipeline/                     # Data pipeline & processing
│   │   ├── pipeline.py
│   │   ├── Load_and_process.py
│   │   ├── generate_labels.py
│   │   ├── generate_new_csv.py
│   │   ├── future_return.py
│   │   └── future_returnnew.py
│   ├── tracing/                      # OpenTelemetry tracing
│   │   ├── tracing.py
│   │   ├── tracing_config.py
│   │   ├── TRACING_INTEGRATION_GUIDE.py
│   │   └── tracing_wrapper.py
│   ├── agents/                       # AI agents
│   │   ├── ai_agentic_agent.py
│   │   ├── FXJEFE_MASTER_CONTROL.py
│   │   └── FXJEFE_MASTER_CONTROL_FINAL.py
│   └── utils/                        # Utilities & fixes
│       ├── path_resolver.py
│       ├── log.py
│       ├── sitecustomize.py
│       ├── format_all_python_files.py
│       ├── fix_csv.py
│       ├── fix_csv_encoding.py
│       ├── fix_paths.py
│       ├── fxjefe_fix_everything.py
│       └── DIAGNOSTIC_AND_FIX.py
├── scripts/
│   ├── evaluate_all_models.py
│   ├── fxjefe_evaluation_server.py
│   └── monitor_model_gates.py
├── evaluation_framework_demo.ipynb
├── "Below is a complete, full‑length co.txt"
├── .gitignore
└── README.md
```

Note: The structure above is transcribed verbatim from the provided inventory, including original spellings and file naming.

## Source file inventory

Proposed Repository Structure is perfect, you may now take control and copy these files to the correct framework:

The paths below are preserved verbatim from the provided inventory, including original spellings.

```
"C:\Users\nikod\Documents\FXJEFE_Project\claude_context_summary.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\ (2).gitignore"
"C:\Users\nikod\Documents\FXJEFE_Project\.gitattributes"
"C:\Users\nikod\Documents\FXJEFE_Project\CHANGELOG.md"
"C:\Users\nikod\Documents\FXJEFE_Project\DEPLOYMENT_SUMMARY.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\TRACING_README.md"
"C:\Users\nikod\Documents\FXJEFE_Project\Below is a complete, full‑length co.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\.gitignore"
"C:\Users\nikod\Documents\FXJEFE_Project\FTMO_SECURE_SETUP_COMPLETE.md"
"C:\Users\nikod\Documents\FXJEFE_Project\unlock_ftmo.py"
"C:\Users\nikod\Documents\FXJEFE_Project\setup_secure_ftmo.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_sentiment_server888.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_xgboost_api.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_xgboost_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_zmq_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\generate_features.py"
"C:\Users\nikod\Documents\FXJEFE_Project\generate_labels.py"
"C:\Users\nikod\Documents\FXJEFE_Project\generate_new_csv.py"
"C:\Users\nikod\Documents\FXJEFE_Project\generate_signals_with_xgboost.py"
"C:\Users\nikod\Documents\FXJEFE_Project\generate_synthetic_features - Copy.py"
"C:\Users\nikod\Documents\FXJEFE_Project\GenerateFeatures.py"
"C:\Users\nikod\Documents\FXJEFE_Project\GenerateFeaturesHTTP.py"
"C:\Users\nikod\Documents\FXJEFE_Project\GenerateFeaturesOllama.py"
"C:\Users\nikod\Documents\FXJEFE_Project\Load_and_process.py"
"C:\Users\nikod\Documents\FXJEFE_Project\log.py"
"C:\Users\nikod\Documents\FXJEFE_Project\lstm_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\main_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\ml_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\model_test_script.py"
"C:\Users\nikod\Documents\FXJEFE_Project\mt5_data_syncNEW.py"
"C:\Users\nikod\Documents\FXJEFE_Project\mt5_signal_script.py"
"C:\Users\nikod\Documents\FXJEFE_Project\path_resolver.py"
"C:\Users\nikod\Documents\FXJEFE_Project\pipeline.py"
"C:\Users\nikod\Documents\FXJEFE_Project\process_trades.py"
"C:\Users\nikod\Documents\FXJEFE_Project\risk_managementnew.py"
"C:\Users\nikod\Documents\FXJEFE_Project\secure_mt5_manager.py"
"C:\Users\nikod\Documents\FXJEFE_Project\sentiment_api_8081.py"
"C:\Users\nikod\Documents\FXJEFE_Project\sitecustomize.py"
"C:\Users\nikod\Documents\FXJEFE_Project\switch_account.py"
"C:\Users\nikod\Documents\FXJEFE_Project\test_mt5_signals.py"
"C:\Users\nikod\Documents\FXJEFE_Project\test_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\tracing.py"
"C:\Users\nikod\Documents\FXJEFE_Project\tracing_config.py"
"C:\Users\nikod\Documents\FXJEFE_Project\TRACING_INTEGRATION_GUIDE.py"
"C:\Users\nikod\Documents\FXJEFE_Project\tracing_wrapper.py"
"C:\Users\nikod\Documents\FXJEFE_Project\trading_integration.py"
"C:\Users\nikod\Documents\FXJEFE_Project\walk_forward_matrix.py"
"C:\Users\nikod\Documents\FXJEFE_Project\xgboost_predictions_api.py"
"C:\Users\nikod\Documents\FXJEFE_Project\ai_agentic_agent.py"
"C:\Users\nikod\Documents\FXJEFE_Project\ai_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\ai_servernwew.py"
"C:\Users\nikod\Documents\FXJEFE_Project\backtest_validation.py"
"C:\Users\nikod\Documents\FXJEFE_Project\DIAGNOSTIC_AND_FIX.py"
"C:\Users\nikod\Documents\FXJEFE_Project\ensemble_predictions.py"
"C:\Users\nikod\Documents\FXJEFE_Project\evaluation_framework.py"
"C:\Users\nikod\Documents\FXJEFE_Project\evaluation_integration.py"
"C:\Users\nikod\Documents\FXJEFE_Project\FEATURE_DIAGNOSTIC.py"
"C:\Users\nikod\Documents\FXJEFE_Project\feature_engineering.py"
"C:\Users\nikod\Documents\FXJEFE_Project\feature_engineerinnewg.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fix_csv.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fix_csv_encoding.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fix_paths.py"
"C:\Users\nikod\Documents\FXJEFE_Project\future_return.py"
"C:\Users\nikod\Documents\FXJEFE_Project\future_returnnew.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_final_8080.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_final_live_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_final_working.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_fix_everything.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_flask_dev_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_flask_ltdm_compat.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_god_server_8080.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_live_sentiment_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_main_8080_fixed.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_main_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\FXJEFE_MASTER_CONTROL.py"
"C:\Users\nikod\Documents\FXJEFE_Project\FXJEFE_MASTER_CONTROL_FINAL.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_nr3_final.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_perfect_final.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_perfect_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_sentiment_server.py"
"C:\Users\nikod\Documents\FXJEFE_Project\fxjefe_sentiment_server777.py"
"C:\Users\nikod\Documents\FXJEFE_Project\format_all_python_files.py"
"C:\Users\nikod\Documents\FXJEFE_Project\SETUP_GUIDE.md"
"C:\Users\nikod\Documents\FXJEFE_Project\Untitled-1.js"
"C:\Users\nikod\Documents\FXJEFE_Project\config.json"
"C:\Users\nikod\Documents\FXJEFE_Project\FXJEFElogtxt.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\nul"
"C:\Users\nikod\Documents\FXJEFE_Project\Below is a drop‑in replacement for.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\LICENSE.md"
"C:\Users\nikod\Documents\FXJEFE_Project\README (2).md"
"C:\Users\nikod\Documents\FXJEFE_Project\SECURITY.md"
"C:\Users\nikod\Documents\FXJEFE_Project\README (1).md"
"C:\Users\nikod\Documents\FXJEFE_Project\README.md"
"C:\Users\nikod\Documents\FXJEFE_Project\AI_AGENT_DEVELOPMENT_GUIDE.md"
"C:\Users\nikod\Documents\FXJEFE_Project\requirements.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\Copy-MQL5Includes.ps1"
"C:\Users\nikod\Documents\FXJEFE_Project\accounts_config.json"
"C:\Users\nikod\Documents\FXJEFE_Project\playground-1.mongodb.js"
"C:\Users\nikod\Documents\FXJEFE_Project\playground-2.mongodb.js"
"C:\Users\nikod\Documents\FXJEFE_Project\files.zip"
"C:\Users\nikod\Documents\FXJEFE_Project\lightgbm.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\FXJEFE_LiveBridge.mq5"
"C:\Users\nikod\Documents\FXJEFE_Project\EVALUATION_FRAMEWORK_COMPLETE.txt"
"C:\Users\nikod\Documents\FXJEFE_Project\EVALUATION_INTEGRATION_GUIDE.md"
"C:\Users\nikod\Documents\FXJEFE_Project\EVALUATION_FRAMEWORK_README.md"
"C:\Users\nikod\Documents\FXJEFE_Project\evaluation_framework_demo.ipynb"
"C:\Users\nikod\Documents\FXJEFE_Project\tracing_edge_decay_notebook.ipynb"
"C:\Users\nikod\Documents\FXJEFE_Project\requirements-tracing.txt"
```
