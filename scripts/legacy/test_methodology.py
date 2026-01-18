"""
Standalone test script for new methodology
Run this to test the improved translation and evaluation system
"""

import pandas as pd
import json
import sys
import os

# Fix encoding for Windows
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded .env file")
except ImportError:
    # dotenv not installed, try to load manually
    try:
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
            print("[OK] Loaded .env file manually")
    except:
        pass

# Try to import the improved methodology
try:
    from improved_methodology import (
        get_gpt_translation,
        blind_evaluation,
        process_sentence_blind,
        analyze_blind_results
    )
    print("[OK] Successfully imported improved methodology functions")
except ImportError as e:
    print(f"[ERROR] Error importing improved methodology: {e}")
    print("Make sure improved_methodology.py is in the same directory")
    sys.exit(1)

# Check if OpenAI is configured
try:
    import openai
    # Check if API key is available from .env
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai.api_key = api_key
        print("[OK] OpenAI API key loaded from .env")
    elif hasattr(openai, 'api_key') and openai.api_key:
        print("[OK] OpenAI API key is set")
    else:
        print("[WARNING] OpenAI API key not set")
        print("Make sure .env file contains: OPENAI_API_KEY=your-key-here")
except ImportError:
    print("[ERROR] OpenAI module not found. Install with: pip install openai==0.28")
    sys.exit(1)

def test_translation():
    """Test Phase 1: Translation"""
    print("\n" + "="*80)
    print("TEST 1: TRANSLATION FUNCTION")
    print("="*80)
    
    test_text = "A fine day like this made her impatient."
    
    try:
        translation = get_gpt_translation(
            source_language='English',
            target_language='Finnish',
            original_text=test_text,
            model='gpt-4o'
        )
        
        print(f"[OK] Translation successful!")
        print(f"   Original: {test_text}")
        print(f"   Translation: {translation}")
        return True, translation
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        return False, None

def test_blind_evaluation(translation_gpt, translation_google, translation_human):
    """Test Phase 2: Blind Evaluation"""
    print("\n" + "="*80)
    print("TEST 2: BLIND EVALUATION")
    print("="*80)
    
    original_text = "A fine day like this made her impatient."
    
    try:
        result = process_sentence_blind(
            source_language='English',
            target_language='Finnish',
            original_text=original_text,
            translation_google=translation_google,
            translation_human=translation_human,
            model='gpt-4o'
        )
        
        print(f"[OK] Blind evaluation successful!")
        print(f"\n   GPT Translation: {result['translation_gpt']}")
        print(f"\n   Mapping:")
        print(f"      Translation A = {result['mapping']['A']}")
        print(f"      Translation B = {result['mapping']['B']}")
        print(f"      Translation C = {result['mapping']['C']}")
        
        if 'blind_evaluation' in result:
            eval_data = result['blind_evaluation']
            print(f"\n   Scores:")
            print(f"      A: {eval_data.get('translation_A_score', 'N/A')}")
            print(f"      B: {eval_data.get('translation_B_score', 'N/A')}")
            print(f"      C: {eval_data.get('translation_C_score', 'N/A')}")
            
            # Check if FD framework is mentioned
            descriptions = [
                eval_data.get('translation_A_description', ''),
                eval_data.get('translation_B_description', ''),
                eval_data.get('translation_C_description', '')
            ]
            
            fd_mentioned = any('force' in desc.lower() or 'agonist' in desc.lower() or 'antagonist' in desc.lower() 
                              for desc in descriptions)
            
            if fd_mentioned:
                print(f"\n   [OK] Force Dynamics framework mentioned in descriptions")
            else:
                print(f"\n   [WARNING] Force Dynamics framework not clearly mentioned")
        
        return True, result
    except Exception as e:
        print(f"[ERROR] Blind evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_with_real_data():
    """Test with actual data from spreadsheet"""
    print("\n" + "="*80)
    print("TEST 3: WITH REAL DATA")
    print("="*80)
    
    try:
        # Try to load data
        link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpFclgUNhF1CSHDHPyQCaSUojcPALed14HFzCMFiseOe1izFPyWOXeDgRABKLhH0ckTW3ffFa1xjRv/pub?output=xlsx"
        df = pd.read_excel(link)
        print(f"[OK] Data loaded: {len(df)} sentences")
        
        # Get first sentence
        test_sentence = df.iloc[0]
        original = test_sentence['English Original']
        google = test_sentence['Finnish MT (Google Translate)']
        human = test_sentence['Finnish Human Reference']
        
        print(f"\n   Original: {original}")
        print(f"   Google: {google}")
        print(f"   Human: {human}")
        
        # Process
        result = process_sentence_blind(
            source_language='English',
            target_language='Finnish',
            original_text=original,
            translation_google=google,
            translation_human=human,
            model='gpt-4o'
        )
        
        print(f"\n[OK] Processing successful!")
        print(f"\n   GPT Translation: {result['translation_gpt']}")
        print(f"\n   Mapping: {result['mapping']}")
        
        if 'blind_evaluation' in result:
            eval_data = result['blind_evaluation']
            print(f"\n   Evaluation Scores:")
            print(f"      A ({result['mapping']['A']}): {eval_data.get('translation_A_score', 'N/A')}")
            print(f"      B ({result['mapping']['B']}): {eval_data.get('translation_B_score', 'N/A')}")
            print(f"      C ({result['mapping']['C']}): {eval_data.get('translation_C_score', 'N/A')}")
        
        return True, result
    except Exception as e:
        print(f"[ERROR] Test with real data failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Run all tests"""
    print("="*80)
    print("TESTING NEW METHODOLOGY")
    print("="*80)
    print("\nThis script tests:")
    print("1. Translation function (separate task)")
    print("2. Blind evaluation (A/B/C labels)")
    print("3. FD framework usage")
    print("4. Real data processing")
    
    # Check API key
    try:
        import openai
        # Try to get from environment (loaded from .env)
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            print("[OK] Using API key from .env file")
        elif hasattr(openai, 'api_key') and openai.api_key:
            print("[OK] Using existing API key")
        else:
            print("\n[WARNING] OpenAI API key not found")
            print("Make sure .env file contains: OPENAI_API_KEY=your-key-here")
            print("\nCannot run tests without API key.")
            return
    except Exception as e:
        print(f"[ERROR] Error checking API key: {e}")
        return
    
    results = {}
    
    # Test 1: Translation
    success, translation = test_translation()
    results['translation'] = success
    
    if not success:
        print("\n[ERROR] Translation test failed. Cannot continue.")
        return
    
    # Test 2: Blind evaluation (with sample translations)
    translation_google = "Tällainen hieno päivä sai hänet kärsimättömäksi."
    translation_human = "Tällainen upea päivä sai hänet kärsimättömäksi."
    
    success, eval_result = test_blind_evaluation(translation, translation_google, translation_human)
    results['blind_evaluation'] = success
    
    # Test 3: Real data
    success, real_result = test_with_real_data()
    results['real_data'] = success
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n[OK] All tests passed! Methodology is ready to use.")
    else:
        print("\n[WARNING] Some tests failed. Review errors above.")

if __name__ == "__main__":
    main()
