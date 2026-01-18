"""
Process all sentences with improved methodology
This script processes Finnish, Polish, and Croatian sentences
"""

import pandas as pd
import json
import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if 'OPENAI_API_KEY' in line and '=' in line:
                    key = line.split('=', 1)[1].strip()
                    os.environ['OPENAI_API_KEY'] = key

# Import improved methodology
from improved_methodology import (
    process_dataframe_blind,
    analyze_blind_results
)

def process_all():
    """Process all languages"""
    
    print("="*80)
    print("PROCESSING ALL SENTENCES WITH IMPROVED METHODOLOGY")
    print("="*80)
    print("\nKey improvements:")
    print("1. Translation separated from evaluation")
    print("2. Blind evaluation (A/B/C labels)")
    print("3. Explicit FD framework")
    print("4. Bias detection")
    print("\n" + "="*80)
    
    # Load data
    print("\n[1/4] Loading data...")
    link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpFclgUNhF1CSHDHPyQCaSUojcPALed14HFzCMFiseOe1izFPyWOXeDgRABKLhH0ckTW3ffFa1xjRv/pub?output=xlsx"
    df = pd.read_excel(link)
    print(f"   [OK] Loaded {len(df)} sentences")
    
    link_hr = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSCb5y3L7siAReDJ2QgaJCoR2b_GnuEciIoGRfdzigi1J0-7IJuSTc2K3WlmH-87czMtKNQsB0oUmAj/pub?output=xlsx'
    df_hr = pd.read_excel(link_hr)
    print(f"   [OK] Loaded {len(df_hr)} Croatian sentences")
    
    # Process Finnish
    print("\n[2/4] Processing Finnish sentences...")
    print("   This may take 5-10 minutes...")
    results_finnish = process_dataframe_blind(
        df,
        source_language='English',
        target_language='Finnish',
        original_col='English Original',
        google_col='Finnish MT (Google Translate)',
        human_col='Finnish Human Reference',
        model='gpt-4o'
    )
    df_finnish = pd.DataFrame(results_finnish)
    df_finnish.to_excel('Finnish_evaluation_IMPROVED.xlsx', index=False)
    print(f"   [OK] Processed {len(results_finnish)} Finnish sentences")
    print(f"   [OK] Saved to: Finnish_evaluation_IMPROVED.xlsx")
    
    # Analyze Finnish
    analysis_finnish = analyze_blind_results(results_finnish)
    print(f"\n   Finnish Analysis:")
    print(f"   - GPT self-score: {analysis_finnish.get('avg_gpt_self', 'N/A'):.3f}")
    print(f"   - GPT score for Google: {analysis_finnish.get('avg_gpt_google', 'N/A'):.3f}")
    print(f"   - GPT score for Human: {analysis_finnish.get('avg_gpt_human', 'N/A'):.3f}")
    
    # Process Polish
    print("\n[3/4] Processing Polish sentences...")
    print("   This may take 5-10 minutes...")
    results_polish = process_dataframe_blind(
        df,
        source_language='English',
        target_language='Polish',
        original_col='English Original',
        google_col='Polish MT (Google Translate)',
        human_col='Polish Human Reference',
        model='gpt-4o'
    )
    df_polish = pd.DataFrame(results_polish)
    df_polish.to_excel('Polish_evaluation_IMPROVED.xlsx', index=False)
    print(f"   [OK] Processed {len(results_polish)} Polish sentences")
    print(f"   [OK] Saved to: Polish_evaluation_IMPROVED.xlsx")
    
    # Analyze Polish
    analysis_polish = analyze_blind_results(results_polish)
    print(f"\n   Polish Analysis:")
    print(f"   - GPT self-score: {analysis_polish.get('avg_gpt_self', 'N/A'):.3f}")
    print(f"   - GPT score for Google: {analysis_polish.get('avg_gpt_google', 'N/A'):.3f}")
    print(f"   - GPT score for Human: {analysis_polish.get('avg_gpt_human', 'N/A'):.3f}")
    
    # Process Croatian
    print("\n[4/4] Processing Croatian sentences...")
    print("   This may take 5-10 minutes...")
    results_croatian = process_dataframe_blind(
        df_hr,
        source_language='English',
        target_language='Croatian',
        original_col='English Original',
        google_col='Croatian MT (Google Translate)',
        human_col='Croatian Human Reference',
        model='gpt-4o'
    )
    df_croatian = pd.DataFrame(results_croatian)
    df_croatian.to_excel('Croatian_evaluation_IMPROVED.xlsx', index=False)
    print(f"   [OK] Processed {len(results_croatian)} Croatian sentences")
    print(f"   [OK] Saved to: Croatian_evaluation_IMPROVED.xlsx")
    
    # Analyze Croatian
    analysis_croatian = analyze_blind_results(results_croatian)
    print(f"\n   Croatian Analysis:")
    print(f"   - GPT self-score: {analysis_croatian.get('avg_gpt_self', 'N/A'):.3f}")
    print(f"   - GPT score for Google: {analysis_croatian.get('avg_gpt_google', 'N/A'):.3f}")
    print(f"   - GPT score for Human: {analysis_croatian.get('avg_gpt_human', 'N/A'):.3f}")
    
    # Summary
    print("\n" + "="*80)
    print("PROCESSING COMPLETE!")
    print("="*80)
    print("\nResults saved to:")
    print("  - Finnish_evaluation_IMPROVED.xlsx")
    print("  - Polish_evaluation_IMPROVED.xlsx")
    print("  - Croatian_evaluation_IMPROVED.xlsx")
    
    print("\nSummary of all languages:")
    print(f"\n{'Language':<12} {'GPT Self':<12} {'Google':<12} {'Human':<12}")
    print("-" * 50)
    print(f"{'Finnish':<12} {analysis_finnish.get('avg_gpt_self', 0):.3f}        {analysis_finnish.get('avg_gpt_google', 0):.3f}        {analysis_finnish.get('avg_gpt_human', 0):.3f}")
    print(f"{'Polish':<12} {analysis_polish.get('avg_gpt_self', 0):.3f}        {analysis_polish.get('avg_gpt_google', 0):.3f}        {analysis_polish.get('avg_gpt_human', 0):.3f}")
    print(f"{'Croatian':<12} {analysis_croatian.get('avg_gpt_self', 0):.3f}        {analysis_croatian.get('avg_gpt_google', 0):.3f}        {analysis_croatian.get('avg_gpt_human', 0):.3f}")
    
    print("\n[OK] All processing complete!")
    print("\nNext steps:")
    print("1. Review Excel files")
    print("2. Compare with old methodology")
    print("3. Update paper methodology section")
    print("4. Analyze findings")

if __name__ == "__main__":
    try:
        process_all()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Processing interrupted by user")
        print("Results saved up to interruption point")
    except Exception as e:
        print(f"\n[ERROR] Processing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
