#!/usr/bin/env python3
"""
Analyze judge rapporteur patterns:
1. Topic specialization (primary_concept distribution)
2. Ruling direction tendencies (pro-DS vs pro-controller)
"""

import json
from collections import defaultdict
from pathlib import Path


def load_data():
    with open(Path(__file__).parent.parent / 'parsed-coded' / 'cases.json') as f:
        return json.load(f)


def analyze_rapporteur_topics(cases):
    """Hypothesis 1: Do rapporteurs specialize in certain topics?"""
    # Count holdings per rapporteur per concept
    rapporteur_concepts = defaultdict(lambda: defaultdict(int))
    rapporteur_total = defaultdict(int)
    
    for case in cases:
        rapporteur = case.get('judge_rapporteur')
        if not rapporteur:
            continue
        for holding in case.get('holdings', []):
            concept = holding.get('primary_concept', 'OTHER')
            rapporteur_concepts[rapporteur][concept] += 1
            rapporteur_total[rapporteur] += 1
    
    print("=" * 70)
    print("HYPOTHESIS 1: RAPPORTEUR TOPIC SPECIALIZATION")
    print("=" * 70)
    
    # Only show rapporteurs with 5+ holdings for meaningful analysis
    active_rapporteurs = {r: t for r, t in rapporteur_total.items() if t >= 5}
    
    print(f"\nRapporteurs with 5+ holdings: {len(active_rapporteurs)}")
    print("-" * 70)
    
    for rapporteur in sorted(active_rapporteurs, key=lambda r: -rapporteur_total[r]):
        total = rapporteur_total[rapporteur]
        print(f"\n{rapporteur} ({total} holdings):")
        
        # Sort concepts by count
        concepts = rapporteur_concepts[rapporteur]
        sorted_concepts = sorted(concepts.items(), key=lambda x: -x[1])
        
        for concept, count in sorted_concepts[:5]:  # Top 5 concepts
            pct = count / total * 100
            bar = "█" * int(pct / 5)
            print(f"  {concept:35} {count:3} ({pct:5.1f}%) {bar}")
    
    # Find potential specializations (rapporteurs with >40% in one concept)
    print("\n" + "-" * 70)
    print("POTENTIAL SPECIALIZATIONS (>40% in one concept, min 5 holdings):")
    print("-" * 70)
    
    specializations = []
    for rapporteur, total in active_rapporteurs.items():
        for concept, count in rapporteur_concepts[rapporteur].items():
            pct = count / total * 100
            if pct >= 40:
                specializations.append((rapporteur, concept, count, total, pct))
    
    if specializations:
        for rap, concept, count, total, pct in sorted(specializations, key=lambda x: -x[4]):
            print(f"  {rap}: {concept} ({count}/{total} = {pct:.1f}%)")
    else:
        print("  No strong specializations found (threshold: 40%)")
    
    return rapporteur_concepts, rapporteur_total


def analyze_rapporteur_directions(cases):
    """Hypothesis 2: Do rapporteurs lean pro-DS or pro-controller?"""
    # Count ruling directions per rapporteur
    rapporteur_directions = defaultdict(lambda: defaultdict(int))
    rapporteur_total = defaultdict(int)
    
    for case in cases:
        rapporteur = case.get('judge_rapporteur')
        if not rapporteur:
            continue
        for holding in case.get('holdings', []):
            direction = holding.get('ruling_direction', 'NEUTRAL_OR_UNCLEAR')
            rapporteur_directions[rapporteur][direction] += 1
            rapporteur_total[rapporteur] += 1
    
    print("\n" + "=" * 70)
    print("HYPOTHESIS 2: RAPPORTEUR RULING DIRECTION TENDENCIES")
    print("=" * 70)
    
    # Calculate bias score: (pro_ds - pro_controller) / total
    # Positive = pro-DS leaning, Negative = pro-controller leaning
    rapporteur_bias = {}
    
    for rapporteur, total in rapporteur_total.items():
        if total < 5:
            continue
        pro_ds = rapporteur_directions[rapporteur].get('PRO_DATA_SUBJECT', 0)
        pro_ctrl = rapporteur_directions[rapporteur].get('PRO_CONTROLLER', 0)
        mixed = rapporteur_directions[rapporteur].get('MIXED', 0)
        neutral = rapporteur_directions[rapporteur].get('NEUTRAL_OR_UNCLEAR', 0)
        
        # Bias score from -1 (all pro-controller) to +1 (all pro-DS)
        if pro_ds + pro_ctrl > 0:
            bias = (pro_ds - pro_ctrl) / (pro_ds + pro_ctrl)
        else:
            bias = 0
        
        rapporteur_bias[rapporteur] = {
            'total': total,
            'pro_ds': pro_ds,
            'pro_ctrl': pro_ctrl,
            'mixed': mixed,
            'neutral': neutral,
            'bias': bias,
            'pro_ds_pct': pro_ds / total * 100,
            'pro_ctrl_pct': pro_ctrl / total * 100,
        }
    
    # Sort by bias score
    sorted_rapporteurs = sorted(rapporteur_bias.items(), key=lambda x: -x[1]['bias'])
    
    print(f"\nRapporteurs with 5+ holdings: {len(sorted_rapporteurs)}")
    print("-" * 70)
    print(f"{'Rapporteur':<25} {'Total':>5} {'Pro-DS':>7} {'Pro-Ctrl':>9} {'Bias':>7}")
    print("-" * 70)
    
    for rapporteur, stats in sorted_rapporteurs:
        bias_bar = ""
        if stats['bias'] > 0:
            bias_bar = "+" * int(abs(stats['bias']) * 5)
        elif stats['bias'] < 0:
            bias_bar = "-" * int(abs(stats['bias']) * 5)
        
        print(f"{rapporteur:<25} {stats['total']:>5} "
              f"{stats['pro_ds']:>3} ({stats['pro_ds_pct']:>4.0f}%) "
              f"{stats['pro_ctrl']:>3} ({stats['pro_ctrl_pct']:>4.0f}%) "
              f"{stats['bias']:>+.2f} {bias_bar}")
    
    # Statistical summary
    print("\n" + "-" * 70)
    print("SUMMARY:")
    print("-" * 70)
    
    all_biases = [s['bias'] for s in rapporteur_bias.values()]
    avg_bias = sum(all_biases) / len(all_biases) if all_biases else 0
    
    pro_ds_leaning = sum(1 for b in all_biases if b > 0.2)
    pro_ctrl_leaning = sum(1 for b in all_biases if b < -0.2)
    neutral_leaning = len(all_biases) - pro_ds_leaning - pro_ctrl_leaning
    
    print(f"  Average bias score: {avg_bias:+.2f} (positive = pro-DS)")
    print(f"  Pro-DS leaning (bias > 0.2): {pro_ds_leaning} rapporteurs")
    print(f"  Pro-controller leaning (bias < -0.2): {pro_ctrl_leaning} rapporteurs")
    print(f"  Neutral (-0.2 to 0.2): {neutral_leaning} rapporteurs")
    
    return rapporteur_bias


def main():
    cases = load_data()
    print(f"Loaded {len(cases)} cases\n")
    
    analyze_rapporteur_topics(cases)
    analyze_rapporteur_directions(cases)
    
    print("\n" + "=" * 70)
    print("NOTE: This is exploratory analysis. Statistical significance testing")
    print("would be needed to confirm these patterns are not due to chance.")
    print("=" * 70)


if __name__ == '__main__':
    main()
