#!/usr/bin/env python3
"""
12_topic_focus_graphs.py
Topic Focus Visualizations for CJEU GDPR Holdings

Generates five publication-quality graphs:
1. Total holdings per topic cluster (horizontal bar chart)
2. Holdings by GDPR article number (top articles, horizontal bar)
3. Topic clusters over time (absolute + proportional stacked bars)
4. Article numbers over time (heatmap)
5. Primary concepts detail within clusters

Cluster scheme splits the old "Enforcement" into:
  - Compensation (REMEDIES_COMPENSATION only — Art. 82)
  - Supervision  (DPA_POWERS, DPA_OTHER, DPA_INDEPENDENCE, ONE_STOP_SHOP,
                   ADMINISTRATIVE_FINES, REPRESENTATIVE_ACTIONS)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import json
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_PATH = '/home/user/cjeudataprotection/analysis/output/holdings_prepared.csv'
CLUSTER_PATH = '/home/user/cjeudataprotection/analysis/output/concept_cluster_info.json'
OUT_DIR = '/home/user/cjeudataprotection/analysis/output/topic_focus'
os.makedirs(OUT_DIR, exist_ok=True)

# --- New 9-cluster mapping (concept → cluster) ---
# Splits the old ENFORCEMENT into COMPENSATION and SUPERVISION
CONCEPT_TO_CLUSTER = {
    # Scope
    'SCOPE_MATERIAL': 'Scope', 'SCOPE_TERRITORIAL': 'Scope',
    'PERSONAL_DATA_SCOPE': 'Scope', 'HOUSEHOLD_EXEMPTION': 'Scope',
    'OTHER_EXEMPTION': 'Scope',
    # Actors
    'CONTROLLER_DEFINITION': 'Actors', 'JOINT_CONTROLLERS_DEFINITION': 'Actors',
    'PROCESSOR_OBLIGATIONS': 'Actors', 'RECIPIENT_DEFINITION': 'Actors',
    # Lawfulness
    'CONSENT_BASIS': 'Lawfulness', 'CONTRACT_BASIS': 'Lawfulness',
    'LEGAL_OBLIGATION_BASIS': 'Lawfulness', 'VITAL_INTERESTS_BASIS': 'Lawfulness',
    'PUBLIC_INTEREST_BASIS': 'Lawfulness', 'LEGITIMATE_INTERESTS': 'Lawfulness',
    # Principles
    'DATA_PROTECTION_PRINCIPLES': 'Principles', 'ACCOUNTABILITY': 'Principles',
    'TRANSPARENCY': 'Principles', 'DATA_MINIMISATION': 'Principles',
    # Rights
    'RIGHT_OF_ACCESS': 'Rights', 'RIGHT_TO_RECTIFICATION': 'Rights',
    'RIGHT_TO_ERASURE': 'Rights', 'RIGHT_TO_RESTRICTION': 'Rights',
    'RIGHT_TO_PORTABILITY': 'Rights', 'RIGHT_TO_OBJECT': 'Rights',
    'AUTOMATED_DECISION_MAKING': 'Rights',
    # Special Categories
    'SPECIAL_CATEGORIES_DEFINITION': 'Special Categories',
    'SPECIAL_CATEGORIES_CONDITIONS': 'Special Categories',
    # Compensation (new — split from Enforcement)
    'REMEDIES_COMPENSATION': 'Compensation',
    # Supervision (new — remaining Enforcement concepts)
    'DPA_INDEPENDENCE': 'Supervision', 'DPA_POWERS': 'Supervision',
    'DPA_OBLIGATIONS': 'Supervision', 'ONE_STOP_SHOP': 'Supervision',
    'DPA_OTHER': 'Supervision', 'ADMINISTRATIVE_FINES': 'Supervision',
    'REPRESENTATIVE_ACTIONS': 'Supervision',
    # Other
    'SECURITY': 'Other', 'INTERNATIONAL_TRANSFER': 'Other',
    'OTHER_CONTROLLER_OBLIGATIONS': 'Other',
    'MEMBER_STATE_DISCRETION': 'Other', 'OTHER': 'Other',
}

# Color palette — each cluster distinct, accessible
CLUSTER_COLORS = {
    'Compensation':       '#B03A2E',   # dark red
    'Supervision':        '#2E5A88',   # deep blue
    'Rights':             '#C44E52',   # muted red
    'Other':              '#8C8C8C',   # neutral grey
    'Principles':         '#DD8452',   # warm orange
    'Lawfulness':         '#4C72B0',   # steel blue
    'Scope':              '#55A868',   # forest green
    'Special Categories': '#8172B3',   # muted purple
    'Actors':             '#CCB974',   # gold
}

# Display order (descending by expected count)
CLUSTER_ORDER = [
    'Compensation', 'Supervision', 'Rights', 'Other', 'Principles',
    'Lawfulness', 'Scope', 'Special Categories', 'Actors'
]


def style_axes(ax, title, xlabel=None, ylabel=None, grid_axis='x'):
    """Apply consistent academic styling to axes."""
    ax.set_title(title, fontsize=14, fontweight='bold', pad=14, loc='left',
                 fontfamily='Liberation Serif')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11, labelpad=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.6)
    ax.spines['bottom'].set_linewidth(0.6)
    if grid_axis:
        ax.grid(axis=grid_axis, linestyle='--', alpha=0.3, linewidth=0.5)
    ax.tick_params(labelsize=10)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH)
with open(CLUSTER_PATH) as f:
    cluster_info = json.load(f)

# Apply the new cluster mapping
df['cluster'] = df['primary_concept'].map(CONCEPT_TO_CLUSTER)
# Fallback for any unmapped concepts
df['cluster'] = df['cluster'].fillna('Other')

# Parse article_numbers (semicolon-separated in raw data)
def parse_articles(val):
    if pd.isna(val):
        return []
    return [int(x.strip()) for x in str(val).split(';') if x.strip().isdigit()]

df['articles_list'] = df['article_numbers'].apply(parse_articles)

print(f"Loaded {len(df)} holdings across {df['case_id'].nunique()} cases")
print(f"Year range: {df['year'].min()}-{df['year'].max()}")
print(f"\nCluster distribution (new 9-cluster scheme):")
for c in CLUSTER_ORDER:
    n = (df['cluster'] == c).sum()
    print(f"  {c:22s} {n:3d}  ({n/len(df)*100:4.1f}%)")

total = len(df)


# ============================================================================
# GRAPH 1: Total Holdings per Topic Cluster
# ============================================================================
print("\n--- Graph 1: Holdings per Topic Cluster ---")

cluster_counts = df['cluster'].value_counts()
cluster_counts = cluster_counts.reindex(CLUSTER_ORDER).fillna(0).astype(int)
cluster_counts = cluster_counts.sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 6))

colors = [CLUSTER_COLORS.get(c, '#999999') for c in cluster_counts.index]
bars = ax.barh(cluster_counts.index, cluster_counts.values, color=colors,
               height=0.65, edgecolor='white', linewidth=0.5)

for i, (bar, val) in enumerate(zip(bars, cluster_counts.values)):
    y_center = bar.get_y() + bar.get_height() / 2
    if val > 10:
        ax.text(val - 1.5, y_center, str(val),
                ha='right', va='center', fontsize=11,
                fontweight='bold', color='white')
    else:
        ax.text(val + 0.8, y_center, str(val),
                ha='left', va='center', fontsize=11,
                fontweight='bold', color=colors[i])
    pct = val / total * 100
    ax.text(val + 2.5, y_center, f'({pct:.0f}%)',
            ha='left', va='center', fontsize=9,
            color='#555555', style='italic')

style_axes(ax, 'Topic Focus in CJEU GDPR Holdings',
           xlabel='Number of Holdings', grid_axis='x')
ax.set_xlim(0, cluster_counts.max() + 12)

fig.text(0.98, 0.02, f'N = {total} holdings', ha='right', va='bottom',
         fontsize=8.5, color='#888888', style='italic')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'topic_cluster_totals.png'),
            dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(os.path.join(OUT_DIR, 'topic_cluster_totals.pdf'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved topic_cluster_totals.png/.pdf")


# ============================================================================
# GRAPH 2: Holdings by Article Number (Top 18)
# ============================================================================
print("\n--- Graph 2: Holdings by Article Number ---")

articles_exploded = df.explode('articles_list')
articles_exploded = articles_exploded.dropna(subset=['articles_list'])
articles_exploded['article'] = articles_exploded['articles_list'].astype(int)

article_counts = articles_exploded['article'].value_counts()
top_articles = article_counts.head(18).sort_values(ascending=True)

# Map articles to GDPR chapters for coloring
GDPR_CHAPTER = {}
for a in range(1, 5):    GDPR_CHAPTER[a] = 'General (Ch. I)'
for a in range(5, 12):   GDPR_CHAPTER[a] = 'Principles (Ch. II)'
for a in range(12, 24):  GDPR_CHAPTER[a] = 'DS Rights (Ch. III)'
for a in range(24, 44):  GDPR_CHAPTER[a] = 'Controller (Ch. IV)'
for a in range(44, 50):  GDPR_CHAPTER[a] = 'Transfer (Ch. V)'
for a in range(51, 77):  GDPR_CHAPTER[a] = 'DPAs (Ch. VI–VII)'
for a in range(77, 85):  GDPR_CHAPTER[a] = 'Remedies (Ch. VIII)'
for a in range(85, 100): GDPR_CHAPTER[a] = 'Specific (Ch. IX)'
GDPR_CHAPTER[95] = 'Specific (Ch. IX)'

CHAPTER_COLORS = {
    'General (Ch. I)':     '#8C8C8C',
    'Principles (Ch. II)': '#55A868',
    'DS Rights (Ch. III)': '#C44E52',
    'Controller (Ch. IV)': '#DD8452',
    'Transfer (Ch. V)':    '#8172B3',
    'DPAs (Ch. VI–VII)':   '#4C72B0',
    'Remedies (Ch. VIII)': '#2E5A88',
    'Specific (Ch. IX)':   '#CCB974',
}

fig, ax = plt.subplots(figsize=(9, 7))

art_colors = [CHAPTER_COLORS.get(GDPR_CHAPTER.get(a, ''), '#999999')
              for a in top_articles.index]
labels = [f'Art. {a}' for a in top_articles.index]

bars = ax.barh(labels, top_articles.values, color=art_colors,
               height=0.65, edgecolor='white', linewidth=0.5)

for bar, val in zip(bars, top_articles.values):
    if val > 8:
        ax.text(val - 1, bar.get_y() + bar.get_height() / 2,
                str(val), ha='right', va='center',
                fontsize=10.5, fontweight='bold', color='white')
    else:
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                str(val), ha='left', va='center',
                fontsize=10.5, fontweight='bold', color='#444444')

style_axes(ax, 'Most Frequently Cited GDPR Articles in Holdings',
           xlabel='Number of Holdings Citing Article', grid_axis='x')
ax.set_xlim(0, top_articles.max() + 10)

unique_chapters = []
seen = set()
for a in top_articles.index:
    ch = GDPR_CHAPTER.get(a, '')
    if ch and ch not in seen:
        unique_chapters.append(ch)
        seen.add(ch)

legend_elements = [Patch(facecolor=CHAPTER_COLORS[ch], edgecolor='white',
                         label=ch) for ch in unique_chapters]
ax.legend(handles=legend_elements, loc='lower right', fontsize=8.5,
          framealpha=0.9, edgecolor='#cccccc', title='GDPR Chapter',
          title_fontsize=9)

fig.text(0.98, -0.01, f'N = {total} holdings (articles may appear multiple times)',
         ha='right', va='top', fontsize=8.5, color='#888888', style='italic')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'article_number_totals.png'),
            dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(os.path.join(OUT_DIR, 'article_number_totals.pdf'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved article_number_totals.png/.pdf")


# ============================================================================
# GRAPH 3: Topic Clusters Over Time (Stacked Bars)
# ============================================================================
print("\n--- Graph 3: Topic Clusters Over Time ---")

ct = pd.crosstab(df['year'], df['cluster'])
for c in CLUSTER_ORDER:
    if c not in ct.columns:
        ct[c] = 0
ct = ct[CLUSTER_ORDER]

years = ct.index.values

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6),
                                gridspec_kw={'width_ratios': [1.1, 1]})

# --- Left: absolute stacked bar ---
bottom = np.zeros(len(years))
for cluster in CLUSTER_ORDER:
    vals = ct[cluster].values
    ax1.bar(years, vals, bottom=bottom, color=CLUSTER_COLORS[cluster],
            label=cluster, width=0.7, edgecolor='white', linewidth=0.4)
    bottom += vals

style_axes(ax1, 'Topic Clusters Over Time (Absolute)',
           xlabel='Year', ylabel='Number of Holdings', grid_axis='y')
ax1.set_xticks(years)
ax1.set_xticklabels(years, rotation=0)
ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# --- Right: 100% stacked bar ---
ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

bottom_pct = np.zeros(len(years))
for cluster in CLUSTER_ORDER:
    vals = ct_pct[cluster].values
    ax2.bar(years, vals, bottom=bottom_pct, color=CLUSTER_COLORS[cluster],
            label=cluster, width=0.7, edgecolor='white', linewidth=0.4)
    bottom_pct += vals

style_axes(ax2, 'Topic Clusters Over Time (Proportional)',
           xlabel='Year', ylabel='Share of Holdings (%)', grid_axis='y')
ax2.set_xticks(years)
ax2.set_xticklabels(years, rotation=0)
ax2.set_ylim(0, 100)
ax2.yaxis.set_major_formatter(mticker.PercentFormatter())

# Shared legend below
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=5, fontsize=9,
           framealpha=0.95, edgecolor='#cccccc',
           bbox_to_anchor=(0.5, -0.02))

fig.text(0.98, 0.01, f'N = {total} holdings',
         ha='right', va='bottom', fontsize=8.5, color='#888888', style='italic')

plt.tight_layout(rect=[0, 0.08, 1, 1])
fig.savefig(os.path.join(OUT_DIR, 'topic_clusters_over_time.png'),
            dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(os.path.join(OUT_DIR, 'topic_clusters_over_time.pdf'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved topic_clusters_over_time.png/.pdf")


# ============================================================================
# GRAPH 4: Article Numbers Over Time (Heatmap)
# ============================================================================
print("\n--- Graph 4: Article Numbers Over Time ---")

top_art_list = article_counts.head(15).index.tolist()

art_year = articles_exploded[articles_exploded['article'].isin(top_art_list)].reset_index(drop=True)
art_year_ct = pd.crosstab(art_year['article'], art_year['year'])

art_year_ct['_total'] = art_year_ct.sum(axis=1)
art_year_ct = art_year_ct.sort_values('_total', ascending=True)
art_year_ct = art_year_ct.drop(columns=['_total'])

for y in years:
    if y not in art_year_ct.columns:
        art_year_ct[y] = 0
art_year_ct = art_year_ct[sorted(art_year_ct.columns)]

fig, ax = plt.subplots(figsize=(10, 7))

cmap = LinearSegmentedColormap.from_list('custom_blues',
    ['#FFFFFF', '#D6E8F7', '#8BBDE0', '#4C8DC4', '#2E5A88', '#1A3657'])

sns.heatmap(art_year_ct, annot=True, fmt='d', cmap=cmap,
            linewidths=1.2, linecolor='white',
            cbar_kws={'label': 'Number of Holdings', 'shrink': 0.75},
            ax=ax, vmin=0,
            annot_kws={'fontsize': 11, 'fontweight': 'bold'})

ax.set_yticklabels([f'Art. {int(a.get_text())}' for a in ax.get_yticklabels()],
                   rotation=0, fontsize=10)
ax.set_xticklabels([str(int(float(x.get_text()))) for x in ax.get_xticklabels()],
                   rotation=0, fontsize=10)

style_axes(ax, 'Most Cited GDPR Articles Over Time',
           xlabel='Year', ylabel='', grid_axis=None)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

fig.text(0.98, 0.01, f'Top 15 articles by total citation count',
         ha='right', va='bottom', fontsize=8.5, color='#888888', style='italic')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'articles_over_time_heatmap.png'),
            dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(os.path.join(OUT_DIR, 'articles_over_time_heatmap.pdf'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved articles_over_time_heatmap.png/.pdf")


# ============================================================================
# GRAPH 5: Detailed Topic Breakdown within Clusters
# ============================================================================
print("\n--- Graph 5: Primary Concepts within Clusters ---")

df['concept_pretty'] = df['primary_concept'].str.replace('_', ' ').str.title()

concept_counts = df.groupby(['cluster', 'concept_pretty']).size().reset_index(name='count')
concept_counts = concept_counts.sort_values(['cluster', 'count'], ascending=[True, False])

# Filter to concepts with at least 2 holdings
concept_counts = concept_counts[concept_counts['count'] >= 2]
concept_counts = concept_counts.sort_values('count', ascending=True)

fig, ax = plt.subplots(figsize=(10, 9))

colors = [CLUSTER_COLORS.get(c, '#999999') for c in concept_counts['cluster']]
bars = ax.barh(concept_counts['concept_pretty'], concept_counts['count'],
               color=colors, height=0.65, edgecolor='white', linewidth=0.5)

for bar, val in zip(bars, concept_counts['count'].values):
    if val > 5:
        ax.text(val - 0.8, bar.get_y() + bar.get_height() / 2,
                str(val), ha='right', va='center',
                fontsize=9.5, fontweight='bold', color='white')
    else:
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                str(val), ha='left', va='center',
                fontsize=9.5, fontweight='bold', color='#444444')

style_axes(ax, 'Primary Concepts in CJEU GDPR Holdings (n \u2265 2)',
           xlabel='Number of Holdings', grid_axis='x')
ax.set_xlim(0, concept_counts['count'].max() + 6)

legend_elements = [Patch(facecolor=CLUSTER_COLORS[c], edgecolor='white',
                         label=c) for c in CLUSTER_ORDER]
ax.legend(handles=legend_elements, loc='lower right', fontsize=8.5,
          framealpha=0.9, edgecolor='#cccccc', title='Topic Cluster',
          title_fontsize=9)

fig.text(0.98, 0.01, f'N = {total} holdings; concepts with < 2 holdings omitted',
         ha='right', va='bottom', fontsize=8.5, color='#888888', style='italic')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'primary_concepts_detail.png'),
            dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(os.path.join(OUT_DIR, 'primary_concepts_detail.pdf'),
            bbox_inches='tight', facecolor='white')
plt.close()
print("  Saved primary_concepts_detail.png/.pdf")


print(f"\n{'=' * 60}")
print(f"All graphs saved to {OUT_DIR}/")
print(f"{'=' * 60}")
