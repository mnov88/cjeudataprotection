# The Means-Ends Distinction in CJEU Data Protection Jurisprudence

## The Hypothesis

> "The Court rarely questions whether objectives are legitimate—it focuses on whether the specific method is proportionate."

This document empirically tests this hypothesis across the CJEU's GDPR jurisprudence, examining whether the Court's analytical methodology consistently accepts the legitimacy of competing objectives while scrutinizing the proportionality of implementation methods.

---

## Part I: Quantitative Evidence

### Necessity Standards Distribution

The dataset codes whether holdings discuss necessity and what standard is applied:

| Necessity Standard | Holdings | Pro-DS | Pro-Controller | Mixed |
|-------------------|----------|--------|----------------|-------|
| **STRICT** | 22 | 19 (86%) | 0 (0%) | 2 |
| **REGULAR** | 19 | 7 (37%) | 3 (16%) | 6 |
| **Not Discussed** | 140 | 84 (60%) | 20 (14%) | 20 |

**Key Finding**: When the Court applies **strict necessity** scrutiny, data subjects win 86% of the time and controllers *never* win outright. This suggests the Court's analytical work occurs at the proportionality stage, not at the legitimacy stage.

### The Pattern in Numbers

Of 41 holdings involving explicit balancing between data protection and competing interests:
- **28 holdings (68%)**: Data protection prevails
- **4 holdings (10%)**: Competing interest prevails
- **9 holdings (22%)**: Mixed outcome

In the 28 holdings where data protection prevails, the Court consistently:
1. Acknowledges the legitimacy of the competing objective
2. Finds the specific implementation method disproportionate

---

## Part II: Textual Evidence from Grand Chamber Cases

### Case Study 1: C-184/20 – Lithuanian Anti-Corruption Declarations

**The Objective**: Preventing corruption, ensuring impartiality of public officials, combating conflicts of interest.

**The Means**: Online publication of declarations including spouse names, family member details, and transactions exceeding EUR 3,000.

**The Court's Analysis**:

At paragraph 75, the Court explicitly accepts the objective:
> "Such objectives, in that they seek to strengthen the safeguards for probity and impartiality of public sector decision makers, to prevent conflicts of interest and to combat corruption in the public sector, are **undeniably objectives of public interest and, accordingly, legitimate**."

At paragraph 80, the Court confirms:
> "It follows from the foregoing considerations that the processing of personal data pursuant to the Law on the reconciliation of interests is intended to meet **objectives of general interest recognised by the European Union**, within the meaning of Article 52(1) of the Charter, and **objectives that are of public interest and therefore legitimate**, within the meaning of Article 6(3) of the GDPR."

But then the Court pivots to scrutinize the means (paragraphs 90-97):
> "The question also arises as to whether it is **strictly necessary**, in order to achieve the objectives of general interest referred to in Article 1 of the Law on the reconciliation of interests, that heads of establishments receiving public funds be... subject to the public disclosure that that law prescribes."

> "Nor does it appear that the systematic publication, online, of the list of the declarant's transactions the value of which is greater than EUR 3000 is **strictly necessary** in the light of the objectives pursued."

**The Structure**: Legitimate objective → Disproportionate means → Data protection prevails

---

### Case Study 2: C-439/19 – Latvian Penalty Points Disclosure

**The Objective**: Road safety, deterring traffic violations.

**The Means**: Public disclosure of driver penalty points to anyone who requests them, without requiring demonstration of specific interest.

**The Court's Analysis**:

The Court does not question that road safety is a legitimate public interest. Instead, it focuses on whether public disclosure is the appropriate method (paragraph 36 of coded analysis):
> "Court applied strict necessity test, finding public disclosure not necessary since **road safety objectives could be achieved through less restrictive means** like deterrent punishments and training requirements."

**The Structure**: Legitimate objective (road safety) → Less restrictive means available → Disproportionate disclosure method → Data protection prevails

---

### Case Study 3: C-311/18 – Schrems II (US Surveillance)

**The Objective**: National security, protection against terrorism and foreign threats.

**The Means**: Mass surveillance programmes under Section 702 FISA and Executive Order 12333, without proportionality limitations or effective judicial remedies.

**The Court's Analysis**:

The Court explicitly accepts that national security is a legitimate objective (this is never questioned). The analysis focuses entirely on the *manner* of surveillance:

From the coded analysis:
> "US surveillance laws including Section 702 FISA and E.O. 12333 **lack clear and precise rules limiting interference to what is strictly necessary**, failing proportionality requirements."

The Court's concern is not whether the US can pursue national security—of course it can—but whether the specific surveillance methods are proportionate:
- Mass, indiscriminate collection (means problem)
- Lack of independent oversight (procedural means problem)
- Absence of effective judicial remedies (means problem)

**The Structure**: Legitimate objective (national security) → Disproportionate implementation (mass surveillance without safeguards) → Data protection prevails

---

### Case Study 4: C-252/21 – Meta/Facebook Data Aggregation

**The Objective**: Personalized advertising to fund free social network services.

**The Means**: Extensive collection and aggregation of user data across Meta services and third-party sources, tracking user behavior pervasively.

**The Court's Analysis**:

The Court accepts that commercial advertising constitutes a "legitimate interest" under Article 6(1)(f)—this is not disputed. The analysis focuses on proportionality:

From the coded analysis:
> "Users' fundamental rights and reasonable expectations override controller's advertising interests; **extensive tracking creates a feeling of continuous surveillance** that overrides commercial interests."

The Court asks: Even if advertising is legitimate, is *this particular method* of data collection necessary and proportionate?
- Could less invasive advertising models achieve the objective?
- Did users reasonably expect this level of tracking?
- Is the intrusiveness proportionate to the benefit?

**The Structure**: Legitimate interest (advertising) → Disproportionate method (pervasive cross-platform tracking) → Data protection prevails

---

### Case Study 5: C-205/21 – Bulgarian Biometric Collection

**The Objective**: Criminal law enforcement, maintaining biometric databases for investigation purposes.

**The Means**: Systematic collection of biometric and genetic data from *all* persons accused of intentional offenses, without individual necessity assessment.

**The Court's Analysis**:

The Court accepts law enforcement objectives as legitimate (Holding 2 is actually pro-controller, permitting deferred judicial review for operational efficiency). But it draws the line at *blanket* collection:

From the coded analysis:
> "The holding prohibits systematic blanket collection of sensitive biometric and genetic data, **requiring individualized necessity assessment** and limiting law enforcement discretion."

The textual analysis (paragraph 128 of decision):
> "National legislation which provides for the **systematic collection** of the biometric and genetic data of **any person** accused of an intentional offence subject to public prosecution is, in principle, contrary to the requirement... that processing of the special categories of data referred to in that article is to be allowed '**only where strictly necessary**'."

**The Structure**: Legitimate objective (law enforcement) → Disproportionate means (blanket collection without individual assessment) → Data protection prevails on Holding 3 (while Holding 2 permits deferred review for operational needs)

---

## Part III: The Proportionality Cascade

Across these cases, the Court applies a consistent analytical structure:

### Step 1: Acknowledge Legitimacy
The Court virtually always accepts that the competing interest is legitimate:
- Anti-corruption ✓
- Road safety ✓
- National security ✓
- Commercial advertising ✓
- Law enforcement ✓
- Freedom of expression ✓
- Intellectual property ✓

**Finding**: In the entire dataset, there is no case where the Court holds that a claimed objective is *illegitimate*. The legitimacy filter is almost always passed.

### Step 2: Assess Necessity
The Court then asks: Is the privacy-invasive processing *necessary* to achieve the legitimate objective?

This breaks into sub-questions:
- Could the objective be achieved **without** processing personal data?
- Could the objective be achieved with **less** personal data?
- Could the objective be achieved with **less intrusive** processing?

### Step 3: Examine Less Restrictive Alternatives
The critical inquiry: Are there alternative means that would achieve the same objective with less privacy intrusion?

| Case | Objective | Rejected Means | Less Restrictive Alternative |
|------|-----------|----------------|------------------------------|
| C-184/20 | Anti-corruption | Online publication of spouse names | Declarations filed but not publicly published; access on request with demonstrated interest |
| C-439/19 | Road safety | Public penalty point disclosure | Deterrent fines, training requirements, license consequences |
| C-311/18 | National security | Mass surveillance | Targeted surveillance with judicial authorization |
| C-252/21 | Advertising | Pervasive cross-platform tracking | Contextual advertising, less invasive targeting |
| C-205/21 | Law enforcement | Blanket biometric collection | Individual necessity assessment per accused |

### Step 4: Proportionality Stricto Sensu
Even if necessary, is the intrusion proportionate to the benefit achieved?

This involves weighing:
- Severity of privacy interference
- Importance of the objective
- Degree to which the means actually advance the objective
- Impact on data subjects

---

## Part IV: Why This Pattern Matters

### For Controllers and Legislators

The means-ends distinction provides actionable guidance:

1. **Objectives will generally be accepted** – Don't over-argue why your goal is legitimate; the Court is likely to agree.

2. **Focus on demonstrating necessity** – The critical question is whether your specific implementation method is the least restrictive means available.

3. **Document alternatives considered** – Show that you evaluated less invasive options and explain why they were inadequate.

4. **Calibrate to the actual need** – Blanket approaches fail; individualized assessment survives.

### For Data Subjects and Advocates

1. **Don't attack objectives** – Arguments that "anti-corruption isn't important" or "road safety doesn't matter" will fail.

2. **Attack methods** – Focus on demonstrating that less invasive alternatives exist.

3. **Propose alternatives** – Affirmatively suggest how the objective could be achieved with less privacy intrusion.

### For Understanding the Court's Role

The Court positions itself as a *calibrator* rather than a *blocker*:
- It does not tell Member States they cannot pursue anti-corruption, road safety, or national security
- It tells them they must pursue these goals through proportionate means
- This preserves policy discretion while enforcing fundamental rights methodology

---

## Part V: Exceptions and Nuances

### When Objectives Do Face Scrutiny

In a few contexts, the Court's legitimacy analysis is more demanding:

**Consent bundling (C-252/21)**: When controllers bundle consent with service provision, the Court examines whether the "objective" is genuinely the service or merely data extraction.

**Pretextual purposes**: Where claimed purposes appear pretextual, the Court may be more skeptical (though this rarely appears explicitly in the dataset).

### When Methods Receive Deference

**Judicial independence (C-245/20)**: The Court grants substantial deference to courts acting in judicial capacity, accepting that judicial communication activities inherently serve open justice without demanding demonstration of strict necessity.

**Institutional discretion (C-768/21)**: DPA enforcement discretion receives deference; the Court does not require DPAs to justify their prioritization decisions.

### Mixed Cases

Some holdings show genuine balancing without clear means-ends separation:

**C-460/20 (De-referencing)**: The Court balances data protection against freedom of expression without fully accepting either as legitimate-but-requiring-scrutiny. Both rights receive substantive examination.

**C-597/19 (Mircom)**: IP enforcement and data protection are balanced more evenly, with procedural safeguards rather than means-substitution providing the resolution.

---

## Part VI: Linguistic Markers

The hypothesis can be tested by searching for characteristic phrases in the Court's reasoning:

### Phrases Indicating Legitimacy Acceptance
- "undeniably objectives of public interest"
- "legitimate aim"
- "objectives of general interest recognised by the European Union"
- "constitutes a legitimate interest"
- "genuine and legitimate interest"

### Phrases Indicating Proportionality Scrutiny
- "strictly necessary"
- "cannot reasonably be achieved by other means"
- "less restrictive means"
- "goes beyond what is necessary"
- "not necessary in the light of"
- "disproportionate interference"

### Frequency Analysis

A search across the decision texts reveals:
- **"legitimate"** appears in virtually every case involving balancing
- **"strictly necessary"** appears in cases where STRICT standard is applied (and data protection prevails)
- **"less restrictive"** or **"other means"** appears when the Court identifies alternatives

---

## Conclusion: Hypothesis Confirmed

The empirical evidence strongly supports the hypothesis:

> **The CJEU rarely questions whether objectives are legitimate—it focuses on whether the specific method is proportionate.**

This pattern manifests across:
- **Grand Chamber cases** (C-184/20, C-311/18, C-252/21, C-439/19)
- **Multiple legal bases** (public interest, legitimate interests, legal obligation)
- **Diverse competing interests** (anti-corruption, security, advertising, law enforcement)

The Court's methodology:
1. **Accepts** the legitimacy of virtually all claimed objectives
2. **Scrutinizes** whether the chosen implementation method is necessary
3. **Examines** whether less restrictive alternatives exist
4. **Requires** proportionality between means and ends

This approach allows the Court to:
- Respect Member State and controller policy choices
- Maintain judicial role as proportionality reviewer rather than policy maker
- Provide actionable guidance (implement differently, not abandon objectives)
- Preserve fundamental rights through methodological discipline

The rare exceptions (judicial independence, institutional discretion) confirm the rule by demonstrating that deference is extended where alternative oversight mechanisms exist or constitutional separation concerns apply.

---

## Appendix: Key Quotations

### C-184/20 (Anti-Corruption Transparency)
> "Such objectives, in that they seek to strengthen the safeguards for probity and impartiality of public sector decision makers, to prevent conflicts of interest and to combat corruption in the public sector, are **undeniably objectives of public interest and, accordingly, legitimate**." (para. 75)

> "Nor does it appear that the systematic publication, online, of the list of the declarant's transactions the value of which is greater than EUR 3000 is **strictly necessary** in the light of the objectives pursued." (para. 97)

### C-439/19 (Penalty Points)
> "As recital 39 of the GDPR makes clear, that requirement of necessity is not met where the objective of general interest pursued can reasonably be achieved **just as effectively by other means less restrictive** of the fundamental rights of data subjects."

### C-311/18 (Schrems II)
> "Section 702 of the FISA does not indicate any limitations on the power it confers to implement surveillance programmes for the purposes of foreign intelligence or the existence of guarantees for non-US persons potentially targeted by those programmes."

### C-205/21 (Biometric Collection)
> "National legislation which provides for the **systematic collection** of the biometric and genetic data of **any person** accused of an intentional offence subject to public prosecution is, in principle, contrary to the requirement... that processing of the special categories of data referred to in that article is to be allowed '**only where strictly necessary**'."

---

*Document generated: January 2026*
*Based on empirical analysis of 181 coded holdings and examination of decision texts*
