"""
Extract Force Dynamics analysis from evaluation results.
"""
import pandas as pd
import json
import ast
from collections import defaultdict

def extract_fd_info(blind_eval_str):
    """Extract FD information from blind evaluation JSON string."""
    try:
        # Parse the JSON-like string
        eval_data = ast.literal_eval(blind_eval_str)
        
        fd_info = {
            'A': {
                'description': eval_data.get('translation_A_description', ''),
                'score': eval_data.get('translation_A_score', 0)
            },
            'B': {
                'description': eval_data.get('translation_B_description', ''),
                'score': eval_data.get('translation_B_score', 0)
            },
            'C': {
                'description': eval_data.get('translation_C_description', ''),
                'score': eval_data.get('translation_C_score', 0)
            },
            'comparison': eval_data.get('comparison', '')
        }
        return fd_info
    except:
        return None

def analyze_fd_patterns(df, language):
    """Analyze Force Dynamics patterns in the results."""
    print(f"\n{'='*60}")
    print(f"FORCE DYNAMICS ANALYSIS: {language.upper()}")
    print(f"{'='*60}\n")
    
    fd_relations = defaultdict(int)
    agonist_mentions = 0
    antagonist_mentions = 0
    causation_count = 0
    permission_count = 0
    blocking_count = 0
    
    total_sentences = len(df)
    
    for idx, row in df.iterrows():
        fd_info = extract_fd_info(row['blind_evaluation'])
        if not fd_info:
            continue
            
        # Check all three descriptions
        for key in ['A', 'B', 'C']:
            desc = fd_info[key]['description'].lower()
            
            # Count FD relation types
            if 'causation' in desc or 'causing' in desc:
                causation_count += 1
            if 'permission' in desc:
                permission_count += 1
            if 'blocking' in desc or 'block' in desc:
                blocking_count += 1
            
            # Count Agonist/Antagonist mentions
            if 'agonist' in desc:
                agonist_mentions += 1
            if 'antagonist' in desc:
                antagonist_mentions += 1
    
    print(f"Total sentences analyzed: {total_sentences}")
    print(f"\nForce Dynamics Elements Identified:")
    print(f"  - Agonist mentions: {agonist_mentions} (across {total_sentences} sentences)")
    print(f"  - Antagonist mentions: {antagonist_mentions} (across {total_sentences} sentences)")
    print(f"\nForce Relation Types:")
    print(f"  - Causation: {causation_count} mentions")
    print(f"  - Permission: {permission_count} mentions")
    print(f"  - Blocking: {blocking_count} mentions")
    
    # Calculate percentages
    total_evaluations = total_sentences * 3  # 3 translations per sentence
    print(f"\nPercentage of evaluations identifying FD elements:")
    print(f"  - Agonist: {agonist_mentions/total_evaluations*100:.1f}%")
    print(f"  - Antagonist: {antagonist_mentions/total_evaluations*100:.1f}%")
    
    return {
        'total_sentences': total_sentences,
        'agonist_mentions': agonist_mentions,
        'antagonist_mentions': antagonist_mentions,
        'causation_count': causation_count,
        'permission_count': permission_count,
        'blocking_count': blocking_count
    }

def get_example_analyses(df, language, n=2):
    """Get example FD analyses."""
    print(f"\n{'='*60}")
    print(f"EXAMPLE ANALYSES: {language.upper()}")
    print(f"{'='*60}\n")
    
    examples = []
    for idx, row in df.iterrows()[:n]:
        fd_info = extract_fd_info(row['blind_evaluation'])
        mapping = ast.literal_eval(row['mapping'])
        
        print(f"\nExample {idx + 1}:")
        print(f"Original: {row['original_text']}")
        print(f"\nEvaluations:")
        
        for key in ['A', 'B', 'C']:
            trans_type = mapping[key]
            score = fd_info[key]['score']
            desc = fd_info[key]['description']
            
            print(f"\n  {key} ({trans_type}) - Score: {score}")
            # Extract just the FD-relevant part
            if 'Agonist' in desc or 'Antagonist' in desc:
                if 'Semantics:' in desc:
                    fd_parts = desc.split('Semantics:')
                    if len(fd_parts) > 1:
                        fd_part = fd_parts[1]
                        print(f"    {fd_part[:200]}...")
                    else:
                        print(f"    {desc[:200]}...")
                else:
                    print(f"    {desc[:200]}...")
        
        examples.append({
            'original': row['original_text'],
            'analyses': fd_info
        })
    
    return examples

# Process all three languages
languages = ['Finnish', 'Polish', 'Croatian']
all_results = {}

for lang in languages:
    filename = f"{lang}_evaluation_IMPROVED.xlsx"
    try:
        df = pd.read_excel(filename)
        results = analyze_fd_patterns(df, lang)
        examples = get_example_analyses(df, lang, n=2)
        all_results[lang] = {
            'stats': results,
            'examples': examples
        }
    except Exception as e:
        print(f"Error processing {lang}: {e}")

# Summary across all languages
print(f"\n{'='*60}")
print("SUMMARY ACROSS ALL LANGUAGES")
print(f"{'='*60}\n")

for lang, data in all_results.items():
    stats = data['stats']
    print(f"{lang}:")
    print(f"  Agonist identified: {stats['agonist_mentions']}/{stats['total_sentences']*3} ({stats['agonist_mentions']/(stats['total_sentences']*3)*100:.1f}%)")
    print(f"  Antagonist identified: {stats['antagonist_mentions']}/{stats['total_sentences']*3} ({stats['antagonist_mentions']/(stats['total_sentences']*3)*100:.1f}%)")
    print()
