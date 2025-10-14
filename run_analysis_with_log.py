#!/usr/bin/env python3
"""
Wrapper script to run analysis with logging to file
Captures all output to timestamped log file
"""

import sys
import os
from datetime import datetime
import subprocess

def main():
    # Create logs directory
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"analysis_{timestamp}.log")
    
    # Get command line arguments (everything after this script name)
    analysis_args = sys.argv[1:]
    
    if not analysis_args:
        print("❌ Error: Please provide arguments for analysis.py")
        print("\nUsage:")
        print("  python run_analysis_with_log.py evaluation_result/test_results.json")
        print("  python run_analysis_with_log.py evaluation_result/test_results.json custom_output")
        print("\nAll output will be saved to logs/analysis_TIMESTAMP.log")
        sys.exit(1)
    
    # Build the command
    cmd = [sys.executable, "analysis.py"] + analysis_args
    
    print(f"📝 Starting analysis...")
    print(f"📁 Log file: {log_file}")
    print(f"🔄 Running: {' '.join(cmd)}")
    print(f"\n{'='*80}")
    print("OUTPUT:")
    print(f"{'='*80}\n")
    
    # Run analysis and capture output
    try:
        with open(log_file, 'w', encoding='utf-8') as log_f:
            # Write header to log
            log_f.write(f"{'='*80}\n")
            log_f.write(f"DeepEval Analysis Log\n")
            log_f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"Command: {' '.join(cmd)}\n")
            log_f.write(f"{'='*80}\n\n")
            log_f.flush()
            
            # Run the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output to both console and file
            for line in process.stdout:
                # Print to console
                print(line, end='')
                # Write to log file
                log_f.write(line)
                log_f.flush()
            
            # Wait for process to complete
            return_code = process.wait()
            
            # Write footer
            log_f.write(f"\n{'='*80}\n")
            log_f.write(f"Analysis completed with exit code: {return_code}\n")
            log_f.write(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"{'='*80}\n")
        
        print(f"\n{'='*80}")
        print(f"✅ Analysis complete!")
        print(f"📁 Full log saved to: {log_file}")
        print(f"{'='*80}\n")
        
        sys.exit(return_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        with open(log_file, 'a', encoding='utf-8') as log_f:
            log_f.write("\n\n⚠️  Analysis interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        with open(log_file, 'a', encoding='utf-8') as log_f:
            log_f.write(f"\n\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

