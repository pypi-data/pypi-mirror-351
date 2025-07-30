EXTRACT_AND_FIX_JSON_PROMPT  = """
The input contains a mix of text and JSON data. Your task is to:

Identify the JSON data by locating the first opening brace {{ and the corresponding last closing brace }}.
Extract the JSON substring from the input.
Validate and fix the JSON data to ensure it conforms to standard JSON formatting, addressing common issues like:
Missing or extra commas.
Unbalanced braces {{}} or brackets [].
Trailing commas before closing braces/brackets.
Any invalid characters within the JSON structure.
Output only the corrected JSON, without any of the surrounding text.
If the input does not contain valid JSON, respond with an error message:
"Error: Unable to extract valid JSON from the input."

Examples:

Input 1:
Here is some extra text before the JSON:
{{
"name": "Alice",
"age": 25,
"is_student": false
Some extra text after the JSON.

Output 1:
{{
"name": "Alice",
"age": 25,
"is_student": false
}}

Input 2:
Random text: Start of message.
{{
"name": "Bob",
"hobbies": ["reading", "cycling",
"profession": "engineer"
Random notes here.

Output 2:
{{
"name": "Bob",
"hobbies": ["reading", "cycling"],
"profession": "engineer"
}}

Input 3:
The data is corrupted. No JSON here.

Output 3:
"Error: Unable to extract valid JSON from the input."

# Input:

{input}


# Note:
  I dont need code implementation, just give me json data. You must produce only valid JSON. Do not include any additional text, explanations, or comments.
  Do not prefix the JSON with any text. Do not suffix the JSON with any text.
  Simply provide the JSON object.
    """
