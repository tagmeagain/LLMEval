"""
Clean Output Generator  
Converts DeepEval results into readable formats
Handles both single and multiple conversations
"""

import json
import os
import re


def extract_metrics(result_dict):
    """Extract ALL metrics from evaluation results - FIXED VERSION"""
    metrics_str = str(result_dict)
    metrics = {}
    
    # Split by MetricData to find all metrics
    metric_sections = metrics_str.split("MetricData(")
    
    for section in metric_sections[1:]:  # Skip first empty part
        try:
            # Extract name
            name_match = re.search(r"name='([^']+)'", section)
            if not name_match:
                continue
            name = name_match.group(1)
            
            # Extract score
            score_match = re.search(r"score=([0-9.]+)", section)
            if not score_match:
                continue
            score = float(score_match.group(1))
            
            # Extract success/pass
            success_match = re.search(r"success=(\w+)", section)
            if not success_match:
                continue
            success = success_match.group(1) == 'True'
            
            # Extract threshold
            threshold_match = re.search(r"threshold=([0-9.]+)", section)
            threshold = float(threshold_match.group(1)) if threshold_match else 0.5
            
            # Extract reason (first 300 chars)
            reason_match = re.search(r"reason='([^']*(?:''[^']*)*?)'", section, re.DOTALL)
            reason = reason_match.group(1)[:300].replace("''", "'") if reason_match else ""
            
            metrics[name] = {
                "score": round(score, 4),
                "pass": success,
                "threshold": threshold,
                "reason": reason
            }
        except Exception as e:
            continue  # Skip malformed metrics
    
    return metrics


def process_result_file(result_json_path):
    """Process a single result JSON and create clean outputs"""
    with open(result_json_path) as f:
        data = json.load(f)
    
    base_name = os.path.basename(result_json_path).replace('_results.json', '')
    output_dir = os.path.dirname(result_json_path)
    
    # Check if this is multi-conversation format
    if "conversations" in data and isinstance(data["conversations"], list):
        # Multi-conversation format
        process_multi_conversation_results(data, base_name, output_dir)
    else:
        # Single conversation format (legacy)
        process_single_conversation_results(data, base_name, output_dir)


def process_multi_conversation_results(data, base_name, output_dir):
    """Process results with multiple conversations"""
    
    # Aggregate metrics across all conversations
    all_model_a_metrics = {}
    all_model_b_metrics = {}
    
    for idx, conv in enumerate(data["conversations"], 1):
        conv_name = f"Conversation {idx}"
        
        # Extract metrics for Model A
        if "model_a_evaluation" in conv:
            model_a_metrics = extract_metrics(conv["model_a_evaluation"]["metrics"])
            all_model_a_metrics[conv_name] = model_a_metrics
            print(f"  Conv {idx} Model A: {len(model_a_metrics)} metrics extracted")
        
        # Extract metrics for Model B
        if "model_b_evaluation" in conv:
            model_b_metrics = extract_metrics(conv["model_b_evaluation"]["metrics"])
            all_model_b_metrics[conv_name] = model_b_metrics
            print(f"  Conv {idx} Model B: {len(model_b_metrics)} metrics extracted")
    
    # Create metrics-only JSON
    metrics_only = {
        "test_name": data.get("file", base_name),
        "timestamp": data.get("timestamp", ""),
        "mode": data.get("mode", ""),
        "total_conversations": data.get("total_conversations", 0),
        "conversations": []
    }
    
    # Add each conversation's metrics
    for idx in range(1, data.get("total_conversations", 0) + 1):
        conv_name = f"Conversation {idx}"
        conv_metrics = {
            "conversation": conv_name,
            "model_a_metrics": all_model_a_metrics.get(conv_name, {}),
            "model_b_metrics": all_model_b_metrics.get(conv_name, {}),
            "comparison": {}
        }
        
        # Compare scores
        for metric in conv_metrics["model_a_metrics"]:
            if metric in conv_metrics["model_b_metrics"]:
                a_score = conv_metrics["model_a_metrics"][metric]["score"]
                b_score = conv_metrics["model_b_metrics"][metric]["score"]
                if a_score > b_score:
                    conv_metrics["comparison"][metric] = "Model A scores higher"
                elif b_score > a_score:
                    conv_metrics["comparison"][metric] = "Model B scores higher"
                else:
                    conv_metrics["comparison"][metric] = "Equivalent performance"
        
        metrics_only["conversations"].append(conv_metrics)
    
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
        f"\n**Total Conversations**: {data.get('total_conversations', 0)}",
    ]
    
    for idx, conv_metrics in enumerate(metrics_only["conversations"], 1):
        md_lines.append(f"\n## Conversation {idx}\n")
        
        md_lines.append("### Model A (Base) Metrics\n")
        for metric, values in sorted(conv_metrics["model_a_metrics"].items()):
            status = "✅" if values["pass"] else "❌"
            md_lines.append(f"- {status} **{metric}**: {values['score']:.4f}")
        
        md_lines.append("\n### Model B (Finetuned) Metrics\n")
        for metric, values in sorted(conv_metrics["model_b_metrics"].items()):
            status = "✅" if values["pass"] else "❌"
            md_lines.append(f"- {status} **{metric}**: {values['score']:.4f}")
        
        if conv_metrics["comparison"]:
            md_lines.append("\n### Comparative Performance\n")
            for metric, comparison in sorted(conv_metrics["comparison"].items()):
                md_lines.append(f"- **{metric}**: {comparison}")
    
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
            print(f"Processing: {result_file}")
            process_result_file(result_path)
            print()
        except Exception as e:
            print(f"❌ Error processing {result_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print("✅ Clean outputs generated\n")


if __name__ == "__main__":
    main()
