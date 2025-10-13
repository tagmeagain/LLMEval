#!/bin/bash

# Example: How to convert your Excel file format
# 
# This script demonstrates how to convert an Excel file with custom columns
# to the format required by the DeepEval testing framework

echo "==================================================="
echo "Excel Format Conversion Example"
echo "==================================================="
echo ""

# Example 1: Basic conversion (auto-generate output filename)
echo "Example 1: Basic conversion"
echo "Command: python convert_excel_format.py input/test_multiple_conversations.xlsx"
echo ""

# Example 2: Specify output filename
echo "Example 2: Specify output filename"
echo "Command: python convert_excel_format.py input/my_data.xlsx input/my_data_converted.xlsx"
echo ""

# Example 3: Full workflow
echo "Example 3: Full workflow (convert + evaluate)"
echo "Commands:"
echo "  1. python convert_excel_format.py input/my_data.xlsx"
echo "  2. python evaluate.py --input-file input/my_data_converted.xlsx"
echo ""

echo "==================================================="
echo "Ready to convert? Run one of the commands above!"
echo "==================================================="

