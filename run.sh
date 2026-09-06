#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Freelancing CRM..."
echo "Browser will open at http://localhost:8501"
streamlit run app.py --server.port 8501
