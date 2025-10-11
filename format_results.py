"""
Result Formatter - Creates Clean, Human-Readable Outputs
Processes evaluation results and creates formatted JSON files

Usage:
    Automatically called by evaluate.py
    Or run manually: python3 format_results.py evaluation_result/file_results.json
"""

import json
import os
from typing import Dict, Any
from datetime import datetime


def format_metrics_only(evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only metrics in clean format
    
    Returns:
        {
            "test_name": "...",
            "timestamp": "...",
            "model_a_metrics": {
                "Coherence": {"score": 0.93, "pass": true, "reason": "..."},
                ...
            },
            "model_b_metrics": {...},
            "comparison": {
                "winner": "Model A" or "Model B" or "Tie",
                "improvements": {...}
            }
        }
    """
    result = {
        "test_name": evaluation_data.get("file", "Unknown"),
        "timestamp": evaluation_data.get("timestamp", datetime.now().isoformat()),
        "mode": evaluation_data.get("mode", "unknown"),
        "model_a_metrics": {},
        "model_b_metrics": {},
        "comparison": {}
    }
    
    # Extract Model A metrics
    if "evaluation" in evaluation_data and "model_a_evaluation" in evaluation_data["evaluation"]:
        model_a_eval = evaluation_data["evaluation"]["model_a_evaluation"]
        if "metrics" in model_a_eval:
            # Metrics is a list from DeepEval, extract the data
            for metric_result in model_a_eval["metrics"]:
                if hasattr(metric_result, 'name'):
                    metric_name = metric_result.name
                    result["model_a_metrics"][metric_name] = {
                        "score": round(metric_result.score, 4) if hasattr(metric_result, 'score') else None,
                        "pass": metric_result.success if hasattr(metric_result, 'success') else None,
                        "reason": metric_result.reason if hasattr(metric_result, 'reason') else None
                    }
    
    # Extract Model B metrics
    if "evaluation" in evaluation_data and "model_b_evaluation" in evaluation_data["evaluation"]:
        model_b_eval = evaluation_data["evaluation"]["model_b_evaluation"]
        if "metrics" in model_b_eval:
            for metric_result in model_b_eval["metrics"]:
                if hasattr(metric_result, 'name'):
                    metric_name = metric_result.name
                    result["model_b_metrics"][metric_name] = {
                        "score": round(metric_result.score, 4) if hasattr(metric_result, 'score') else None,
                        "pass": metric_result.success if hasattr(metric_result, 'success') else None,
                        "reason": metric_result.reason if hasattr(metric_result, 'reason') else None
                    }
    
    # Compare scores
    if result["model_a_metrics"] and result["model_b_metrics"]:
        comparison = {
            "average_score_model_a": 0.0,
            "average_score_model_b": 0.0,
            "winner": "Tie",
            "improvements": {},
            "metric_comparison": {}
        }
        
        a_scores = []
        b_scores = []
        
        for metric_name in result["model_a_metrics"].keys():
            a_score = result["model_a_metrics"][metric_name]["score"]
            b_score = result["model_b_metrics"].get(metric_name, {}).get("score", 0)
            
            if a_score is not None:
                a_scores.append(a_score)
            if b_score is not None:
                b_scores.append(b_score)
            
            # Calculate difference
            if a_score is not None and b_score is not None:
                diff = b_score - a_score
                comparison["metric_comparison"][metric_name] = {
                    "model_a": a_score,
                    "model_b": b_score,
                    "difference": round(diff, 4),
                    "improvement_percentage": round((diff / a_score * 100) if a_score > 0 else 0, 2)
                }
        
        # Calculate averages
        if a_scores:
            comparison["average_score_model_a"] = round(sum(a_scores) / len(a_scores), 4)
        if b_scores:
            comparison["average_score_model_b"] = round(sum(b_scores) / len(b_scores), 4)
        
        # Determine winner
        if comparison["average_score_model_b"] > comparison["average_score_model_a"]:
            comparison["winner"] = "Model B (Finetuned)"
        elif comparison["average_score_model_a"] > comparison["average_score_model_b"]:
            comparison["winner"] = "Model A (Base)"
        else:
            comparison["winner"] = "Tie"
        
        result["comparison"] = comparison
    
    return result


def format_test_case_flow(evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format test case showing input → processing → output flow
    
    Returns:
        {
            "input": {
                "system_prompt": "...",
                "initial_conversation": [...],
                "user_queries": [...]
            },
            "processing": {
                "mode": "generate" or "pre_recorded",
                "models_used": {...}
            },
            "output": {
                "model_a_conversation": [...],
                "model_b_conversation": [...]
            },
            "evaluation_summary": {...}
        }
    """
    result = {
        "test_name": evaluation_data.get("file", "Unknown"),
        "timestamp": evaluation_data.get("timestamp", datetime.now().isoformat()),
        "input": {},
        "processing": {},
        "output": {},
        "evaluation_summary": {}
    }
    
    # Input section
    result["input"] = {
        "system_prompt": evaluation_data.get("system_prompt", None),
        "initial_conversation": evaluation_data.get("initial_conversation", []),
        "user_queries": evaluation_data.get("user_queries", []),
        "scenario": evaluation_data.get("scenario", None),
        "expected_outcome": evaluation_data.get("expected_outcome", None),
        "chatbot_role": evaluation_data.get("chatbot_role", None)
    }
    
    # Processing section
    result["processing"] = {
        "mode": evaluation_data.get("mode", "unknown"),
        "description": "Generated responses on-the-fly" if evaluation_data.get("mode") == "generated" else "Used pre-recorded responses from Excel"
    }
    
    # Output section - conversations
    if "base_model" in evaluation_data:
        result["output"]["model_a_conversation"] = evaluation_data["base_model"].get("conversation", [])
    if "finetuned_model" in evaluation_data:
        result["output"]["model_b_conversation"] = evaluation_data["finetuned_model"].get("conversation", [])
    
    # Evaluation summary - just scores
    result["evaluation_summary"] = {
        "total_metrics": 7,
        "all_passed": True,
        "model_a_scores": {},
        "model_b_scores": {}
    }
    
    # Extract scores
    if "evaluation" in evaluation_data:
        if "model_a_evaluation" in evaluation_data["evaluation"]:
            model_a_eval = evaluation_data["evaluation"]["model_a_evaluation"]
            if "metrics" in model_a_eval:
                for metric in model_a_eval["metrics"]:
                    if hasattr(metric, 'name') and hasattr(metric, 'score'):
                        result["evaluation_summary"]["model_a_scores"][metric.name] = round(metric.score, 4)
                        if hasattr(metric, 'success') and not metric.success:
                            result["evaluation_summary"]["all_passed"] = False
        
        if "model_b_evaluation" in evaluation_data["evaluation"]:
            model_b_eval = evaluation_data["evaluation"]["model_b_evaluation"]
            if "metrics" in model_b_eval:
                for metric in model_b_eval["metrics"]:
                    if hasattr(metric, 'name') and hasattr(metric, 'score'):
                        result["evaluation_summary"]["model_b_scores"][metric.name] = round(metric.score, 4)
    
    return result


def create_readable_summary(evaluation_data: Dict[str, Any]) -> str:
    """
    Create human-readable text summary
    
    Returns markdown-formatted summary
    """
    summary = []
    summary.append("# Evaluation Summary\n")
    summary.append(f"**Test**: {evaluation_data.get('file', 'Unknown')}")
    summary.append(f"**Timestamp**: {evaluation_data.get('timestamp', 'Unknown')}")
    summary.append(f"**Mode**: {evaluation_data.get('mode', 'Unknown').upper()}\n")
    
    # Input section
    summary.append("## Input\n")
    summary.append(f"**System Prompt**: {len(evaluation_data.get('system_prompt', ''))} characters")
    
    user_queries = evaluation_data.get('user_queries', [])
    summary.append(f"**User Queries**: {len(user_queries)}")
    for i, query in enumerate(user_queries, 1):
        summary.append(f"  {i}. {query}")
    summary.append("")
    
    # Evaluation results
    summary.append("## Evaluation Results\n")
    
    metrics_only = format_metrics_only(evaluation_data)
    
    if metrics_only.get("model_a_metrics"):
        summary.append("### Model A (Base)\n")
        for metric_name, data in metrics_only["model_a_metrics"].items():
            score = data.get("score", 0)
            emoji = "✅" if data.get("pass") else "❌"
            summary.append(f"{emoji} **{metric_name}**: {score:.2f}")
        summary.append("")
    
    if metrics_only.get("model_b_metrics"):
        summary.append("### Model B (Finetuned)\n")
        for metric_name, data in metrics_only["model_b_metrics"].items():
            score = data.get("score", 0)
            emoji = "✅" if data.get("pass") else "❌"
            summary.append(f"{emoji} **{metric_name}**: {score:.2f}")
        summary.append("")
    
    # Comparison
    if metrics_only.get("comparison"):
        comp = metrics_only["comparison"]
        summary.append("## Comparison\n")
        summary.append(f"**Winner**: {comp.get('winner', 'Unknown')}")
        summary.append(f"**Average Score (Model A)**: {comp.get('average_score_model_a', 0):.4f}")
        summary.append(f"**Average Score (Model B)**: {comp.get('average_score_model_b', 0):.4f}")
    
    return "\n".join(summary)


def process_evaluation_result(result_path: str, output_dir: str = None):
    """
    Process evaluation result and create formatted outputs
    
    Args:
        result_path: Path to original results JSON
        output_dir: Directory to save formatted outputs (default: same as result_path)
    
    Creates:
        - {name}_metrics_only.json: Clean metrics scores
        - {name}_test_case_flow.json: Input → Output flow
        - {name}_summary.md: Human-readable summary
    """
    # Load original results
    with open(result_path, 'r') as f:
        data = json.load(f)
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(result_path)
    
    base_name = os.path.basename(result_path).replace('_results.json', '')
    
    print(f"\n📝 Creating formatted outputs for: {base_name}")
    
    # 1. Metrics only JSON
    metrics_only = format_metrics_only(data)
    metrics_path = os.path.join(output_dir, f"{base_name}_metrics_only.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics_only, f, indent=2)
    print(f"✓ Created: {metrics_path}")
    
    # 2. Test case flow JSON
    test_case_flow = format_test_case_flow(data)
    flow_path = os.path.join(output_dir, f"{base_name}_test_case_flow.json")
    with open(flow_path, 'w') as f:
        json.dump(test_case_flow, f, indent=2)
    print(f"✓ Created: {flow_path}")
    
    # 3. Human-readable summary
    summary_text = create_readable_summary(data)
    summary_path = os.path.join(output_dir, f"{base_name}_summary.md")
    with open(summary_path, 'w') as f:
        f.write(summary_text)
    print(f"✓ Created: {summary_path}")
    
    print()
    
    return {
        "metrics_only": metrics_path,
        "test_case_flow": flow_path,
        "summary": summary_path
    }


def format_all_results_in_directory(directory: str = "evaluation_result"):
    """
    Format all result files in a directory
    
    Args:
        directory: Directory containing *_results.json files
    """
    import glob
    
    result_files = glob.glob(os.path.join(directory, "*_results.json"))
    
    # Exclude already formatted files
    result_files = [f for f in result_files if not any(x in f for x in ["_metrics_only", "_test_case_flow"])]
    
    if not result_files:
        print(f"No result files found in {directory}/")
        return
    
    print(f"\n{'='*80}")
    print(f"FORMATTING {len(result_files)} RESULT FILE(S)")
    print(f"{'='*80}\n")
    
    for result_file in result_files:
        try:
            process_evaluation_result(result_file, directory)
        except Exception as e:
            print(f"❌ Error processing {result_file}: {e}\n")
    
    print(f"{'='*80}")
    print("✅ FORMATTING COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Format specific file
        result_path = sys.argv[1]
        if os.path.exists(result_path):
            process_evaluation_result(result_path)
        else:
            print(f"❌ File not found: {result_path}")
    else:
        # Format all files in evaluation_result/
        format_all_results_in_directory("evaluation_result")

