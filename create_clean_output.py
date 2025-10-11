"""
Clean Output Generator
Extracts evaluation data and creates clean, readable JSON files

Run after evaluation to generate formatted outputs
"""

import json
import os
import re
from datetime import datetime


def extract_metrics_from_string(metrics_str):
    """Extract metric scores from DeepEval string output"""
    metrics = {}
    
    # Pattern to match MetricData entries
    pattern = r"MetricData\(name='([^']+)'[^,]*,\s*threshold=[^,]*,\s*success=(\w+),\s*score=([^,]+),\s*reason='([^']*(?:''[^']*)*)',"
    
    matches = re.findall(pattern, metrics_str)
    
    for match in matches:
        metric_name = match[0]
        success = match[1] == 'True'
        score = float(match[2])
        reason = match[3].replace("''", "'")  # Unescape quotes
        
        metrics[metric_name] = {
            "score": round(score, 4),
            "pass": success,
            "reason": reason[:500] if len(reason) > 500 else reason  # Truncate long reasons
        }
    
    return metrics


def create_metrics_only_json(result_file):
    """Create clean metrics-only JSON"""
    with open(result_file) as f:
        data = json.load(f)
    
    # Extract metrics from both models
    model_a_metrics = {}
    model_b_metrics = {}
    
    if "evaluation" in data:
        if "model_a_evaluation" in data["evaluation"]:
            metrics_str = str(data["evaluation"]["model_a_evaluation"].get("metrics", ""))
            model_a_metrics = extract_metrics_from_string(metrics_str)
        
        if "model_b_evaluation" in data["evaluation"]:
            metrics_str = str(data["evaluation"]["model_b_evaluation"].get("metrics", ""))
            model_b_metrics = extract_metrics_from_string(metrics_str)
    
    # Create clean output
    output = {
        "test_name": data.get("file", "Unknown"),
        "timestamp": data.get("timestamp", datetime.now().isoformat()),
        "mode": data.get("mode", "unknown"),
        "model_a_metrics": model_a_metrics,
        "model_b_metrics": model_b_metrics
    }
    
    # Add comparison if both exist
    if model_a_metrics and model_b_metrics:
        a_avg = sum(m["score"] for m in model_a_metrics.values()) / len(model_a_metrics)
        b_avg = sum(m["score"] for m in model_b_metrics.values()) / len(model_b_metrics)
        
        output["comparison"] = {
            "model_a_average": round(a_avg, 4),
            "model_b_average": round(b_avg, 4),
            "winner": "Model B" if b_avg > a_avg else "Model A" if a_avg > b_avg else "Tie",
            "metric_comparison": {}
        }
        
        for metric_name in model_a_metrics.keys():
            if metric_name in model_b_metrics:
                diff = model_b_metrics[metric_name]["score"] - model_a_metrics[metric_name]["score"]
                output["comparison"]["metric_comparison"][metric_name] = {
                    "model_a": model_a_metrics[metric_name]["score"],
                    "model_b": model_b_metrics[metric_name]["score"],
                    "difference": round(diff, 4),
                    "improvement_pct": round((diff / model_a_metrics[metric_name]["score"] * 100) if model_a_metrics[metric_name]["score"] > 0 else 0, 2)
                }
    
    return output


def extract_conversation_from_string(conv_str):
    """Extract conversation turns from string"""
    turns = []
    
    # Pattern to match Turn objects
    pattern = r"Turn\(role='(user|assistant)', content=([\"'])(.+?)\2\)"
    
    matches = re.findall(pattern, conv_str, re.DOTALL)
    
    for match in matches:
        role = match[0]
        content = match[2].replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
        turns.append({
            "role": role,
            "content": content
        })
    
    return turns


def create_test_case_flow_json(result_file):
    """Create input → output flow JSON"""
    with open(result_file) as f:
        data = json.load(f)
    
    # Extract conversations
    model_a_conversation = []
    model_b_conversation = []
    
    if "evaluation" in data:
        if "model_a_evaluation" in data["evaluation"]:
            test_case_str = str(data["evaluation"]["model_a_evaluation"].get("test_case", ""))
            model_a_conversation = extract_conversation_from_string(test_case_str)
        
        if "model_b_evaluation" in data["evaluation"]:
            test_case_str = str(data["evaluation"]["model_b_evaluation"].get("test_case", ""))
            model_b_conversation = extract_conversation_from_string(test_case_str)
    
    # Create flow
    output = {
        "test_name": data.get("file", "Unknown"),
        "timestamp": data.get("timestamp", datetime.now().isoformat()),
        "input": {
            "system_prompt": data.get("system_prompt", "")[:200] + "..." if data.get("system_prompt") and len(data.get("system_prompt", "")) > 200 else data.get("system_prompt", ""),
            "user_queries": [
                turn["content"] for turn in model_a_conversation if turn["role"] == "user"
            ] if model_a_conversation else [],
            "scenario": data.get("scenario"),
            "chatbot_role": data.get("chatbot_role")
        },
        "output": {
            "model_a_conversation": model_a_conversation,
            "model_b_conversation": model_b_conversation
        },
        "processing": {
            "mode": data.get("mode", "unknown"),
            "description": "Generated responses on-the-fly" if data.get("mode") == "generated" else "Used pre-recorded responses"
        }
    }
    
    return output


def create_summary_markdown(result_file):
    """Create human-readable markdown summary"""
    with open(result_file) as f:
        data = json.load(f)
    
    metrics_only = create_metrics_only_json(result_file)
    
    lines = []
    lines.append(f"# Evaluation Summary\n")
    lines.append(f"**Test**: {data.get('file', 'Unknown')}")
    lines.append(f"**Mode**: {data.get('mode', 'unknown').upper()}")
    lines.append(f"**Timestamp**: {data.get('timestamp', 'Unknown')}\n")
    
    # Input section
    lines.append("## Input\n")
    user_queries = [turn["content"] for turn in metrics_only.get("output", {}).get("model_a_conversation", []) if turn.get("role") == "user"][:20]
    
    lines.append(f"**User Queries ({len(user_queries)} total)**:")
    for i, query in enumerate(user_queries, 1):
        lines.append(f"{i}. {query}")
    lines.append("")
    
    # Model A Results
    if metrics_only.get("model_a_metrics"):
        lines.append("## Model A (Base) - Evaluation Scores\n")
        for metric_name, metric_data in metrics_only["model_a_metrics"].items():
            emoji = "✅" if metric_data["pass"] else "❌"
            score = metric_data["score"]
            lines.append(f"{emoji} **{metric_name}**: `{score:.4f}`")
        
        # Average
        avg_score = sum(m["score"] for m in metrics_only["model_a_metrics"].values()) / len(metrics_only["model_a_metrics"])
        lines.append(f"\n**Average Score**: `{avg_score:.4f}`\n")
    
    # Model B Results
    if metrics_only.get("model_b_metrics"):
        lines.append("## Model B (Finetuned) - Evaluation Scores\n")
        for metric_name, metric_data in metrics_only["model_b_metrics"].items():
            emoji = "✅" if metric_data["pass"] else "❌"
            score = metric_data["score"]
            lines.append(f"{emoji} **{metric_name}**: `{score:.4f}`")
        
        # Average
        avg_score = sum(m["score"] for m in metrics_only["model_b_metrics"].values()) / len(metrics_only["model_b_metrics"])
        lines.append(f"\n**Average Score**: `{avg_score:.4f}`\n")
    
    # Comparison
    if "comparison" in metrics_only:
        comp = metrics_only["comparison"]
        lines.append("## Comparison\n")
        lines.append(f"**Winner**: {comp.get('winner', 'Unknown')}\n")
        
        lines.append("### Metric-by-Metric Comparison\n")
        if "metric_comparison" in comp:
            for metric, scores in comp["metric_comparison"].items():
                diff = scores["difference"]
                emoji = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
                lines.append(f"{emoji} **{metric}**: {scores['model_a']:.4f} → {scores['model_b']:.4f} ({diff:+.4f}, {scores['improvement_pct']:+.1f}%)")
    
    return "\n".join(lines)


def process_result_file(result_file):
    """Process a result file and create all formatted outputs"""
    base_name = os.path.basename(result_file).replace("_results.json", "")
    output_dir = os.path.dirname(result_file)
    
    print(f"\n📝 Formatting: {base_name}")
    
    # 1. Metrics only
    try:
        metrics_json = create_metrics_only_json(result_file)
        metrics_path = os.path.join(output_dir, f"{base_name}_metrics_only.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics_json, f, indent=2)
        print(f"   ✅ {base_name}_metrics_only.json")
    except Exception as e:
        print(f"   ❌ Error creating metrics JSON: {e}")
    
    # 2. Test case flow
    try:
        flow_json = create_test_case_flow_json(result_file)
        flow_path = os.path.join(output_dir, f"{base_name}_test_case_flow.json")
        with open(flow_path, "w") as f:
            json.dump(flow_json, f, indent=2)
        print(f"   ✅ {base_name}_test_case_flow.json")
    except Exception as e:
        print(f"   ❌ Error creating flow JSON: {e}")
    
    # 3. Summary markdown
    try:
        summary_md = create_summary_markdown(result_file)
        summary_path = os.path.join(output_dir, f"{base_name}_summary.md")
        with open(summary_path, "w") as f:
            f.write(summary_md)
        print(f"   ✅ {base_name}_summary.md")
    except Exception as e:
        print(f"   ❌ Error creating summary: {e}")


if __name__ == "__main__":
    import sys
    import glob
    
    if len(sys.argv) > 1:
        # Process specific file
        process_result_file(sys.argv[1])
    else:
        # Process all results in evaluation_result/
        result_files = glob.glob("evaluation_result/*_results.json")
        
        if not result_files:
            print("No result files found in evaluation_result/")
        else:
            print(f"\n{'='*80}")
            print(f"CREATING CLEAN OUTPUTS FOR {len(result_files)} FILE(S)")
            print(f"{'='*80}")
            
            for rf in result_files:
                process_result_file(rf)
            
            print(f"\n{'='*80}")
            print("✅ CLEAN OUTPUTS CREATED")
            print(f"{'='*80}\n")

