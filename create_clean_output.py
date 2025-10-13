"""
Clean Output Generator
Converts DeepEval results into readable formats
"""

import json
import os
import re


def extract_metrics(result_dict):
    """Extract metrics from evaluation results"""
    metrics_str = str(result_dict)
    metrics = {}
    
    # Extract metric data using regex
    pattern = r"MetricData\(name='([^']+)'.*?score=([0-9.]+).*?success=(\w+).*?reason='([^']*(?:''[^']*)*?)'"
    matches = re.findall(pattern, metrics_str, re.DOTALL)
    
    for match in matches:
        name, score, success, reason = match
        metrics[name] = {
            "score": round(float(score), 4),
            "pass": success == 'True',
            "reason": reason[:300].replace("''", "'")  # First 300 chars, unescape quotes
        }
    
    return metrics


def process_result_file(result_json_path):
    """Process a single result JSON and create clean outputs"""
    with open(result_json_path) as f:
        data = json.load(f)
    
    base_name = os.path.basename(result_json_path).replace('_results.json', '')
    output_dir = os.path.dirname(result_json_path)
    
    # Extract metrics
    model_a_metrics = {}
    model_b_metrics = {}
    
    if "results" in data:
        results = data["results"]
        if "model_a_evaluation" in results:
            model_a_metrics = extract_metrics(results["model_a_evaluation"]["metrics"])
        if "model_b_evaluation" in results:
            model_b_metrics = extract_metrics(results["model_b_evaluation"]["metrics"])
    
    # Create metrics-only JSON
    metrics_only = {
        "test_name": data.get("file", base_name),
        "timestamp": data.get("timestamp", ""),
        "model_a_metrics": model_a_metrics,
        "model_b_metrics": model_b_metrics,
        "comparison": {}
    }
    
    # Compare scores
    for metric in model_a_metrics:
        if metric in model_b_metrics:
            a_score = model_a_metrics[metric]["score"]
            b_score = model_b_metrics[metric]["score"]
            if a_score > b_score:
                metrics_only["comparison"][metric] = "Model A wins"
            elif b_score > a_score:
                metrics_only["comparison"][metric] = "Model B wins"
            else:
                metrics_only["comparison"][metric] = "Tie"
    
    # Save metrics-only
    metrics_path = os.path.join(output_dir, f"{base_name}_metrics_only.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics_only, f, indent=2)
    print(f"✓ Created: {metrics_path}")
    
    # Create summary markdown
    md_lines = [
        f"# Evaluation Summary: {base_name}",
        f"\n**Timestamp**: {data.get('timestamp', 'N/A')}",
        f"\n**Mode**: {data.get('mode', 'N/A').upper()}",
        "\n## Model A (Base) Metrics\n"
    ]
    
    for metric, values in model_a_metrics.items():
        status = "✅" if values["pass"] else "❌"
        md_lines.append(f"- {status} **{metric}**: {values['score']:.4f}")
    
    md_lines.append("\n## Model B (Finetuned) Metrics\n")
    for metric, values in model_b_metrics.items():
        status = "✅" if values["pass"] else "❌"
        md_lines.append(f"- {status} **{metric}**: {values['score']:.4f}")
    
    md_lines.append("\n## Comparison\n")
    for metric, winner in metrics_only["comparison"].items():
        md_lines.append(f"- **{metric}**: {winner}")
    
    # Save summary
    summary_path = os.path.join(output_dir, f"{base_name}_summary.md")
    with open(summary_path, 'w') as f:
        f.write('\n'.join(md_lines))
    print(f"✓ Created: {summary_path}")


def main():
    """Process all results in evaluation_result/ folder"""
    result_dir = "evaluation_result"
    
    if not os.path.exists(result_dir):
        print(f"❌ No {result_dir} directory found")
        return
    
    result_files = [f for f in os.listdir(result_dir) if f.endswith('_results.json')]
    
    if not result_files:
        print(f"❌ No result files found in {result_dir}/")
        return
    
    print(f"\n📊 Processing {len(result_files)} result file(s)...\n")
    
    for result_file in result_files:
        result_path = os.path.join(result_dir, result_file)
        try:
            process_result_file(result_path)
        except Exception as e:
            print(f"❌ Error processing {result_file}: {e}")
    
    print("\n✅ Clean outputs generated\n")


if __name__ == "__main__":
    main()
