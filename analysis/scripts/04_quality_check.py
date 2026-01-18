#!/usr/bin/env python3
"""
04_quality_check.py
===================
Quality check: Review individual decisions against statistical conclusions.

Identifies exemplary cases that confirm or challenge the statistical findings.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "analysis" / "output" / "holdings_prepared.csv"
CODED_PATH = PROJECT_ROOT / "coded-decisions"
OUTPUT_PATH = PROJECT_ROOT / "analysis" / "output"

def load_coded_decision(case_id):
    """Load the coded decision markdown file for a case."""
    # Try different filename patterns
    patterns = [
        f"{case_id}_coded.md",
        f"{case_id.replace('/', '-')}_coded.md",
    ]

    for pattern in patterns:
        filepath = CODED_PATH / pattern
        if filepath.exists():
            with open(filepath, 'r') as f:
                return f.read()
    return None

def extract_justification(coded_text, holding_id=1):
    """Extract the direction justification from coded text."""
    if not coded_text:
        return None

    lines = coded_text.split('\n')
    in_holding = False
    target_holding = f"=== HOLDING {holding_id} ==="

    for i, line in enumerate(lines):
        if target_holding in line:
            in_holding = True
        elif in_holding and line.startswith("A33:"):
            return line.replace("A33:", "").strip()
        elif in_holding and "=== HOLDING" in line and target_holding not in line:
            break

    # If single holding, just find A33
    for line in lines:
        if line.startswith("A33:"):
            return line.replace("A33:", "").strip()

    return None

def run_quality_check(df):
    """Identify and review exemplary cases for each key finding."""

    print("=" * 70)
    print("QUALITY CHECK: INDIVIDUAL DECISION REVIEW")
    print("=" * 70)

    findings = []

    # =========================================================================
    # FINDING 1: TELEOLOGICAL INTERPRETATION → PRO-DS
    # =========================================================================
    print("\n" + "-" * 70)
    print("FINDING 1: Teleological Interpretation → Pro-Data Subject")
    print("-" * 70)

    # Cases that CONFIRM the finding (teleological + pro-DS)
    confirm_f1 = df[(df['teleological_present'] == 1) & (df['pro_ds'] == 1)]
    # Cases that CHALLENGE the finding (teleological + NOT pro-DS)
    challenge_f1 = df[(df['teleological_present'] == 1) & (df['pro_ds'] == 0)]

    print(f"\nConfirming cases: {len(confirm_f1)} holdings")
    print(f"Challenging cases: {len(challenge_f1)} holdings")

    # Sample confirming cases
    print("\n  CONFIRMING EXAMPLES (Teleological + Pro-DS):")
    sample_confirm = confirm_f1.sample(min(3, len(confirm_f1)), random_state=42)
    for _, row in sample_confirm.iterrows():
        print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
        print(f"    Ruling: {row['ruling_direction']}")
        print(f"    Core holding: {row['core_holding'][:100]}...")
        print(f"    Teleological quote: {str(row['teleological_quote'])[:100]}...")
        justification = row.get('direction_justification', 'N/A')
        print(f"    Direction justification: {justification}")

    # Sample challenging cases
    if len(challenge_f1) > 0:
        print("\n  CHALLENGING EXAMPLES (Teleological but NOT Pro-DS):")
        sample_challenge = challenge_f1.sample(min(3, len(challenge_f1)), random_state=42)
        for _, row in sample_challenge.iterrows():
            print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
            print(f"    Ruling: {row['ruling_direction']}")
            print(f"    Core holding: {row['core_holding'][:100]}...")
            justification = row.get('direction_justification', 'N/A')
            print(f"    Direction justification: {justification}")

    findings.append({
        'finding': 'Teleological → Pro-DS',
        'confirming_n': len(confirm_f1),
        'challenging_n': len(challenge_f1),
        'confirmation_rate': len(confirm_f1) / (len(confirm_f1) + len(challenge_f1)) if (len(confirm_f1) + len(challenge_f1)) > 0 else 0
    })

    # =========================================================================
    # FINDING 2: PRO-DS PURPOSE INVOCATION → PRO-DS OUTCOME
    # =========================================================================
    print("\n" + "-" * 70)
    print("FINDING 2: HIGH_LEVEL_OF_PROTECTION/FUNDAMENTAL_RIGHTS Purpose → Pro-DS")
    print("-" * 70)

    confirm_f2 = df[(df['pro_ds_purpose'] == 1) & (df['pro_ds'] == 1)]
    challenge_f2 = df[(df['pro_ds_purpose'] == 1) & (df['pro_ds'] == 0)]

    print(f"\nConfirming cases: {len(confirm_f2)} holdings")
    print(f"Challenging cases: {len(challenge_f2)} holdings")

    print("\n  CONFIRMING EXAMPLES (Pro-DS Purpose + Pro-DS Outcome):")
    sample_confirm = confirm_f2.sample(min(3, len(confirm_f2)), random_state=42)
    for _, row in sample_confirm.iterrows():
        print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
        print(f"    Purposes: {row['teleological_purposes']}")
        print(f"    Core holding: {row['core_holding'][:100]}...")

    if len(challenge_f2) > 0:
        print("\n  CHALLENGING EXAMPLES (Pro-DS Purpose but NOT Pro-DS Outcome):")
        sample_challenge = challenge_f2.sample(min(3, len(challenge_f2)), random_state=42)
        for _, row in sample_challenge.iterrows():
            print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
            print(f"    Ruling: {row['ruling_direction']}")
            print(f"    Purposes: {row['teleological_purposes']}")
            justification = row.get('direction_justification', 'N/A')
            print(f"    Direction justification: {justification}")

    findings.append({
        'finding': 'Pro-DS Purpose → Pro-DS',
        'confirming_n': len(confirm_f2),
        'challenging_n': len(challenge_f2),
        'confirmation_rate': len(confirm_f2) / (len(confirm_f2) + len(challenge_f2)) if (len(confirm_f2) + len(challenge_f2)) > 0 else 0
    })

    # =========================================================================
    # FINDING 3: LEVEL SHIFTING → PRO-DS
    # =========================================================================
    print("\n" + "-" * 70)
    print("FINDING 3: Level Shifting → Pro-Data Subject")
    print("-" * 70)

    confirm_f3 = df[(df['level_shifting'] == 1) & (df['pro_ds'] == 1)]
    challenge_f3 = df[(df['level_shifting'] == 1) & (df['pro_ds'] == 0)]

    print(f"\nConfirming cases: {len(confirm_f3)} holdings")
    print(f"Challenging cases: {len(challenge_f3)} holdings")

    if len(confirm_f3) > 0:
        print("\n  CONFIRMING EXAMPLES (Level Shifting + Pro-DS):")
        sample_confirm = confirm_f3.sample(min(3, len(confirm_f3)), random_state=42)
        for _, row in sample_confirm.iterrows():
            print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
            print(f"    Core holding: {row['core_holding'][:100]}...")
            shift_exp = row.get('level_shifting_explanation', 'N/A')
            if pd.notna(shift_exp) and shift_exp != 'NULL':
                print(f"    Level shifting: {str(shift_exp)[:150]}...")

    if len(challenge_f3) > 0:
        print("\n  CHALLENGING EXAMPLES (Level Shifting but NOT Pro-DS):")
        sample_challenge = challenge_f3.sample(min(3, len(challenge_f3)), random_state=42)
        for _, row in sample_challenge.iterrows():
            print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
            print(f"    Ruling: {row['ruling_direction']}")
            justification = row.get('direction_justification', 'N/A')
            print(f"    Direction justification: {justification}")

    findings.append({
        'finding': 'Level Shifting → Pro-DS',
        'confirming_n': len(confirm_f3),
        'challenging_n': len(challenge_f3),
        'confirmation_rate': len(confirm_f3) / (len(confirm_f3) + len(challenge_f3)) if (len(confirm_f3) + len(challenge_f3)) > 0 else 0
    })

    # =========================================================================
    # FINDING 4: BALANCING → LESS PRO-DS
    # =========================================================================
    print("\n" + "-" * 70)
    print("FINDING 4: Explicit Balancing → Fewer Pro-DS Outcomes")
    print("-" * 70)

    confirm_f4 = df[(df['any_balancing'] == 1) & (df['pro_ds'] == 0)]
    challenge_f4 = df[(df['any_balancing'] == 1) & (df['pro_ds'] == 1)]

    print(f"\nConfirming cases (balancing + NOT pro-DS): {len(confirm_f4)} holdings")
    print(f"Challenging cases (balancing + pro-DS): {len(challenge_f4)} holdings")

    # Pro-DS rate when balancing present vs absent
    bal_pro_ds_rate = df[df['any_balancing'] == 1]['pro_ds'].mean()
    no_bal_pro_ds_rate = df[df['any_balancing'] == 0]['pro_ds'].mean()
    print(f"\nPro-DS rate with balancing: {bal_pro_ds_rate*100:.1f}%")
    print(f"Pro-DS rate without balancing: {no_bal_pro_ds_rate*100:.1f}%")

    if len(confirm_f4) > 0:
        print("\n  CONFIRMING EXAMPLES (Balancing + NOT Pro-DS):")
        sample_confirm = confirm_f4.sample(min(3, len(confirm_f4)), random_state=42)
        for _, row in sample_confirm.iterrows():
            print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
            print(f"    Ruling: {row['ruling_direction']}")
            print(f"    Interest prevails: {row.get('interest_prevails', 'N/A')}")
            print(f"    Core holding: {row['core_holding'][:100]}...")

    findings.append({
        'finding': 'Balancing → Fewer Pro-DS',
        'confirming_n': len(confirm_f4),
        'challenging_n': len(challenge_f4),
        'confirmation_rate': len(confirm_f4) / (len(confirm_f4) + len(challenge_f4)) if (len(confirm_f4) + len(challenge_f4)) > 0 else 0
    })

    # =========================================================================
    # FINDING 5: SEMANTIC DOMINANT → FEWER PRO-DS
    # =========================================================================
    print("\n" + "-" * 70)
    print("FINDING 5: Semantic Dominant Source → Fewer Pro-DS Outcomes")
    print("-" * 70)

    semantic_df = df[df['dominant_source'] == 'SEMANTIC']
    non_semantic_df = df[df['dominant_source'] != 'SEMANTIC']

    sem_pro_ds_rate = semantic_df['pro_ds'].mean() if len(semantic_df) > 0 else 0
    non_sem_pro_ds_rate = non_semantic_df['pro_ds'].mean() if len(non_semantic_df) > 0 else 0

    print(f"\nSemantic dominant: {sem_pro_ds_rate*100:.1f}% pro-DS (n={len(semantic_df)})")
    print(f"Other dominant: {non_sem_pro_ds_rate*100:.1f}% pro-DS (n={len(non_semantic_df)})")

    # Cases where semantic led to pro-controller
    confirm_f5 = df[(df['dominant_source'] == 'SEMANTIC') & (df['pro_ds'] == 0)]
    challenge_f5 = df[(df['dominant_source'] == 'SEMANTIC') & (df['pro_ds'] == 1)]

    print(f"\nSemantic + NOT Pro-DS: {len(confirm_f5)} holdings")
    print(f"Semantic + Pro-DS: {len(challenge_f5)} holdings")

    if len(confirm_f5) > 0:
        print("\n  CONFIRMING EXAMPLES (Semantic + NOT Pro-DS):")
        sample_confirm = confirm_f5.sample(min(3, len(confirm_f5)), random_state=42)
        for _, row in sample_confirm.iterrows():
            print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
            print(f"    Ruling: {row['ruling_direction']}")
            print(f"    Semantic quote: {str(row.get('semantic_quote', 'N/A'))[:100]}...")

    findings.append({
        'finding': 'Semantic → Fewer Pro-DS',
        'confirming_n': len(confirm_f5),
        'challenging_n': len(challenge_f5),
        'confirmation_rate': len(confirm_f5) / (len(confirm_f5) + len(challenge_f5)) if (len(confirm_f5) + len(challenge_f5)) > 0 else 0
    })

    # =========================================================================
    # OUTLIER ANALYSIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("OUTLIER ANALYSIS: SURPRISING CASES")
    print("=" * 70)

    # Find cases that contradict all expectations
    # Expected pro-DS: teleological + pro-DS purpose + level shifting
    # Actual: NOT pro-DS
    expected_pro_ds = df[
        (df['teleological_present'] == 1) &
        (df['pro_ds_purpose'] == 1) &
        (df['any_balancing'] == 0)
    ]
    surprising_not_pro_ds = expected_pro_ds[expected_pro_ds['pro_ds'] == 0]

    print(f"\nSURPRISING: Expected pro-DS but ruled otherwise (n={len(surprising_not_pro_ds)})")
    for _, row in surprising_not_pro_ds.iterrows():
        print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
        print(f"    Ruling: {row['ruling_direction']}")
        print(f"    Core holding: {row['core_holding'][:120]}...")
        justification = row.get('direction_justification', 'N/A')
        print(f"    Direction justification: {justification}")

    # Expected NOT pro-DS: semantic dominant + balancing
    # Actual: pro-DS
    expected_not_pro_ds = df[
        (df['dominant_source'] == 'SEMANTIC') &
        (df['any_balancing'] == 1)
    ]
    surprising_pro_ds = expected_not_pro_ds[expected_not_pro_ds['pro_ds'] == 1]

    print(f"\nSURPRISING: Expected NOT pro-DS but ruled pro-DS (n={len(surprising_pro_ds)})")
    for _, row in surprising_pro_ds.head(5).iterrows():
        print(f"\n  Case: {row['case_id']}, Holding {row['holding_id']}")
        print(f"    Ruling: {row['ruling_direction']}")
        print(f"    Core holding: {row['core_holding'][:120]}...")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("QUALITY CHECK SUMMARY")
    print("=" * 70)

    summary_df = pd.DataFrame(findings)
    summary_df['confirmation_rate'] = summary_df['confirmation_rate'].apply(lambda x: f"{x*100:.1f}%")
    print("\n" + summary_df.to_string(index=False))

    # Overall assessment
    avg_confirmation = np.mean([f['confirming_n'] / (f['confirming_n'] + f['challenging_n'])
                                for f in findings if (f['confirming_n'] + f['challenging_n']) > 0])
    print(f"\nOverall average confirmation rate: {avg_confirmation*100:.1f}%")

    if avg_confirmation >= 0.7:
        print("ASSESSMENT: Statistical findings are well-supported by individual case review")
    elif avg_confirmation >= 0.5:
        print("ASSESSMENT: Statistical findings have moderate support; some nuance required")
    else:
        print("ASSESSMENT: Statistical findings require careful interpretation; many exceptions")

    # Save results
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(OUTPUT_PATH / "quality_check_summary.csv", index=False)

    with open(OUTPUT_PATH / "quality_check_details.json", 'w') as f:
        json.dump({
            'findings': findings,
            'surprising_not_pro_ds': surprising_not_pro_ds[['case_id', 'holding_id', 'ruling_direction', 'core_holding']].to_dict('records'),
            'surprising_pro_ds': surprising_pro_ds[['case_id', 'holding_id', 'ruling_direction', 'core_holding']].to_dict('records')[:10]
        }, f, indent=2, default=str)

    print(f"\nResults saved to {OUTPUT_PATH}")

    return findings

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    findings = run_quality_check(df)
    print("\nQuality check complete!")
