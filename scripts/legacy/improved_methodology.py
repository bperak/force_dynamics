"""
Improved Methodology for Translation and Evaluation
Addresses reviewer concerns about single prompt, blind evaluation, and FD framework.

Key improvements:
1. Separate translation and evaluation tasks
2. Blind evaluation (A/B/C labels)
3. Explicit FD framework definition
4. Clear evaluation criteria
"""

import json
import random
from typing import Dict, List, Tuple

# Load FD Framework Definition
FD_FRAMEWORK = """
Force Dynamics (Talmy, 2000) Framework:

CORE CONCEPTS:
- Agonist: The entity whose situation is being described (typically the subject)
- Antagonist: The opposing force entity (may be explicit or implicit)
- Force Relations: How Agonist and Antagonist interact

FORCE RELATION TYPES:
1. Causation: Antagonist causes Agonist to act/change state
   Example: "The wind broke the window" - wind (Antagonist) causes window (Agonist) to break

2. Permission/Letting: Antagonist allows Agonist to act
   Example: "She let him go" - she (Antagonist) allows him (Agonist) to go

3. Blocking/Prevention: Antagonist prevents Agonist from acting
   Example: "She was forbidden to help" - authority (Antagonist) prevents her (Agonist) from helping

4. Overcoming: Agonist overcomes opposing force
   Example: "He resisted the pressure" - he (Agonist) overcomes pressure (Antagonist)

EVALUATION CRITERIA FOR FD PRESERVATION:
1. Agonist/Antagonist Preservation: Same entities, same roles
2. Force Relation Type: Same relation type (causation, permission, etc.)
3. Force Strength: Similar force strength maintained
4. Linguistic Realization: Natural and idiomatic in target language
"""


def get_response(user_content: str, system_content: str, model: str = 'gpt-4o'):
    """
    Get response from OpenAI API.
    Compatible with both old (0.28) and new (>=1.0.0) OpenAI API versions.
    
    Note: Requires openai module to be imported and API key to be set.
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai module not found. Install with: pip install openai")
    
    # Try new API first (openai >= 1.0.0)
    try:
        client = openai.OpenAI()
        completion = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
        )
        return completion.choices[0].message.content
    except (AttributeError, TypeError):
        # Fall back to old API (openai < 1.0.0)
        try:
            completion = openai.ChatCompletion.create(
                model=model,
                temperature=0,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to call OpenAI API with both old and new methods: {e}")


def get_gpt_translation(source_language: str, target_language: str, 
                       original_text: str, model: str = 'gpt-4o') -> str:
    """
    PHASE 1: Get translation from GPT - SEPARATE TASK, no evaluation.
    
    This addresses Reviewer 1's concern about single prompt doing multiple tasks.
    Translation is now a separate, independent task.
    
    Args:
        source_language: Source language name
        target_language: Target language name
        original_text: Text to translate
        model: GPT model to use
        
    Returns:
        Translation string
    """
    system_prompt = f'''You are an expert translator specializing in {target_language}. 
Provide only the translation of the given sentence. Do not provide explanations, evaluations, or any other text.'''
    
    user_prompt = f'''Translate the following sentence from {source_language} to {target_language}:

{original_text}'''
    
    response = get_response(user_prompt, system_prompt, model)
    # Clean up response (remove any extra text)
    translation = response.strip()
    # Remove quotes if present
    if translation.startswith('"') and translation.endswith('"'):
        translation = translation[1:-1]
    if translation.startswith("'") and translation.endswith("'"):
        translation = translation[1:-1]
    
    return translation


def blind_evaluation(source_language: str, target_language: str, 
                    original_text: str,
                    translation_a: str, translation_b: str, translation_c: str,
                    model: str = 'gpt-4o') -> Dict:
    """
    PHASE 2: Blind evaluation of three translations.
    
    This addresses:
    - Reviewer 1: Blind evaluation (GPT doesn't know which is which)
    - Reviewer 1: Explicit FD framework provided
    - Reviewer 1: Clear evaluation criteria
    
    Args:
        source_language: Source language name
        target_language: Target language name
        original_text: Original English sentence
        translation_a: First translation (masked)
        translation_b: Second translation (masked)
        translation_c: Third translation (masked)
        model: GPT model to use
        
    Returns:
        Dictionary with evaluation results
    """
    system_prompt = '''You are an expert linguist specializing in cognitive semantics and translation evaluation. 
You are familiar with Leonard Talmy's (2000) Force Dynamics framework.'''
    
    user_prompt = f'''Evaluate three translations of the same English sentence, focusing EXCLUSIVELY on the verb phrase and its preservation of Force Dynamics relations.

{FD_FRAMEWORK}

EVALUATION CRITERIA:

1. Lexis (verb phrase only):
   - Word choice appropriateness
   - Idiomaticity in target language
   - Register appropriateness

2. Syntax (verb phrase only):
   - Grammatical accuracy
   - Structural correctness
   - Word order appropriateness

3. Semantics (verb phrase only):
   - Meaning preservation
   - Force Dynamics relations:
     * Identify Agonist and Antagonist (if present)
     * Identify force relation type (causation, permission, blocking, etc.)
     * Assess preservation of FD structure from source

Original sentence ({source_language}): {original_text}

Translation A ({target_language}): {translation_a}
Translation B ({target_language}): {translation_b}
Translation C ({target_language}): {translation_c}

For each translation (A, B, C):
1. Describe the verb phrase in terms of:
   - Lexis (word choice, idiomaticity)
   - Syntax (grammar, structure)
   - Semantics (meaning, Force Dynamics analysis)
2. Provide a numerical score (0.0 to 1.0) for verb phrase quality

Output format (JSON only, no other text):
{{
  "translation_A_description": "string",
  "translation_A_score": float,
  "translation_B_description": "string", 
  "translation_B_score": float,
  "translation_C_description": "string",
  "translation_C_score": float,
  "comparison": "string describing comparative analysis"
}}'''
    
    response = get_response(user_prompt, system_prompt, model)
    
    # Clean JSON response
    response = response.replace('```json', '').replace('```', '').strip()
    
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response: {response}")
        return {"error": "Failed to parse JSON", "raw_response": response}


def process_sentence_blind(source_language: str, target_language: str,
                          original_text: str,
                          translation_google: str,
                          translation_human: str,
                          model: str = 'gpt-4o') -> Dict:
    """
    Complete workflow: Translation + Blind Evaluation
    
    This implements the improved methodology:
    1. Get GPT translation (separate task)
    2. Blind evaluation of all three translations
    
    Args:
        source_language: Source language name
        target_language: Target language name
        original_text: Original English sentence
        translation_google: Google Translate output
        translation_human: Human reference translation
        model: GPT model to use
        
    Returns:
        Dictionary with:
        - translation_gpt: GPT's translation
        - blind_evaluation: Evaluation results with A/B/C labels
        - mapping: Which translation is which (for analysis)
    """
    # Phase 1: Get GPT translation (separate task)
    translation_gpt = get_gpt_translation(
        source_language, target_language, original_text, model
    )
    
    # Phase 2: Prepare for blind evaluation
    # Randomize order to avoid position bias
    translations = [
        ('GPT', translation_gpt),
        ('Google', translation_google),
        ('Human', translation_human)
    ]
    random.shuffle(translations)
    
    # Create blind labels
    blind_translations = {
        'A': translations[0][1],
        'B': translations[1][1],
        'C': translations[2][1]
    }
    
    # Track mapping for later analysis
    mapping = {
        'A': translations[0][0],  # 'GPT', 'Google', or 'Human'
        'B': translations[1][0],
        'C': translations[2][0]
    }
    
    # Phase 3: Blind evaluation
    evaluation = blind_evaluation(
        source_language, target_language, original_text,
        blind_translations['A'],
        blind_translations['B'],
        blind_translations['C'],
        model
    )
    
    # Combine results
    result = {
        'original_text': original_text,
        'translation_gpt': translation_gpt,
        'translation_google': translation_google,
        'translation_human': translation_human,
        'blind_evaluation': evaluation,
        'mapping': mapping  # For analysis: which is A, B, C
    }
    
    return result


def process_dataframe_blind(df, source_language: str, target_language: str,
                            original_col: str,
                            google_col: str,
                            human_col: str,
                            model: str = 'gpt-4o') -> List[Dict]:
    """
    Process entire dataframe with improved methodology.
    
    Args:
        df: DataFrame with translation data
        source_language: Source language name
        target_language: Target language name
        original_col: Column name for original text
        google_col: Column name for Google Translate
        human_col: Column name for Human reference
        model: GPT model to use
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    for index, row in df.iterrows():
        original_text = row[original_col]
        translation_google = row[google_col]
        translation_human = row[human_col]
        
        result = process_sentence_blind(
            source_language, target_language,
            original_text,
            translation_google,
            translation_human,
            model
        )
        
        results.append(result)
        
        print(f"Processed sentence {index + 1}/{len(df)}")
    
    return results


def analyze_blind_results(results: List[Dict]) -> Dict:
    """
    Analyze blind evaluation results.
    
    This helps identify:
    - How GPT rates its own translations vs others (now blind)
    - Patterns in evaluation
    - Bias detection
    
    Args:
        results: List of result dictionaries from process_dataframe_blind
        
    Returns:
        Analysis dictionary
    """
    analysis = {
        'gpt_self_scores': [],
        'gpt_google_scores': [],
        'gpt_human_scores': [],
        'total_sentences': len(results)
    }
    
    for result in results:
        mapping = result['mapping']
        evaluation = result['blind_evaluation']
        
        # Map scores back to sources
        if 'translation_A_score' in evaluation:
            score_a = evaluation['translation_A_score']
            score_b = evaluation['translation_B_score']
            score_c = evaluation['translation_C_score']
            
            # Find which translation got which score
            if mapping['A'] == 'GPT':
                analysis['gpt_self_scores'].append(score_a)
            elif mapping['B'] == 'GPT':
                analysis['gpt_self_scores'].append(score_b)
            elif mapping['C'] == 'GPT':
                analysis['gpt_self_scores'].append(score_c)
            
            if mapping['A'] == 'Google':
                analysis['gpt_google_scores'].append(score_a)
            elif mapping['B'] == 'Google':
                analysis['gpt_google_scores'].append(score_b)
            elif mapping['C'] == 'Google':
                analysis['gpt_google_scores'].append(score_c)
            
            if mapping['A'] == 'Human':
                analysis['gpt_human_scores'].append(score_a)
            elif mapping['B'] == 'Human':
                analysis['gpt_human_scores'].append(score_b)
            elif mapping['C'] == 'Human':
                analysis['gpt_human_scores'].append(score_c)
    
    # Calculate averages
    if analysis['gpt_self_scores']:
        analysis['avg_gpt_self'] = sum(analysis['gpt_self_scores']) / len(analysis['gpt_self_scores'])
    if analysis['gpt_google_scores']:
        analysis['avg_gpt_google'] = sum(analysis['gpt_google_scores']) / len(analysis['gpt_google_scores'])
    if analysis['gpt_human_scores']:
        analysis['avg_gpt_human'] = sum(analysis['gpt_human_scores']) / len(analysis['gpt_human_scores'])
    
    return analysis
