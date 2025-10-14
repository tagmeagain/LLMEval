#!/usr/bin/env python3
"""
Analysis & Visualization Tool for CXO Presentations
Generates charts, graphs, and detailed Excel reports from evaluation results
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from datetime import datetime
import os
import sys

# Set style for professional charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class DeepEvalAnalyzer:
    """Analyze DeepEval results and create CXO-ready visualizations"""
    
    def __init__(self, results_json_path: str, output_dir: str = "analysis_output"):
        """
        Initialize analyzer
        
        Args:
            results_json_path: Path to the *_results.json file
            output_dir: Directory for analysis outputs
        """
        self.results_path = results_json_path
        self.output_dir = output_dir
        self.charts_dir = os.path.join(output_dir, "charts")
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # Load results
        with open(results_json_path, 'r') as f:
            self.data = json.load(f)
        
        self.filename = Path(results_json_path).stem
        print(f"📊 Analyzing: {self.filename}")
        print(f"📁 Output directory: {self.output_dir}")
    
    def truncate_text(self, text: str, max_words: int = 100) -> str:
        """Truncate text to max_words"""
        if not text:
            return ""
        words = str(text).split()
        if len(words) <= max_words:
            return text
        return ' '.join(words[:max_words]) + "..."
    
    def extract_metrics_data(self):
        """Extract all metrics data into structured format"""
        conversations = self.data.get('conversations', [])
        
        all_data = []
        for conv in conversations:
            # Get test case data
            model_a = conv.get('model_a_evaluation', {})
            model_b = conv.get('model_b_evaluation', {})
            
            # Get test case details
            test_case_a = model_a.get('test_case', {})
            test_case_b = model_b.get('test_case', {})
            
            # Extract turns - handle both dict and string representations
            if isinstance(test_case_a, dict):
                turns_a = test_case_a.get('turns', [])
            else:
                turns_a = []
            
            if isinstance(test_case_b, dict):
                turns_b = test_case_b.get('turns', [])
            else:
                turns_b = []
            
            # Build conversation text
            initial_conversation = []
            user_query = ""
            model_a_response = ""
            model_b_response = ""
            
            # Extract from turns
            for i, turn in enumerate(turns_a):
                role = turn.get('role', '')
                content = turn.get('content', '')
                
                if i < len(turns_a) - 2:  # Initial conversation
                    initial_conversation.append(f"{role}: {content}")
                elif role == 'user':
                    user_query = content
                elif role == 'assistant':
                    model_a_response = content
            
            for i, turn in enumerate(turns_b):
                role = turn.get('role', '')
                content = turn.get('content', '')
                
                if role == 'assistant' and i == len(turns_b) - 1:
                    model_b_response = content
            
            # Fallback: If no turns found, try to get data from conversation directly
            if not turns_a:
                user_query = conv.get('user_query', '')
                model_a_response = conv.get('model_a_response', '')
                model_b_response = conv.get('model_b_response', '')
                initial_conv = conv.get('initial_conversation', '')
                if initial_conv and isinstance(initial_conv, str):
                    initial_conversation = [initial_conv]
            
            # Get chatbot role - handle both dict and string
            if isinstance(test_case_a, dict):
                chatbot_role = test_case_a.get('chatbot_role', '')
            else:
                chatbot_role = conv.get('chatbot_role', '')
            
            # Get metrics results
            metrics_a = model_a.get('metrics', {})
            metrics_b = model_b.get('metrics', {})
            
            # Extract metric scores and reasons
            row = {
                'Test Case': conv.get('test_case_name', ''),
                'Initial Conversation': '\n'.join(initial_conversation),
                'User Query': user_query,
                'Model A Response': model_a_response,
                'Model B Response': model_b_response,
                'Chatbot Role (100 words)': self.truncate_text(chatbot_role, 100),
            }
            
            # Add Model A metrics
            if hasattr(metrics_a, 'test_results'):
                for result in metrics_a.test_results:
                    for metric_data in result.metrics_data:
                        metric_name = metric_data.name
                        row[f'Model A - {metric_name} Score'] = round(metric_data.score, 3)
                        row[f'Model A - {metric_name} Pass'] = metric_data.success
                        row[f'Model A - {metric_name} Reason'] = metric_data.reason or 'N/A'
            
            # Add Model B metrics
            if hasattr(metrics_b, 'test_results'):
                for result in metrics_b.test_results:
                    for metric_data in result.metrics_data:
                        metric_name = metric_data.name
                        row[f'Model B - {metric_name} Score'] = round(metric_data.score, 3)
                        row[f'Model B - {metric_name} Pass'] = metric_data.success
                        row[f'Model B - {metric_name} Reason'] = metric_data.reason or 'N/A'
            
            all_data.append(row)
        
        return pd.DataFrame(all_data)
    
    def create_detailed_excel(self):
        """Create comprehensive Excel with all data and metrics"""
        print("\n📊 Creating detailed Excel report...")
        
        df = self.extract_metrics_data()
        
        # Create Excel with formatting
        excel_path = os.path.join(self.output_dir, f"{self.filename}_detailed_analysis.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Full Analysis', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Full Analysis']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                # Cap at 100 characters for readability
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 100)
        
        print(f"✅ Detailed Excel saved: {excel_path}")
        return excel_path
    
    def create_executive_summary_excel(self):
        """Create executive summary Excel with key metrics"""
        print("\n📊 Creating executive summary Excel...")
        
        conversations = self.data.get('conversations', [])
        
        summary_data = []
        metric_scores_a = []
        metric_scores_b = []
        metric_names = []
        
        for conv in conversations:
            model_a = conv.get('model_a_evaluation', {})
            model_b = conv.get('model_b_evaluation', {})
            
            metrics_a = model_a.get('metrics', {})
            metrics_b = model_b.get('metrics', {})
            
            row = {
                'Test Case': conv.get('test_case_name', ''),
            }
            
            # Extract scores
            if hasattr(metrics_a, 'test_results'):
                for result in metrics_a.test_results:
                    for metric_data in result.metrics_data:
                        metric_name = metric_data.name
                        if metric_name not in metric_names:
                            metric_names.append(metric_name)
                        
                        row[f'{metric_name} - Model A'] = round(metric_data.score, 3)
                        row[f'{metric_name} - Model B'] = 0  # Placeholder
            
            if hasattr(metrics_b, 'test_results'):
                for result in metrics_b.test_results:
                    for metric_data in result.metrics_data:
                        metric_name = metric_data.name
                        row[f'{metric_name} - Model B'] = round(metric_data.score, 3)
            
            summary_data.append(row)
        
        df_summary = pd.DataFrame(summary_data)
        
        # Calculate averages
        avg_data = {'Metric': [], 'Model A Avg': [], 'Model B Avg': [], 'Difference (B-A)': [], 'Better Performer': []}
        
        for metric in metric_names:
            col_a = f'{metric} - Model A'
            col_b = f'{metric} - Model B'
            
            if col_a in df_summary.columns and col_b in df_summary.columns:
                avg_a = df_summary[col_a].mean()
                avg_b = df_summary[col_b].mean()
                diff = avg_b - avg_a
                better_performer = 'Model B' if diff > 0 else 'Model A' if diff < 0 else 'Equivalent'
                
                avg_data['Metric'].append(metric)
                avg_data['Model A Avg'].append(round(avg_a, 3))
                avg_data['Model B Avg'].append(round(avg_b, 3))
                avg_data['Difference (B-A)'].append(round(diff, 3))
                avg_data['Better Performer'].append(better_performer)
        
        df_avg = pd.DataFrame(avg_data)
        
        # Save to Excel
        excel_path = os.path.join(self.output_dir, f"{self.filename}_executive_summary.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_avg.to_excel(writer, sheet_name='Metric Averages', index=False)
            df_summary.to_excel(writer, sheet_name='All Test Cases', index=False)
        
        print(f"✅ Executive summary saved: {excel_path}")
        return excel_path, df_avg
    
    def create_metric_comparison_chart(self, df_avg):
        """Create bar chart comparing Model A vs Model B across all metrics"""
        print("\n📈 Creating metric comparison chart...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(df_avg['Metric']))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, df_avg['Model A Avg'], width, label='Model A', 
                       color='#3498db', alpha=0.8)
        bars2 = ax.bar(x + width/2, df_avg['Model B Avg'], width, label='Model B', 
                       color='#2ecc71', alpha=0.8)
        
        ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Score', fontsize=12, fontweight='bold')
        ax.set_title('Model A vs Model B - Metric Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(df_avg['Metric'], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'metric_comparison.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {chart_path}")
        return chart_path
    
    def create_performance_pie_chart(self, df_avg):
        """Create pie chart showing comparative model performance across metrics"""
        print("\n📈 Creating performance distribution chart...")
        
        performance_counts = df_avg['Better Performer'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#2ecc71', '#3498db', '#95a5a6']
        explode = [0.05 if w == 'Model B' else 0 for w in performance_counts.index]
        
        wedges, texts, autotexts = ax.pie(
            performance_counts.values,
            labels=performance_counts.index,
            autopct='%1.1f%%',
            colors=colors[:len(performance_counts)],
            explode=explode,
            startangle=90,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        
        ax.set_title('Performance Distribution Across Metrics', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'performance_distribution.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {chart_path}")
        return chart_path
    
    def create_heatmap(self):
        """Create heatmap showing scores across all test cases and metrics"""
        print("\n📈 Creating metric heatmap...")
        
        df = self.extract_metrics_data()
        
        # Extract only score columns
        score_cols_a = [col for col in df.columns if 'Model A' in col and 'Score' in col]
        score_cols_b = [col for col in df.columns if 'Model B' in col and 'Score' in col]
        
        if not score_cols_a or not score_cols_b:
            print("⚠️  No score data found for heatmap")
            return None
        
        # Create separate heatmaps
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Model A heatmap
        data_a = df[score_cols_a].T
        data_a.columns = [f"TC{i+1}" for i in range(len(df))]
        data_a.index = [col.replace('Model A - ', '').replace(' Score', '') for col in score_cols_a]
        
        sns.heatmap(data_a, annot=True, fmt='.2f', cmap='RdYlGn', 
                   vmin=0, vmax=1, ax=ax1, cbar_kws={'label': 'Score'})
        ax1.set_title('Model A - Metric Scores Heatmap', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Test Cases', fontweight='bold')
        ax1.set_ylabel('Metrics', fontweight='bold')
        
        # Model B heatmap
        data_b = df[score_cols_b].T
        data_b.columns = [f"TC{i+1}" for i in range(len(df))]
        data_b.index = [col.replace('Model B - ', '').replace(' Score', '') for col in score_cols_b]
        
        sns.heatmap(data_b, annot=True, fmt='.2f', cmap='RdYlGn', 
                   vmin=0, vmax=1, ax=ax2, cbar_kws={'label': 'Score'})
        ax2.set_title('Model B - Metric Scores Heatmap', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Test Cases', fontweight='bold')
        ax2.set_ylabel('Metrics', fontweight='bold')
        
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'metrics_heatmap.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {chart_path}")
        return chart_path
    
    def create_improvement_chart(self, df_avg):
        """Create chart showing improvement of Model B over Model A"""
        print("\n📈 Creating improvement analysis chart...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Sort by difference
        df_sorted = df_avg.sort_values('Difference (B-A)')
        
        colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in df_sorted['Difference (B-A)']]
        
        bars = ax.barh(df_sorted['Metric'], df_sorted['Difference (B-A)'], color=colors, alpha=0.8)
        
        ax.set_xlabel('Score Difference (Model B - Model A)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Metrics', fontsize=12, fontweight='bold')
        ax.set_title('Model B Improvement Over Model A', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, df_sorted['Difference (B-A)'])):
            ax.text(val, bar.get_y() + bar.get_height()/2, 
                   f'{val:+.3f}',
                   ha='left' if val > 0 else 'right', 
                   va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'improvement_analysis.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Chart saved: {chart_path}")
        return chart_path
    
    def generate_insights_report(self, df_avg):
        """Generate text-based insights report for CXOs"""
        print("\n📝 Generating insights report...")
        
        report = []
        report.append("="*80)
        report.append("EXECUTIVE INSIGHTS REPORT")
        report.append("="*80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Source: {self.filename}")
        report.append("\n" + "="*80)
        
        # Overall performance
        report.append("\n📊 OVERALL PERFORMANCE")
        report.append("-"*80)
        
        total_metrics = len(df_avg)
        model_b_higher = len(df_avg[df_avg['Better Performer'] == 'Model B'])
        model_a_higher = len(df_avg[df_avg['Better Performer'] == 'Model A'])
        equivalent = len(df_avg[df_avg['Better Performer'] == 'Equivalent'])
        
        report.append(f"Total Metrics Evaluated: {total_metrics}")
        report.append(f"Model B Scores Higher: {model_b_higher} ({model_b_higher/total_metrics*100:.1f}%)")
        report.append(f"Model A Scores Higher: {model_a_higher} ({model_a_higher/total_metrics*100:.1f}%)")
        report.append(f"Equivalent Performance: {equivalent} ({equivalent/total_metrics*100:.1f}%)")
        
        # Best performing metrics
        report.append("\n🏆 TOP 3 IMPROVEMENTS (Model B over Model A)")
        report.append("-"*80)
        
        top_improvements = df_avg.nlargest(3, 'Difference (B-A)')
        for i, row in enumerate(top_improvements.itertuples(), 1):
            report.append(f"{i}. {row.Metric}")
            report.append(f"   Model A: {row._2:.3f} | Model B: {row._3:.3f} | Improvement: +{row._4:.3f}")
        
        # Areas needing attention
        report.append("\n⚠️  AREAS NEEDING ATTENTION")
        report.append("-"*80)
        
        bottom_improvements = df_avg.nsmallest(3, 'Difference (B-A)')
        for i, row in enumerate(bottom_improvements.itertuples(), 1):
            report.append(f"{i}. {row.Metric}")
            report.append(f"   Model A: {row._2:.3f} | Model B: {row._3:.3f} | Difference: {row._4:+.3f}")
        
        # Recommendations
        report.append("\n💡 KEY RECOMMENDATIONS")
        report.append("-"*80)
        
        if model_b_higher > model_a_higher:
            report.append("✅ Model B shows overall superior performance across most metrics")
            report.append("   → Recommended for production deployment")
        elif model_a_higher > model_b_higher:
            report.append("⚠️  Model A outperforms Model B in majority of metrics")
            report.append("   → Further finetuning of Model B recommended")
        else:
            report.append("⚖️  Models show comparable performance")
            report.append("   → Consider cost, latency, and specific use-case requirements")
        
        report.append("\n" + "="*80)
        
        # Save report
        report_text = '\n'.join(report)
        report_path = os.path.join(self.output_dir, f"{self.filename}_insights_report.txt")
        
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        print(report_text)
        print(f"\n✅ Insights report saved: {report_path}")
        
        return report_path
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("\n" + "="*80)
        print("🚀 STARTING COMPREHENSIVE ANALYSIS FOR CXO PRESENTATION")
        print("="*80)
        
        # Create detailed Excel
        detailed_excel = self.create_detailed_excel()
        
        # Create executive summary
        exec_excel, df_avg = self.create_executive_summary_excel()
        
        # Create visualizations
        metric_chart = self.create_metric_comparison_chart(df_avg)
        performance_chart = self.create_performance_pie_chart(df_avg)
        heatmap_chart = self.create_heatmap()
        improvement_chart = self.create_improvement_chart(df_avg)
        
        # Generate insights
        insights_report = self.generate_insights_report(df_avg)
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\n📁 All outputs saved in: {self.output_dir}/")
        print("\n📊 Excel Reports:")
        print(f"  - Detailed Analysis: {os.path.basename(detailed_excel)}")
        print(f"  - Executive Summary: {os.path.basename(exec_excel)}")
        print("\n📈 Charts:")
        print(f"  - {os.path.basename(metric_chart)}")
        print(f"  - {os.path.basename(performance_chart)}")
        if heatmap_chart:
            print(f"  - {os.path.basename(heatmap_chart)}")
        print(f"  - {os.path.basename(improvement_chart)}")
        print("\n📝 Reports:")
        print(f"  - {os.path.basename(insights_report)}")
        print("\n" + "="*80)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python analysis.py <path_to_results.json> [output_directory]")
        print("\nExample:")
        print("  python analysis.py evaluation_result/test_results.json")
        print("  python analysis.py evaluation_result/test_results.json custom_analysis")
        sys.exit(1)
    
    results_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_output"
    
    if not os.path.exists(results_path):
        print(f"❌ Error: File not found: {results_path}")
        sys.exit(1)
    
    analyzer = DeepEvalAnalyzer(results_path, output_dir)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()

