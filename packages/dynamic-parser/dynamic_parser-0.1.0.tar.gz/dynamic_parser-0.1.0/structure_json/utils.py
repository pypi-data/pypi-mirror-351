import json
import re
from .prompts import EXTRACT_AND_FIX_JSON_PROMPT
def _extract_json_string(llm_response):
    start_idx = llm_response.find('{')
    if start_idx == -1:
        return None

    end_idx = llm_response.rfind('}')
    if end_idx == -1 or end_idx < len(llm_response.strip()) - 1:
        end_idx = len(llm_response)

    json_string = llm_response[start_idx:end_idx].strip()
    return json_string



def extract_and_fix_json(llm_response):

    json_string = _extract_json_string(llm_response)
    if json_string is None:
        return  None, "No valid JSON found in the response."

    def safe_json_parse(json_string):
        try:
            return json.loads(json_string), None
        except json.JSONDecodeError as e:
            return None, str(e)

    result, error = safe_json_parse(json_string)
    if result:
        return result, None

    def auto_fix_json(json_string):
        json_string = re.sub(r',\s*([}\]])', r'\1', json_string)  # Remove commas before braces/brackets
        json_string = re.sub(r',\s*$', '', json_string.strip())  # Remove trailing commas

        # Fix unbalanced braces
        open_braces = json_string.count('{')
        close_braces = json_string.count('}')
        if open_braces > close_braces:
            json_string += '}' * (open_braces - close_braces)


        try:
            return json.loads(json_string), None
        except json.JSONDecodeError as e:
            return None, str(e)

    result, error = auto_fix_json(json_string)
    if result:
        return result, None

    # Step 5: Log and return error if all attempts fail
    return None, f"Failed to parse JSON after auto-fixing: {error}"


def ask_llm_to_fix_json(llm, json_string):
    prompt = EXTRACT_AND_FIX_JSON_PROMPT.format(input=json_string)
    fixed_json = llm.invoke(prompt)
    return fixed_json

def robust_json_parser(llm_response, llm=None):
    parsed_data, error = extract_and_fix_json(llm_response)
    if parsed_data:
        return parsed_data, None

    if llm is not None:
        json_part = _extract_json_string(llm_response)
        fixed_response = ask_llm_to_fix_json(llm, json_part)
        # Attempt parsing again
        parsed_data, error = extract_and_fix_json(fixed_response.content)
        if parsed_data:
            return parsed_data, None

    # Step 3: If all else fails, return error
    return None, f"Failed to parse JSON: {error}"