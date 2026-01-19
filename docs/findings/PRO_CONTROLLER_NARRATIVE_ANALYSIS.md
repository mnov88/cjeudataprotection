# Non-Compensation Pro-Controller Rulings: A Narrative Analysis

## Introduction

Excluding compensation cases, the CJEU has issued **11 pro-controller holdings** across diverse areas of GDPR and related data protection law. These rulings reveal nuanced judicial reasoning that does not simply favor commercial interests, but rather addresses structural tensions within the data protection framework: the need for operational flexibility, institutional autonomy, proportionate enforcement, and legal certainty.

This document provides an objective, narrative account of each ruling, explaining what the Court decided, why it matters, and what underlying principles it reflects.

---

## 1. Security Standards: The Risk Management Framework

### C-340/21 – Natsionalna agentsia za prihodite (Bulgarian Revenue Agency Data Breach)

**Facts**: The Bulgarian National Revenue Agency suffered a cyberattack that exposed personal data of millions of citizens. Data subjects sought compensation, arguing that the mere occurrence of the breach proved the agency's security measures were inadequate.

**Holding**: A data breach by third parties is not sufficient in itself to establish that the controller's technical and organisational measures were inappropriate under Articles 24 and 32 GDPR.

**The Court's Reasoning**: The Court anchored its analysis in the text of Article 32, which requires "a level of security appropriate to the risk." This phrasing, the Court observed, reflects a deliberate legislative choice: the GDPR establishes a *risk management* system, not a *risk elimination* mandate. The regulation aims to "mitigate" risks, not prevent all breaches—an acknowledgment that perfect security is technically impossible.

Controllers must demonstrate the appropriateness of their measures through a two-stage assessment: first identifying the specific risks inherent to their processing operations, then evaluating whether the measures implemented adequately address those risks. The focus is *ex ante*—on whether reasonable precautions were taken—rather than *ex post*—on whether a breach occurred.

**Significance**: This ruling provides essential clarity for controllers operating in an environment where sophisticated cyberattacks are increasingly common. It establishes that compliance is judged by process and preparation, not by outcomes alone. A well-prepared controller who suffers a breach despite appropriate measures is not automatically liable.

---

### C-687/21 – MediaMarktSaturn (Employee Misdirection of Documents)

**Facts**: An employee at a MediaMarktSaturn subsidiary accidentally provided documents containing another customer's personal data to the wrong person. The affected data subject claimed compensation, arguing that this error demonstrated inadequate organizational measures.

**Holding**: Employee error in providing documents containing personal data to an unauthorized third party is not sufficient in itself to conclude that the controller's technical and organizational measures were inappropriate.

**The Court's Reasoning**: Building on C-340/21, the Court applied the same risk management framework to human error scenarios. Controllers are obligated to implement measures that reduce the risk of employee mistakes—through training, procedures, access controls, and supervision—but they cannot be expected to prevent every individual error by every employee in every circumstance.

The Court emphasized that the appropriateness of measures must be assessed "in a concrete manner," examining the specific risks, the nature of the processing, and the implementation of safeguards. The occurrence of an isolated employee mistake does not, without more, demonstrate systemic failure.

**Significance**: This ruling addresses the reality that organizations rely on human beings who will occasionally make mistakes. It distinguishes between organizational failure (inadequate systems, training, or supervision) and individual error within an otherwise adequate framework. Controllers are protected from strict liability for every human slip.

---

## 2. Administrative Fines: The Fault Requirement

### C-807/21 – Deutsche Wohnen (Grand Chamber)

**Facts**: Deutsche Wohnen, a German real estate company, was fined €14.5 million by the Berlin data protection authority for retaining tenant data longer than necessary. German law required that administrative fines could only be imposed if the infringement was attributable to an identified natural person within the organization—a requirement that would make fining large corporations difficult.

**Holdings**:
1. National law cannot require attribution to an identified natural person before fining a legal person controller (PRO_DATA_SUBJECT)
2. Administrative fines under Article 83 may only be imposed where the controller intentionally or negligently committed the infringement (PRO_CONTROLLER)

**The Court's Reasoning on the Fault Requirement**: While the first holding strengthened enforcement against corporations, the second established an important limitation. The Court examined Article 83(2), which lists factors for determining fines, including "the intentional or negligent character of the infringement." Reading this systematically with Article 83(3)—which addresses cumulative infringements committed "intentionally or negligently"—the Court concluded that fault is a prerequisite for fines, not merely an aggravating factor.

This interpretation rejects strict liability for administrative sanctions. A controller can only be fined if it "could not be unaware of the infringing nature of its conduct"—a standard that encompasses both deliberate violations and negligent failures to meet compliance obligations, but excludes situations where a controller genuinely and reasonably believed it was acting lawfully.

**Significance**: This Grand Chamber ruling establishes that GDPR administrative enforcement operates on a fault-based model. Controllers who make good-faith compliance efforts are protected from fines for inadvertent technical violations. The ruling balances the need for effective enforcement (through direct corporate liability) with fairness to controllers (through the fault requirement).

---

## 3. Institutional Boundaries: Judicial Independence and DPA Discretion

### C-245/20 – Rechtbank Midden-Nederland (Court Documents to Journalists)

**Facts**: A Dutch court provided documents from pending proceedings to journalists for reporting purposes. These documents contained personal data. A data subject complained to the Dutch Data Protection Authority, but the DPA declined jurisdiction, reasoning that the court was acting in its "judicial capacity."

**Holding**: Courts making documents containing personal data available to journalists for reporting falls within their judicial capacity, excluding DPA supervisory competence under Article 55(3) GDPR.

**The Court's Reasoning**: The Court interpreted "judicial capacity" broadly, guided by the purpose underlying Article 55(3): safeguarding judicial independence. Recital 20 of the GDPR explains that courts should not be subject to DPA oversight when acting judicially, to protect them from external pressure that could influence their decision-making.

The Court reasoned that judicial communication activities—including providing information to journalists about court proceedings—are integral to the administration of justice and the principle of open justice. Subjecting these activities to DPA oversight would create a form of external supervision over judicial functions, potentially chilling courts' engagement with the press and public.

Importantly, the ruling does not leave courts entirely unaccountable. Article 55(3) permits Member States to establish alternative oversight mechanisms within the judicial system itself—specialized bodies that can supervise court data processing while remaining within the judicial branch.

**Significance**: This ruling preserves the constitutional separation between judicial and administrative functions. It prevents DPAs—which are executive-branch agencies in most Member States—from exercising supervisory authority over courts' communication decisions. The holding reflects a structural concern with institutional architecture, not simply a preference for controllers over data subjects.

---

### C-768/21 – Land Hessen (DPA Enforcement Discretion)

**Facts**: Following a data breach, a data subject complained to the supervisory authority and sought judicial review of the DPA's decision not to impose corrective measures on the controller.

**Holding**: When a personal data breach is established, the supervisory authority is not required to exercise corrective powers where such action is not appropriate, necessary, or proportionate.

**The Court's Reasoning**: The Court examined the relationship between Articles 57 and 58 of the GDPR. Article 57 defines DPA tasks, including handling complaints and investigating subject matter. Article 58 provides a range of corrective powers—from warnings to fines to processing bans. The Court concluded that these provisions establish discretionary authority, not mandatory obligations.

DPAs must investigate complaints and inform complainants of outcomes, but they retain professional judgment about which corrective measures, if any, are appropriate in particular circumstances. Factors such as the severity of the infringement, whether the controller has taken remedial action, the likelihood of recurrence, and the proportionate allocation of enforcement resources all legitimately inform this discretion.

**Significance**: This ruling recognizes that DPAs operate with limited resources and must prioritize enforcement actions strategically. Not every established breach requires formal corrective measures; sometimes informal resolution, controller self-correction, or simply closing a case serves the regulatory objectives adequately. The ruling prevents courts from mandating specific enforcement actions and preserves DPA professional autonomy.

---

## 4. Processing Justifications: Operational Flexibility

### C-77/21 – Digi Távközlési (Test Database Copying)

**Facts**: A Hungarian telecommunications company copied customer personal data to a test database for the purpose of software testing and error correction. The data subject challenged this as incompatible with the original collection purposes.

**Holding**: The purpose limitation principle does not preclude copying personal data to a test database for testing and error correction where such processing is compatible with the initial collection purposes.

**The Court's Reasoning**: The Court examined Article 5(1)(b), which prohibits processing for purposes "incompatible" with original collection purposes, and Article 6(4), which provides criteria for assessing compatibility. Together, these provisions create a framework that allows some flexibility in data use while preventing fundamental purpose drift.

The Court found that using existing customer data for internal testing—to ensure systems function correctly and errors are identified and corrected—is compatible with the original purposes of providing telecommunications services. Testing contributes to service quality and reliability, which benefits the data subjects themselves.

However, the Court coupled this flexibility with strict limits: the second holding in this case (PRO_DATA_SUBJECT) emphasized that data in test environments cannot be retained indefinitely. Once testing purposes are fulfilled, the storage limitation principle requires deletion. The "oversight" excuse—that the controller simply forgot the data existed—provides no defense.

**Significance**: This ruling acknowledges that software development and maintenance require realistic test data. Forcing controllers to use only synthetic or anonymized data for all testing would impose significant operational burdens without proportionate privacy benefits, particularly for internal quality assurance. The ruling balances operational needs with continued protection through strict storage limitation.

---

### C-180/21 – Inspektor v Inspektorata (Public Prosecutor's Litigation Defense)

**Facts**: A Bulgarian public prosecutor's office processed personal data originally collected for criminal investigation purposes when defending the State in subsequent civil damages proceedings brought by a former suspect.

**Holding**: Processing personal data by a public prosecutor's office for State defense in damages proceedings may be lawful under Article 6(1)(e) GDPR as a task carried out in the public interest.

**The Court's Reasoning**: The Court first determined that this processing fell under the GDPR rather than the Law Enforcement Directive (2016/680), because defending civil litigation is not a criminal justice function. This brought the prosecutor's office within GDPR's scope as a data controller.

The Court then examined whether the public interest basis under Article 6(1)(e) could apply. It concluded that enabling public authorities to defend themselves against civil claims serves legitimate public interests: preserving legal certainty of official acts, protecting public finances, and ensuring equality of arms in litigation. A State body unable to use relevant evidence in its defense would be significantly disadvantaged.

Notably, the Court emphasized that this holding does not give public authorities unlimited data processing powers. The processing must still satisfy data protection principles—purpose limitation, data minimization, necessity—and affected individuals retain rights to object under Article 21.

**Significance**: This ruling addresses a practical gap: public authorities sometimes need to use data for legitimate defensive purposes that differ from original collection purposes. Without this flexibility, the State would face asymmetric litigation conditions. The ruling enables proportionate use while maintaining GDPR's protective framework.

---

### C-667/21 – Krankenversicherung Nordrhein (Medical Service Processing Employee Data)

**Facts**: A German statutory health insurance fund operated an in-house medical service that assessed employee working capacity. An employee challenged the processing of her health data by this internal service, arguing that only an independent, external medical provider should perform such assessments.

**Holding**: The Article 9(2)(h) exception applies when a medical service processes health data of its own employee to assess working capacity, provided it acts as medical service not employer.

**The Court's Reasoning**: Article 9(2)(h) permits processing of health data for assessing employee working capacity "on the basis of Union or Member State law or pursuant to contract with a health professional." The data subject argued this required an independent third party—someone with no employment relationship to the organization.

The Court disagreed. The text of Article 9(2)(h) does not require external independence; it requires professional competence and legal authorization. A properly qualified medical professional operating within an organization can fulfill these requirements, provided they act in their medical capacity (bound by professional secrecy and medical ethics) rather than their administrative capacity as a colleague.

The Court acknowledged the data subject's concerns about potential conflicts of interest but found these adequately addressed through existing safeguards: the professional secrecy obligation under Article 9(3), security requirements preventing inappropriate colleague access, and the general requirement that processing serve legitimate assessment purposes.

**Significance**: This ruling recognizes the practical reality that many organizations maintain in-house occupational health services. Requiring external providers for all employee health assessments would impose significant costs without necessarily improving privacy—external providers can have their own conflicts of interest and may be less familiar with specific workplace conditions. The ruling permits efficient arrangements while maintaining professional safeguards.

---

### C-169/23 – Agentsia po vpisvaniyata (Controller-Generated Data Exception)

**Facts**: A Bulgarian registration agency generated assessment data about individuals in the course of its administrative functions. Data subjects requested information about this internally-generated data under Article 14 (information to be provided where personal data have not been obtained from the data subject).

**Holding**: The exception to the controller's obligation to provide information under Article 14(5)(c) applies to all personal data not collected directly from the data subject, including data generated by the controller itself.

**The Court's Reasoning**: Article 14 establishes transparency obligations when controllers obtain personal data from sources other than the data subject. Article 14(5)(c) provides an exception when the data are subject to professional secrecy obligations under national or EU law.

The data subject argued this exception should only apply to data obtained from third parties, not to data the controller itself generates. The Court examined the text, which refers to data "not obtained from the data subject"—language that encompasses both external acquisition and internal generation. Data that a controller creates through its own assessment processes are, by definition, not obtained from the data subject.

This interpretation aligns Article 14's scope with Article 13's scope: Article 13 covers data collected directly from data subjects, while Article 14 covers all other scenarios. Controller-generated data fit within Article 14's framework.

**Significance**: This ruling reduces transparency burdens for controllers who generate assessments, evaluations, or other derived data as part of their regular functions—provided those data are subject to statutory secrecy requirements. It prevents controllers from having to provide potentially sensitive internal assessments (such as risk ratings, eligibility determinations, or compliance evaluations) where disclosure would conflict with legal confidentiality obligations.

---

## 5. Law Enforcement: Deferred Judicial Review

### C-205/21 – Ministerstvo na vatreshnite raboti (Bulgarian Biometric Data Collection)

**Facts**: Bulgarian law authorized courts to order compulsory collection of biometric and genetic data from persons accused of intentional criminal offenses. The authorizing court was not required to assess the evidence against the accused before approving collection. An accused person challenged this as violating his right to effective judicial protection.

**Holdings**:
1. Technical transposition errors do not invalidate authorization if the law is sufficiently clear (NEUTRAL)
2. Courts may authorize compulsory biometric collection without assessing evidence, provided effective subsequent review exists (PRO_CONTROLLER)
3. Systematic collection from all accused persons without individual necessity assessment is precluded (PRO_DATA_SUBJECT)

**The Court's Reasoning on Holding 2**: The Court acknowledged that compulsory biometric collection significantly interferes with fundamental rights, particularly the right to privacy and data protection. However, it recognized that criminal investigations operate under time pressure and informational constraints.

Requiring the authorizing court to conduct a full evidentiary assessment at the preliminary stage could impede investigations by revealing prosecution strategies or allowing evidence destruction. The Court found that Article 47 of the Charter (right to effective judicial protection) permits a staged approach: limited review at the authorization stage, followed by comprehensive review through subsequent judicial proceedings.

The accused retains the ability to challenge the collection order through appeal or in the context of the criminal trial itself. The presumption of innocence is preserved because the authorizing court makes no determination of guilt—it merely authorizes data collection for investigative purposes.

**Significance**: This ruling illustrates the Court balancing data protection against competing public interests. Unlike the other pro-controller holdings, this one explicitly addresses the law enforcement context where operational effectiveness may justify temporary limitations on immediate procedural rights. The Court carefully cabined this holding: the deferred review must be genuinely effective, and systematic blanket collection (holding 3) remains prohibited.

---

## 6. Intellectual Property Intersection

### C-597/19 – Mircom International Content Management (Peer-to-Peer File Sharing)

**Facts**: Mircom, an intellectual property management company, sought disclosure of subscriber data to pursue infringement claims against users who had shared copyrighted content via BitTorrent. The users' uploads occurred automatically through the peer-to-peer software.

**Holding**: Uploading pieces of a media file on a peer-to-peer network constitutes "making available to the public" even when automatic, provided the user consented to installing the software.

**The Court's Reasoning**: This case primarily concerned copyright law (Directive 2001/29) rather than data protection, though it was coded in the dataset because it affected data disclosure for enforcement purposes. The Court found that users who install BitTorrent software and load copyrighted files are "making available" those files to the public, even though the actual uploading occurs automatically without moment-to-moment user intervention.

The initial consent to install software that functions by sharing uploaded content constitutes sufficient volitional involvement. Users are presumed to understand that peer-to-peer systems operate through reciprocal sharing.

**Significance**: While tangential to core GDPR issues, this ruling affects the balance between privacy and intellectual property enforcement. By confirming that automatic P2P uploads constitute actionable infringement, the Court facilitated the data disclosure requests that enable rights holders to identify and pursue infringers. The holding favors "controllers" in the sense of rights holders seeking to protect their intellectual property.

---

## Cross-Cutting Themes

### Theme 1: Proportionality in Standard-Setting

Several rulings reflect the principle that GDPR requirements must be practically achievable. The security holdings (C-340/21, C-687/21) establish that controllers are measured against reasonable, risk-appropriate standards rather than impossible perfection. The test database ruling (C-77/21) acknowledges that software development requires realistic data. The medical service ruling (C-667/21) recognizes that workplace health assessments can be conducted internally.

### Theme 2: Institutional Autonomy

The judicial capacity ruling (C-245/20) and DPA discretion ruling (C-768/21) both preserve the autonomous judgment of specialized institutions. Courts should not face DPA oversight when performing judicial functions; DPAs should not face judicial mandates to exercise specific enforcement powers. These rulings reflect constitutional principles about separation of powers and professional expertise.

### Theme 3: Fault and Culpability

The administrative fines ruling (C-807/21) establishes that GDPR enforcement operates on a fault basis. This aligns with broader principles of administrative law that sanction intentional or negligent wrongdoing rather than innocent mistakes. Controllers who genuinely attempt compliance are protected from penalties for technical inadvertent violations.

### Theme 4: Balancing Within Cases

Several of these cases contain multiple holdings with different directions. C-205/21 permits deferred judicial review (pro-controller) while prohibiting systematic blanket collection (pro-data subject). C-667/21 permits internal medical services (pro-controller) while requiring cumulative Article 6 and Article 9 compliance (pro-data subject). C-77/21 permits test database copying (pro-controller) while strictly enforcing storage limitation (pro-data subject). This pattern suggests the Court consciously balances flexibility with constraints.

---

## Conclusion

The non-compensation pro-controller rulings are not expressions of deregulatory impulse or commercial favoritism. They address specific structural challenges within the data protection framework:

- **Security standards** that can actually be met
- **Administrative enforcement** grounded in fault
- **Institutional boundaries** that preserve judicial independence and DPA expertise
- **Operational flexibility** for legitimate business and public functions
- **Law enforcement** needs in criminal contexts

Each ruling represents a calibration—defining the boundaries of GDPR obligations in ways that maintain the protective framework while acknowledging practical realities. The Court consistently invokes "high level of protection" even in pro-controller holdings, suggesting it views these boundaries as *defining* appropriate protection rather than undermining it.

---

*Document generated: January 2026*
*Based on analysis of 11 non-compensation PRO_CONTROLLER holdings*
