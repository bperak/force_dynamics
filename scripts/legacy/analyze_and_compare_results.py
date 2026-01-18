"""
Analyze new results and compare with old methodology (if available)
"""

import pandas as pd
import json
from improved_methodology import analyze_blind_results

def load_and_analyze_new_results():
    """Load and analyze new methodology results"""
    print("="*80)
    print("ANALYZING NEW METHODOLOGY RESULTS")
    print("="*80)
    
    results = {}
    
    # Try to load each language
    languages = ['Finnish', 'Polish', 'Croatian']
    
    for lang in languages:
        filename = f'{lang}_evaluation_IMPROVED.xlsx'
        try:
            df = pd.read_excel(filename)
            print(f"\n[OK] Loaded {lang} results: {len(df)} sentences")
            
            # Parse results from Excel (stored as strings)
            results_list = []
            for idx, row in df.iterrows():
                try:
                    # Parse mapping (stored as string representation of dict)
                    mapping_str = row.get('mapping', '{}')
                    if isinstance(mapping_str, str):
                        # Replace single quotes with double quotes for JSON
                        mapping_str = mapping_str.replace("'", '"')
                        mapping = json.loads(mapping_str)
                    else:
                        mapping = mapping_str
                    
                    # Parse blind_evaluation (stored as string representation of dict)
                    eval_str = row.get('blind_evaluation', '{}')
                    if isinstance(eval_str, str):
                        # Try to parse - may have single quotes
                        try:
                            # First try as JSON
                            blind_eval = json.loads(eval_str)
                        except:
                            # If that fails, try eval (less safe but needed for single quotes)
                            blind_eval = eval(eval_str) if eval_str else {}
                    else:
                        blind_eval = eval_str
                    
                    result = {
                        'original_text': row.get('original_text', ''),
                        'translation_gpt': row.get('translation_gpt', ''),
                        'translation_google': row.get('translation_google', ''),
                        'translation_human': row.get('translation_human', ''),
                        'mapping': mapping,
                        'blind_evaluation': blind_eval
                    }
                    results_list.append(result)
                except Exception as e:
                    print(f"    [WARNING] Error parsing row {idx}: {e}")
                    continue
            
            # Analyze
            try:
                analysis = analyze_blind_results(results_list)
            except Exception as e:
                print(f"    [WARNING] Could not analyze {lang}: {e}")
                import traceback
                traceback.print_exc()
                analysis = {}
            results[lang] = {
                'data': results_list,
                'analysis': analysis
            }
            
            print(f"  Average GPT self-score: {analysis.get('avg_gpt_self', 'N/A'):.3f}")
            print(f"  Average GPT score for Google: {analysis.get('avg_gpt_google', 'N/A'):.3f}")
            print(f"  Average GPT score for Human: {analysis.get('avg_gpt_human', 'N/A'):.3f}")
            
            # Calculate bias
            if analysis.get('avg_gpt_self') and analysis.get('avg_gpt_human'):
                bias = analysis.get('avg_gpt_self') - analysis.get('avg_gpt_human')
                print(f"  Bias (self - human): {bias:+.3f}")
                if bias > 0.05:
                    print(f"    [NOTE] GPT shows self-scoring bias")
                elif bias < -0.05:
                    print(f"    [NOTE] GPT rates itself lower (interesting)")
                else:
                    print(f"    [NOTE] Relatively neutral scoring")
                    
        except FileNotFoundError:
            print(f"\n[WARNING] {filename} not found - processing may still be running")
        except Exception as e:
            print(f"\n[ERROR] Error loading {lang}: {e}")
    
    return results

def load_old_results():
    """Try to load old methodology results for comparison"""
    print("\n" + "="*80)
    print("ATTEMPTING TO LOAD OLD RESULTS FOR COMPARISON")
    print("="*80)
    
    old_results = {}
    
    # Try to find old Excel files
    old_files = {
        'Finnish': 'Finnish_evaluation.xlsx',
        'Polish': 'Polish_evaluation.xlsx',
        'Croatian': 'Croatian_evaluation.xlsx'
    }
    
    for lang, filename in old_files.items():
        try:
            df = pd.read_excel(filename)
            print(f"\n[OK] Found old {lang} results: {len(df)} sentences")
            
            # Extract scores if available
            if 'trans_quality_GPT_n' in df.columns:
                gpt_scores = df['trans_quality_GPT_n'].dropna().tolist()
                google_scores = df['trans_quality_Google_n'].dropna().tolist() if 'trans_quality_Google_n' in df.columns else []
                human_scores = df['trans_quality_User_n'].dropna().tolist() if 'trans_quality_User_n' in df.columns else []
                
                old_results[lang] = {
                    'gpt_self': gpt_scores,
                    'gpt_google': google_scores,
                    'gpt_human': human_scores,
                    'avg_gpt_self': sum(gpt_scores) / len(gpt_scores) if gpt_scores else None,
                    'avg_gpt_google': sum(google_scores) / len(google_scores) if google_scores else None,
                    'avg_gpt_human': sum(human_scores) / len(human_scores) if human_scores else None
                }
                
                print(f"  Old average GPT self-score: {old_results[lang]['avg_gpt_self']:.3f}")
                if old_results[lang]['avg_gpt_google']:
                    print(f"  Old average GPT score for Google: {old_results[lang]['avg_gpt_google']:.3f}")
                if old_results[lang]['avg_gpt_human']:
                    print(f"  Old average GPT score for Human: {old_results[lang]['avg_gpt_human']:.3f}")
                    
        except FileNotFoundError:
            print(f"\n[INFO] Old {lang} results not found - skipping comparison")
        except Exception as e:
            print(f"\n[WARNING] Error loading old {lang} results: {e}")
    
    return old_results

def compare_results(new_results, old_results):
    """Compare new and old results"""
    print("\n" + "="*80)
    print("COMPARING OLD vs NEW METHODOLOGY")
    print("="*80)
    
    for lang in ['Finnish', 'Polish', 'Croatian']:
        if lang in new_results and lang in old_results:
            print(f"\n{lang} Comparison:")
            print("-" * 60)
            
            new_analysis = new_results[lang]['analysis']
            old_analysis = old_results[lang]
            
            # Compare GPT self-scores
            if new_analysis.get('avg_gpt_self') and old_analysis.get('avg_gpt_self'):
                new_self = new_analysis.get('avg_gpt_self')
                old_self = old_analysis.get('avg_gpt_self')
                diff = new_self - old_self
                print(f"GPT Self-Score:")
                print(f"  Old: {old_self:.3f}")
                print(f"  New: {new_self:.3f}")
                print(f"  Difference: {diff:+.3f} ({'higher' if diff > 0 else 'lower'} in new methodology)")
            
            # Compare GPT Human scores
            if new_analysis.get('avg_gpt_human') and old_analysis.get('avg_gpt_human'):
                new_human = new_analysis.get('avg_gpt_human')
                old_human = old_analysis.get('avg_gpt_human')
                diff = new_human - old_human
                print(f"\nGPT Human Score:")
                print(f"  Old: {old_human:.3f}")
                print(f"  New: {new_human:.3f}")
                print(f"  Difference: {diff:+.3f}")
            
            # Compare bias
            if (new_analysis.get('avg_gpt_self') and new_analysis.get('avg_gpt_human') and
                old_analysis.get('avg_gpt_self') and old_analysis.get('avg_gpt_human')):
                new_bias = new_analysis.get('avg_gpt_self') - new_analysis.get('avg_gpt_human')
                old_bias = old_analysis.get('avg_gpt_self') - old_analysis.get('avg_gpt_human')
                bias_change = new_bias - old_bias
                
                print(f"\nBias (Self - Human):")
                print(f"  Old: {old_bias:+.3f}")
                print(f"  New: {new_bias:+.3f}")
                print(f"  Change: {bias_change:+.3f}")
                if abs(bias_change) > 0.05:
                    if bias_change < 0:
                        print(f"    [NOTE] Bias REDUCED with blind evaluation!")
                    else:
                        print(f"    [NOTE] Bias increased (unexpected)")
                else:
                    print(f"    [NOTE] Bias similar (blind evaluation may not have changed bias much)")

def main():
    """Main analysis"""
    # Load new results
    new_results = load_and_analyze_new_results()
    
    if not new_results:
        print("\n[WARNING] No new results found. Processing may still be running.")
        print("Check if *_IMPROVED.xlsx files exist.")
        return
    
    # Try to load old results
    old_results = load_old_results()
    
    # Compare if both available
    if old_results:
        compare_results(new_results, old_results)
    else:
        print("\n[INFO] Old results not available for comparison.")
        print("New methodology results are ready for analysis.")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\nNew methodology results:")
    for lang, data in new_results.items():
        analysis = data['analysis']
        print(f"\n{lang}:")
        print(f"  GPT self-score: {analysis.get('avg_gpt_self', 'N/A'):.3f}")
        print(f"  GPT Google score: {analysis.get('avg_gpt_google', 'N/A'):.3f}")
        print(f"  GPT Human score: {analysis.get('avg_gpt_human', 'N/A'):.3f}")
    
    print("\n[OK] Analysis complete!")
    print("\nNext steps:")
    print("1. Review results in Excel files")
    print("2. Update paper Results section")
    print("3. Document findings")
    print("4. Complete paper revision")

if __name__ == "__main__":
    main()
