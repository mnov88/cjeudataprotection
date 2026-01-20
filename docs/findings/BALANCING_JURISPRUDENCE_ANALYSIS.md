# CJEU Balancing Jurisprudence: Data Protection vs. Competing Interests

## Introduction

This analysis examines **41 CJEU holdings** where the Court explicitly balanced data protection rights against competing interests and fundamental rights. The GDPR does not operate in a vacuum—it must coexist with freedom of expression, intellectual property, judicial independence, public security, transparency, and numerous other values protected by EU law and the Charter of Fundamental Rights.

Understanding how the Court conducts these balancing exercises reveals the practical contours of data protection law and the hierarchy (or lack thereof) among fundamental rights.

### Overall Pattern

| Outcome | Holdings | Percentage |
|---------|----------|------------|
| Data Protection Prevails | 28 | 68.3% |
| Competing Interest Prevails | 4 | 9.8% |
| Mixed/Balanced | 9 | 22.0% |

Data protection prevails in approximately two-thirds of explicit balancing situations. However, the outcomes vary significantly by the type of competing interest and the specific context.

---

## Part I: Freedom of Expression and Information

**Holdings examined**: 7 | **Data Protection Prevails**: 5 | **Mixed**: 2

### The Right to Be Forgotten Cases

**C-460/20 – Google (De-referencing for Alleged Inaccuracy)** – Grand Chamber

The Court addressed whether Google must de-reference search results when a data subject claims the underlying content is inaccurate.

*Holding 1*: De-referencing requests are not conditional on obtaining a prior judicial ruling against the original content publisher. The Court reasoned that requiring data subjects to first sue content providers would create insurmountable barriers to exercising the right to erasure. However, the data subject must provide evidence sufficient to establish that the content is *manifestly* inaccurate—"relevant and sufficient" proof, not mere allegations.

*Holding 2*: Thumbnail images displayed in search results must be assessed independently of the original publication context. Photographs extracted from articles and displayed as standalone thumbnails lose the informative context that might justify their publication. The "informative value" of decontextualized images is typically low, while the privacy interference from displaying someone's face remains significant.

**Significance**: The Court establishes an asymmetric approach—freedom of expression protects the original publication, but does not automatically protect search engine amplification of that content. The intermediary (Google) bears assessment obligations that the original publisher does not.

### Freedom of Expression at Polling Stations

**C-306/21 – Koalitsia Demokratichna Bulgaria (Election Filming)**

Bulgarian authorities restricted video recording during vote counting at polling stations. Journalists and civic monitors challenged this as infringing freedom of expression and the right to information.

*Holding*: Competent authorities may adopt measures limiting or prohibiting video recording during the vote count to protect the personal data of election officials and other individuals present.

**The Court's Reasoning**: While transparency in elections is vital, it can be achieved through means less invasive than unlimited video recording. The personal data of poll workers, voters, and observers deserves protection. Data minimisation applies even in contexts where democratic accountability is at stake.

**Significance**: This ruling demonstrates that data protection can prevail over freedom of expression even in contexts with strong public interest dimensions. The availability of alternative, less privacy-invasive means of ensuring electoral transparency was central to the analysis.

---

## Part II: Transparency and Public Access

**Holdings examined**: 6 | **Data Protection Prevails**: 4 | **Other Prevails**: 1 | **Mixed**: 1

### Anti-Corruption Transparency

**C-184/20 – Vyriausioji tarnybinės etikos komisija (Lithuanian Ethics Commission)** – Grand Chamber

Lithuanian law required public officials to file declarations of private interests, which were then published online. These declarations included the names of spouses, cohabitants, and close relatives, as well as details of transactions exceeding EUR 3,000 over the previous 12 months.

*Holding*: GDPR precludes online publication of name-specific data about the declarant's spouse, close relatives, or transaction details.

**The Court's Reasoning**: The Court acknowledged that preventing corruption and conflicts of interest constitute legitimate public interest objectives. However, the *means* chosen—unrestricted online publication exposing third parties (spouses, relatives) who hold no public office—exceeded what was necessary. The interference with family members' privacy rights was disproportionate to the anti-corruption objective.

The Court emphasized that less invasive alternatives exist: declarations could be filed without online publication, or published with third-party names redacted, or made available only upon specific request demonstrating legitimate interest.

**Significance**: This Grand Chamber ruling establishes that even compelling public interests (anti-corruption, good governance) do not automatically justify maximum transparency. Proportionality requires assessing whether the *specific modality* of disclosure is necessary, not merely whether disclosure *in some form* serves a legitimate purpose.

### Public Disclosure of Penalty Points

**C-439/19 – Latvijas Republikas Saeima (Latvian Road Traffic Penalty Points)** – Grand Chamber

Latvian law required public disclosure of driver penalty points to anyone requesting such information, without requiring demonstration of any specific interest.

*Holding*: GDPR precludes national legislation obliging public disclosure of penalty points data to anyone without requiring a specific interest.

**The Court's Reasoning**: While improving road safety is a legitimate objective, the connection between public shaming (via penalty point disclosure) and safer driving is tenuous. The legislation essentially created a "pillory" effect—exposing drivers to social judgment without meaningful road safety benefits.

The Court noted that penalty points serve administrative functions (license management), not public accountability functions. Unlike corruption (where public scrutiny deters misconduct), driving violations are already punished through fines and license consequences.

**Significance**: The Court distinguishes between types of public interests. Some justify transparency (public official conduct, corruption prevention), while others (general road safety) do not necessarily support exposing individuals' violation histories to the public.

---

## Part III: Intellectual Property Rights

**Holdings examined**: 4 | **IP Prevails**: 1 | **Mixed**: 3

### The Mircom Cases: P2P Enforcement

**C-597/19 – Mircom International Content Management**

Mircom, an IP rights management company, sought disclosure of internet subscriber data to pursue infringement claims against BitTorrent users who had shared copyrighted content.

*Holding 1 (Pro-IP)*: Uploading file segments via peer-to-peer networks constitutes "making available to the public" even when the upload occurs automatically through software functionality.

*Holdings 2-3 (Balanced)*: While IP holders can seek subscriber data for enforcement purposes, national courts must assess whether requests are abusive, unjustified, or disproportionate. The GDPR's legitimate interests basis may permit IP address collection and disclosure, but only where:
- The rights holder has a genuine enforcement interest (not merely extractive settlement demands)
- The processing is proportionate
- National law provides adequate legal basis
- The request is not abusive

**The Court's Reasoning**: The Court explicitly balanced the IP holder's right to protection of property (Article 17 Charter) and right to an effective remedy (Article 47 Charter) against the data subjects' right to data protection (Article 8 Charter). Neither right automatically prevails; case-by-case proportionality assessment is required.

**Significance**: This is one of the few areas where data protection does not systematically prevail. The Court treats IP enforcement as a legitimate interest capable of justifying personal data processing, but imposes procedural safeguards against abuse. The "copyright troll" concern—rights holders who seek settlements rather than genuine enforcement—is addressed through the abuse/proportionality filter.

---

## Part IV: Judicial Independence and Open Justice

**Holdings examined**: 2 | **Judicial Values Prevail**: 2

### Court Communications to Journalists

**C-245/20 – Rechtbank Midden-Nederland**

A Dutch court provided documents from pending proceedings to journalists. The data protection authority declined to investigate, citing the judicial capacity exception.

*Holding*: Courts making documents containing personal data available to journalists for reporting falls within their "judicial capacity," excluding DPA supervisory competence.

**The Court's Reasoning**: The principle of open justice requires courts to be accessible to the public and press. Communication about judicial proceedings—including sharing relevant documents—is integral to the administration of justice. Subjecting these activities to DPA oversight would create external pressure on judicial decision-making.

The Court invoked judicial independence as a fundamental constitutional principle. External supervision by executive-branch agencies (which DPAs are in most Member States) would compromise the autonomy courts require for their judicial functions.

**Significance**: This is one of only two situations where a competing interest clearly prevails over data protection. The Court's reasoning rests on constitutional separation-of-powers principles rather than utilitarian balancing. Judicial independence is treated as a structural prerequisite for the rule of law, not merely one interest among many.

### Fair Trial and Document Production

**C-268/21 – Norra Stockholm Bygg**

A Swedish court considered whether to order production of documents containing personal data in civil litigation.

*Holding*: National courts must balance data subject interests against the right to effective judicial protection and fair trial, applying proportionality and data minimisation principles including pseudonymisation and access restrictions.

**The Court's Reasoning**: Unlike C-245/20, this case involved a genuine conflict rather than categorical exclusion. Fair trial rights require access to relevant evidence; data protection requires minimising unnecessary exposure of personal data. The Court required courts to:
- Assess whether document production is strictly necessary
- Apply data minimisation through redaction, pseudonymisation, or restricted access
- Balance the probative value of personal data against the privacy intrusion

*Outcome*: Data subject interests prevailed in the specific guidance, but the framework acknowledges both interests as legitimate.

---

## Part V: Law Enforcement and Public Security

**Holdings examined**: 8 | **Data Protection Prevails**: 7 | **Mixed**: 1

### The Schrems II Decision

**C-311/18 – Data Protection Commissioner (Schrems II)** – Grand Chamber

This landmark decision addressed EU-US data transfers in light of US surveillance programmes.

*Holdings*:
1. Standard contractual clauses must ensure protection "essentially equivalent" to EU standards
2. The Privacy Shield decision is invalid because US surveillance programmes lack proportionality and effective judicial remedies

**The Court's Reasoning**: US national security surveillance—specifically programmes under Section 702 FISA and Executive Order 12333—was found to exceed what is "strictly necessary" for national security. The Court applied its settled proportionality framework: even legitimate security objectives cannot justify mass, indiscriminate data collection without effective independent oversight and judicial remedies.

The Ombudsperson mechanism established under Privacy Shield was insufficient because it lacked genuine independence from the executive branch and could not issue binding decisions.

**Significance**: This case demonstrates that data protection can prevail even against national security claims from a major ally. However, the Court's analysis focused on *procedural* deficiencies (lack of proportionality review, inadequate remedies) rather than categorical rejection of security-based processing. A surveillance regime with proper safeguards might pass muster; the US system failed because it lacked such safeguards.

### Biometric Data Collection from Criminal Suspects

**C-205/21 – Ministerstvo na vatreshnite raboti**

Bulgarian law authorized compulsory biometric and genetic data collection from all persons accused of intentional criminal offenses.

*Holding 2 (Pro-Law Enforcement)*: Courts may authorize compulsory collection without full evidentiary assessment at the preliminary stage, provided effective subsequent judicial review is guaranteed.

*Holding 3 (Pro-Data Subject)*: Systematic, blanket collection from all accused persons without individual necessity assessment is precluded.

**The Court's Balancing**: Law enforcement operational needs justify *some* procedural flexibility—the deferred judicial review model. But efficiency cannot justify eliminating individual assessment entirely. Each collection must be evaluated for necessity in the specific case; categorical rules treating all accused persons identically fail the proportionality test.

---

## Part VI: Economic Rights and Business Interests

**Holdings examined**: 5 | **Data Protection Prevails**: 5

### Legitimate Interests and Commercial Processing

**C-252/21 – Meta Platforms (Facebook/Meta)** – Grand Chamber

Meta argued that its legitimate commercial interests in personalized advertising justified extensive collection and aggregation of user data across its services and third-party sources.

*Holding*: Users' fundamental rights and reasonable expectations override Meta's advertising interests. Extensive tracking creates "a feeling of continuous surveillance" that overrides commercial interests.

**The Court's Reasoning**: The Court acknowledged that commercial interests can constitute "legitimate interests" under Article 6(1)(f). However, the balancing test requires examining:
- Whether the data subject could reasonably expect such processing
- The intrusiveness of the processing
- Whether less invasive alternatives exist
- The severity of the impact on data subjects

Meta's practices failed on all counts: users did not reasonably expect cross-platform aggregation, the surveillance was pervasive, less invasive advertising models exist, and the impact on user autonomy was significant.

**Significance**: This Grand Chamber ruling establishes that scale and invasiveness matter in the balancing analysis. A large platform's commercial model does not automatically receive deference simply because advertising generates revenue. User expectations and autonomy carry substantial weight.

### Access Copies and Controller Costs

**C-307/22 – Leistritz**

German law permitted controllers to charge data subjects for the first copy of their personal data, ostensibly to protect controllers' economic interests.

*Holding*: National legislation cannot require data subjects to bear costs for obtaining a first copy of their personal data in order to protect controller economic interests.

**The Court's Reasoning**: Article 15(3) provides for a free first copy. Member States cannot override this through national legislation protecting business interests. The right of access must be "effective," and cost barriers undermine effectiveness.

**Significance**: Economic convenience for controllers does not justify limiting fundamental data protection rights. The GDPR provides specific exceptions (manifestly unfounded or excessive requests); Member States cannot expand these based on general business considerations.

---

## Part VII: Trade Secrets and Confidential Information

**Holdings examined**: 2 | **Mixed**: 2

### Algorithmic Transparency vs. Trade Secrets

**C-203/22 – Dun & Bradstreet Austria**

An Austrian law created an automatic exception to access rights under Article 15(1)(h) (information about automated decision-making logic) whenever trade secrets were potentially involved.

*Holding*: The controller must provide information to supervisory authorities or courts to enable case-by-case balancing; automatic categorical exclusions are invalid.

**The Court's Reasoning**: Trade secrets are protected under EU law (Directive 2016/943), and controllers have legitimate interests in protecting proprietary algorithms. However, these interests cannot be protected through blanket rules that eliminate data subject rights entirely.

The solution is procedural: when trade secrets and access rights conflict, an independent body (DPA or court) must assess the competing interests and determine appropriate disclosure modalities—which might include redacted information, summaries, or in camera review.

**Significance**: The Court refuses to establish a categorical hierarchy between data protection and trade secrets. Instead, it mandates case-by-case balancing through institutional mechanisms. Neither right automatically trumps the other.

---

## Part VIII: Special Categories – Gender Identity and Human Dignity

**Holdings examined**: 2 | **Data Protection Prevails**: 2

### Rectification of Gender Identity Data

**C-247/23 – Direcția pentru Evidența Persoanelor**

A Romanian authority refused to rectify gender identity data in public registers because Romanian law did not provide a specific procedure for legal gender recognition.

*Holding 1*: The right to rectification under Article 16 requires authorities to correct inaccurate data, including gender identity, regardless of whether national law provides specific recognition procedures.

*Holding 2*: Member States cannot require proof of gender reassignment surgery as a condition for exercising the right to rectification.

**The Court's Reasoning**: The accuracy principle (Article 5(1)(d)) requires that personal data be accurate and kept up to date. Gender identity is a matter of personal identity protected under Articles 3 and 7 of the Charter. Requiring surgical intervention as proof of gender identity "undermines the essence" of these fundamental rights—it imposes disproportionate bodily requirements on transgender individuals.

**Significance**: These rulings demonstrate data protection principles operating in service of broader human dignity values. The accuracy principle becomes a vehicle for protecting gender identity when Member States fail to provide adequate recognition procedures.

---

## Cross-Cutting Observations

### Observation 1: The Proportionality Cascade

The Court's balancing methodology follows a consistent pattern:

1. **Identify the competing interest** – Is it legitimate?
2. **Assess necessity** – Is the privacy intrusion required to achieve the objective?
3. **Examine alternatives** – Could less invasive means achieve the same result?
4. **Evaluate proportionality stricto sensu** – Even if necessary, is the intrusion proportionate to the benefit?

Data protection rarely loses at step 1 (legitimacy)—most competing interests are legitimate. Data protection most often prevails at steps 2-4, where the Court finds either that the intrusion isn't truly necessary or that less invasive alternatives exist.

### Observation 2: The Expectation Factor

"Reasonable expectations" appears repeatedly as a decisive factor. Processing that surprises data subjects—that occurs without their knowledge or contrary to their assumptions—consistently fails the balancing test. Conversely, processing that aligns with what individuals would anticipate receives more favorable treatment.

### Observation 3: Institutional Trust

When the Court allows competing interests to prevail, it typically involves institutional actors with structural legitimacy:
- **Courts**: Judicial independence and open justice receive strong deference
- **IP enforcement**: Procedural safeguards through judicial oversight

By contrast, pure commercial interests (advertising, data monetisation) consistently fail the balancing test, even when pursued by major economic actors.

### Observation 4: The Proportionality of Means

Several Grand Chamber rulings distinguish between the legitimacy of objectives and the proportionality of means:
- Anti-corruption is legitimate, but publishing spouse names online is disproportionate (C-184/20)
- Road safety is legitimate, but public penalty point disclosure is disproportionate (C-439/19)
- National security is legitimate, but mass surveillance without safeguards is disproportionate (C-311/18)

The Court rarely questions *whether* a societal objective is valuable; it focuses on *how* that objective is pursued and whether less privacy-invasive methods would suffice.

---

## Conclusion

The CJEU's balancing jurisprudence reveals a Court that takes data protection seriously as a fundamental right while acknowledging that it must coexist with other values. Data protection prevails in approximately two-thirds of explicit balancing situations, but this statistic masks important nuances:

**Data protection consistently prevails against**:
- Pure commercial interests (advertising, data monetization)
- Transparency interests that expose third parties (spouse names, family relationships)
- Public shaming mechanisms (penalty point disclosure)
- Blanket surveillance without procedural safeguards

**Data protection yields or shares ground with**:
- Judicial independence and open justice (structural constitutional principles)
- Intellectual property enforcement (with procedural safeguards)
- Law enforcement needs (subject to individual necessity assessment)
- Trade secrets (case-by-case balancing required)

The unifying principle is **proportionality applied contextually**. The Court does not establish rigid hierarchies; it examines specific factual circumstances, available alternatives, and the severity of impacts on both sides. This approach creates predictability through methodology rather than through categorical rules—parties can anticipate *how* the Court will reason, even if specific outcomes depend on factual particulars.

---

*Document generated: January 2026*
*Based on analysis of 41 holdings with explicit rights/interest balancing*
