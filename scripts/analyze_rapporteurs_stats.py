#!/usr/bin/env python3
"""
Statistical analysis of rapporteur patterns using chi-squared tests.
"""

import json
from collections import defaultdict
from pathlib import Path

def load_data():
    with open(Path(__file__).parent.parent / 'parsed-coded' / 'cases.json') as f:
        return json.load(f)


def chi_squared_test(observed, expected):
    """Simple chi-squared test without scipy."""
    chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
    return chi2


def analyze_direction_significance(cases):
    """Test if rapporteur direction differences are significant."""
    print("=" * 70)
    print("STATISTICAL ANALYSIS: RULING DIRECTION BY RAPPORTEUR")
    print("=" * 70)
    
    # Collect data
    rapporteur_dirs = defaultdict(lambda: {'PRO_DATA_SUBJECT': 0, 'PRO_CONTROLLER': 0, 'OTHER': 0})
    
    for case in cases:
        rap = case.get('judge_rapporteur')
        if not rap:
            continue
        for h in case.get('holdings', []):
            direction = h.get('ruling_direction', 'NEUTRAL_OR_UNCLEAR')
            if direction == 'PRO_DATA_SUBJECT':
                rapporteur_dirs[rap]['PRO_DATA_SUBJECT'] += 1
            elif direction == 'PRO_CONTROLLER':
                rapporteur_dirs[rap]['PRO_CONTROLLER'] += 1
            else:
                rapporteur_dirs[rap]['OTHER'] += 1
    
    # Filter to rapporteurs with enough data
    active = {r: d for r, d in rapporteur_dirs.items() 
              if sum(d.values()) >= 5 and (d['PRO_DATA_SUBJECT'] + d['PRO_CONTROLLER']) >= 3}
    
    # Calculate overall rates
    total_ds = sum(d['PRO_DATA_SUBJECT'] for d in active.values())
    total_ctrl = sum(d['PRO_CONTROLLER'] for d in active.values())
    total = total_ds + total_ctrl
    
    expected_ds_rate = total_ds / total if total > 0 else 0.5
    expected_ctrl_rate = total_ctrl / total if total > 0 else 0.5
    
    print(f"\nOverall rates (baseline):")
    print(f"  Pro-DS: {total_ds}/{total} = {expected_ds_rate:.1%}")
    print(f"  Pro-Controller: {total_ctrl}/{total} = {expected_ctrl_rate:.1%}")
    
    print(f"\n{'Rapporteur':<20} {'Obs DS':>7} {'Exp DS':>7} {'Obs Ctrl':>9} {'Exp Ctrl':>9} {'Chi2':>8} {'Sig?':>6}")
    print("-" * 70)
    
    # Chi-squared critical value for df=1, p=0.05 is ~3.84
    # For p=0.01 is ~6.63
    chi_critical_05 = 3.84
    chi_critical_01 = 6.63
    
    results = []
    for rap, dirs in sorted(active.items(), key=lambda x: -sum(x[1].values())):
        obs_ds = dirs['PRO_DATA_SUBJECT']
        obs_ctrl = dirs['PRO_CONTROLLER']
        total_rap = obs_ds + obs_ctrl
        
        exp_ds = total_rap * expected_ds_rate
        exp_ctrl = total_rap * expected_ctrl_rate
        
        chi2 = chi_squared_test([obs_ds, obs_ctrl], [exp_ds, exp_ctrl])
        
        sig = ""
        if chi2 > chi_critical_01:
            sig = "**"  # p < 0.01
        elif chi2 > chi_critical_05:
            sig = "*"   # p < 0.05
        
        results.append((rap, obs_ds, exp_ds, obs_ctrl, exp_ctrl, chi2, sig))
        print(f"{rap:<20} {obs_ds:>7} {exp_ds:>7.1f} {obs_ctrl:>9} {exp_ctrl:>9.1f} {chi2:>8.2f} {sig:>6}")
    
    print("-" * 70)
    print("* = p < 0.05, ** = p < 0.01 (chi-squared test, df=1)")
    
    # Identify significant deviations
    sig_rapporteurs = [(r, chi2, sig) for r, _, _, _, _, chi2, sig in results if sig]
    if sig_rapporteurs:
        print(f"\n{len(sig_rapporteurs)} rapporteur(s) show statistically significant deviation:")
        for rap, chi2, sig in sig_rapporteurs:
            direction = "MORE pro-DS" if active[rap]['PRO_DATA_SUBJECT'] > active[rap]['PRO_CONTROLLER'] * expected_ds_rate / expected_ctrl_rate else "MORE pro-controller"
            print(f"  - {rap}: {direction} than expected ({sig})")
    else:
        print("\nNo rapporteurs show statistically significant deviation from the baseline.")


def analyze_topic_concentration(cases):
    """Test if rapporteurs specialize in topics more than expected by chance."""
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS: TOPIC SPECIALIZATION")
    print("=" * 70)
    
    # Collect data
    rapporteur_topics = defaultdict(lambda: defaultdict(int))
    topic_totals = defaultdict(int)
    
    for case in cases:
        rap = case.get('judge_rapporteur')
        if not rap:
            continue
        for h in case.get('holdings', []):
            concept = h.get('primary_concept', 'OTHER')
            rapporteur_topics[rap][concept] += 1
            topic_totals[concept] += 1
    
    # Filter active rapporteurs
    active = {r: dict(t) for r, t in rapporteur_topics.items() if sum(t.values()) >= 5}
    
    total_holdings = sum(topic_totals.values())
    
    print(f"\nTesting concentration vs expected distribution...")
    print(f"(Expected = if holdings were randomly distributed among rapporteurs)\n")
    
    # For each rapporteur, check if any topic is significantly overrepresented
    print(f"{'Rapporteur':<20} {'Top Topic':<30} {'Obs':>5} {'Exp':>6} {'Ratio':>6} {'Sig?':>6}")
    print("-" * 80)
    
    specializations = []
    for rap in sorted(active, key=lambda r: -sum(active[r].values())):
        topics = active[rap]
        rap_total = sum(topics.values())
        
        # Find most concentrated topic
        top_topic = max(topics, key=topics.get)
        obs = topics[top_topic]
        
        # Expected if this rapporteur had same topic distribution as overall
        exp = rap_total * (topic_totals[top_topic] / total_holdings)
        ratio = obs / exp if exp > 0 else 0
        
        # Simple test: is observed > 2x expected?
        sig = ""
        if obs >= 5 and ratio >= 2.5:
            sig = "**"
        elif obs >= 3 and ratio >= 2.0:
            sig = "*"
        
        print(f"{rap:<20} {top_topic:<30} {obs:>5} {exp:>6.1f} {ratio:>5.1f}x {sig:>6}")
        
        if sig:
            specializations.append((rap, top_topic, obs, exp, ratio))
    
    print("-" * 80)
    print("* = ratio >= 2x, ** = ratio >= 2.5x with sufficient observations")
    
    if specializations:
        print(f"\n{len(specializations)} potential specialization(s) found:")
        for rap, topic, obs, exp, ratio in specializations:
            print(f"  - {rap}: {topic}")
            print(f"    ({obs} holdings vs {exp:.1f} expected = {ratio:.1f}x concentration)")


def main():
    cases = load_data()
    print(f"Analyzing {len(cases)} cases...\n")
    
    analyze_direction_significance(cases)
    analyze_topic_concentration(cases)
    
    print("\n" + "=" * 70)
    print("CAVEATS:")
    print("- Small sample sizes limit statistical power")
    print("- Case assignment may not be random (confounding factors)")
    print("- Multiple testing increases false positive risk")
    print("=" * 70)


if __name__ == '__main__':
    main()
