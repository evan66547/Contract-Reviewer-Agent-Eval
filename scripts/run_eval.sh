#!/bin/bash
# ---------------------------------------------------------
# Run Benchmark Evaluations for Contract-Reviewer-Agent v2
# ---------------------------------------------------------

set -e

echo "🚀 Contract Reviewer Agent Evaluation Test Runner"
echo "================================================="

# Check dependencies
if ! python3 -c "import jsonschema" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt --quiet
fi

# Run evaluation
python3 scripts/run_eval.py \
    --input_dir data/test_cases/ \
    --schema schemas/output_schema.json \
    "$@"

# Tip: Use --report to generate Markdown risk report
# Example: bash scripts/run_eval.sh --report
# Example: bash scripts/run_eval.sh --live --report --report_output results/my_report.md
