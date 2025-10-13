"""
Excel Format Converter
Converts user's custom Excel format to the format expected by excel_loader.py

Input columns:
- test_id
- conversation_history (text format: "assistant: ... user: ... assistant: ...")
- query
- response_A
- response_B

Output columns:
- Initial Conversation (JSON format)
- User Query
- Model A Response
- Model B Response
"""

import pandas as pd
import json
import re
from typing import List, Dict


def parse_conversation_history_to_json(conversation_text: str) -> str:
    """
    Convert conversation history from text format to JSON format
    
    Args:
        conversation_text: Text in format like "assistant: hello user: hi assistant: how are you"
        
    Returns:
        JSON string: [{"role": "assistant", "content": "hello"}, {"role": "user", "content": "hi"}, ...]
    """
    if pd.isna(conversation_text) or not str(conversation_text).strip():
        return "[]"
    
    conversation_text = str(conversation_text).strip()
    
    # Try to parse different text formats
    turns = []
    
    # Pattern 1: "assistant: content user: content" or "assistant content user content"
    # Split by role markers
    pattern = r'(assistant|user)\s*:?\s*'
    parts = re.split(pattern, conversation_text, flags=re.IGNORECASE)
    
    # Remove empty strings and process pairs
    parts = [p.strip() for p in parts if p.strip()]
    
    i = 0
    while i < len(parts) - 1:
        role = parts[i].lower()
        if role in ['assistant', 'user']:
            content = parts[i + 1].strip()
            # Remove trailing role markers from content
            content = re.sub(r'\s*(assistant|user)\s*:?\s*$', '', content, flags=re.IGNORECASE).strip()
            
            if content:
                turns.append({
                    "role": role,
                    "content": content
                })
            i += 2
        else:
            i += 1
    
    return json.dumps(turns, ensure_ascii=False)


def convert_excel_format(input_path: str, output_path: str):
    """
    Convert Excel from user's format to required format
    
    Args:
        input_path: Path to input Excel file
        output_path: Path to save converted Excel file
    """
    print(f"Reading input Excel from: {input_path}")
    df = pd.read_excel(input_path)
    
    print(f"Input columns: {list(df.columns)}")
    print(f"Number of rows: {len(df)}")
    
    # Create new DataFrame with required columns
    converted_data = []
    
    for idx, row in df.iterrows():
        # Convert conversation_history to JSON format
        conversation_json = parse_conversation_history_to_json(
            row.get('conversation_history', '')
        )
        
        converted_row = {
            'Initial Conversation': conversation_json,
            'User Query': str(row.get('query', '')).strip() if pd.notna(row.get('query')) else '',
            'Model A Response': str(row.get('response_A', '')).strip() if pd.notna(row.get('response_A')) else '',
            'Model B Response': str(row.get('response_B', '')).strip() if pd.notna(row.get('response_B')) else '',
            'Chatbot Role': 'helpful AI assistant',  # Default role, can be customized
        }
        
        # Optionally include test_id as metadata
        if 'test_id' in row and pd.notna(row['test_id']):
            converted_row['Test ID'] = row['test_id']
        
        # Check if user's input has a chatbot_role column
        if 'chatbot_role' in row and pd.notna(row['chatbot_role']):
            converted_row['Chatbot Role'] = str(row['chatbot_role']).strip()
        
        converted_data.append(converted_row)
    
    # Create new DataFrame
    converted_df = pd.DataFrame(converted_data)
    
    # Reorder columns (Test ID first if it exists, then the required columns)
    column_order = []
    if 'Test ID' in converted_df.columns:
        column_order.append('Test ID')
    column_order.extend(['Initial Conversation', 'User Query', 'Model A Response', 'Model B Response', 'Chatbot Role'])
    
    converted_df = converted_df[column_order]
    
    # Save to Excel
    converted_df.to_excel(output_path, index=False)
    
    print(f"\n✅ Conversion complete!")
    print(f"Output saved to: {output_path}")
    print(f"Output columns: {list(converted_df.columns)}")
    print(f"\nSample conversion (first row):")
    print(f"- Initial Conversation: {converted_df.iloc[0]['Initial Conversation'][:100]}...")
    print(f"- User Query: {converted_df.iloc[0]['User Query'][:100]}...")
    
    # Show a preview of the JSON conversion
    if len(converted_df) > 0:
        print(f"\n📋 Preview of conversation JSON format:")
        try:
            sample_json = json.loads(converted_df.iloc[0]['Initial Conversation'])
            print(json.dumps(sample_json, indent=2, ensure_ascii=False))
        except:
            print("(No conversation history in first row)")


def main():
    """Main conversion function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python convert_excel_format.py <input_file> [output_file]")
        print("\nExample:")
        print("  python convert_excel_format.py input/my_data.xlsx input/converted_data.xlsx")
        print("\nOr simply:")
        print("  python convert_excel_format.py input/my_data.xlsx")
        print("  (will create input/my_data_converted.xlsx)")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Generate output path if not provided
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        # Auto-generate output path
        if input_path.endswith('.xlsx'):
            output_path = input_path.replace('.xlsx', '_converted.xlsx')
        else:
            output_path = input_path + '_converted.xlsx'
    
    convert_excel_format(input_path, output_path)


if __name__ == "__main__":
    main()

