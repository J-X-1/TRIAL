# TRIAL Evaluation — 25 Test Questions with Answer Keys

All expected answers below are derived directly from the statute text in `chunks.json`. For each question, the answer key lists the relevant section(s) and what they say.

---

## Category A: Direct Factual Lookup (Single Section)

These should be straightforward — one section contains the answer clearly.

**Q1:** "What is the grace period for life insurance in Texas?"
- **Expected sections:** Sec. 1101.005 (primary), possibly also 1151.057, 1131.103
- **Expected answer:** At least one month for payment of each premium after the first. The policy remains in force during the grace period. The insurer may charge interest on a premium paid during a grace period, or deduct the overdue premium from any death settlement. (Sec. 1101.005)

**Q2:** "How long does a life insurance company have to settle a death claim?"
- **Expected sections:** Sec. 1101.011
- **Expected answer:** Not later than two months after the date of receipt of proof of death and proof of the claimant's right to proceeds. (Sec. 1101.011)

**Q3:** "What happens if the insured's age was understated on a life insurance policy?"
- **Expected sections:** Sec. 1101.008
- **Expected answer:** The amount payable under the policy is the amount that the premium paid would have purchased if the insured's age had been stated correctly. (Sec. 1101.008)

**Q4:** "Must life insurance benefits in Texas be paid in US currency?"
- **Expected sections:** Sec. 1102.002, possibly 1102.003
- **Expected answer:** Each benefit payable under an insurance policy delivered, issued, or used in Texas must be payable in currency. If benefits are payable in foreign currency, the policy must include a conspicuous statement that the value can fluctuate compared to US currency. (Sec. 1102.002, 1102.003)

**Q5:** "What is the rescission period for a fixed annuity contract?"
- **Expected sections:** Sec. 1116.002
- **Expected answer:** At least 20 days after the date the contract is delivered. During this period, the purchaser may rescind the contract and receive an unconditional refund of premiums paid, including any contract fees or charges. (Sec. 1116.002)

---

## Category B: Conceptual / Multi-Section Synthesis

These require the system to pull from multiple sections or synthesize a broader answer.

**Q6:** "What are the incontestability provisions across different types of life insurance?"
- **Expected sections:** Sec. 1101.006 (standard life), Sec. 1151.055 (industrial life), Sec. 1131.104 (group life)
- **Expected answer:** Standard life insurance: incontestable after two years from date of issue during the insured's lifetime, except for nonpayment of premiums; may optionally be contested for naval/military service violations in wartime (Sec. 1101.006). Industrial life insurance: incontestable after two years, except for nonpayment, naval/military service in wartime, and provisions relating to disability or accidental death benefits (Sec. 1151.055). Group life insurance: policy validity cannot be contested after two years except for nonpayment; individual insured's statements cannot be used to contest after two years from issuance during the insured's lifetime (Sec. 1131.104).

**Q7:** "What protections exist for a policyholder who defaults on premium payments?"
- **Expected sections:** Sec. 1105.004 (nonforfeiture provisions), Sec. 1101.005 (grace period), Sec. 1101.010 (nonforfeiture benefits general)
- **Expected answer:** The policyholder gets a grace period of at least one month (Sec. 1101.005). If they default, the company must grant a paid-up nonforfeiture benefit on request within 60 days of the premium due date (Sec. 1105.004(b)). On surrender within 60 days of default, the company must pay a cash surrender value if premiums were paid for at least 3 full years (ordinary) or 5 full years (industrial) (Sec. 1105.004(c)).

**Q8:** "How does Texas law regulate the replacement of existing life insurance policies?"
- **Expected sections:** Sec. 1114.001, possibly 1114.005, 1114.051
- **Expected answer:** Chapter 1114 regulates replacement transactions. Its purpose is to regulate activities of insurers and agents regarding replacement of existing life insurance and annuities, protect purchasers by establishing minimum conduct standards, ensure purchasers receive information to make decisions in their best interest, reduce opportunities for misrepresentation and incomplete disclosure, and establish penalties for failure to comply (Sec. 1114.001). A "financed purchase" where existing policy values fund a new policy from the same insurer is prima facie evidence of intent to finance (Sec. 1114.005).

**Q9:** "What rights does a group life insurance policyholder have when their employment ends?"
- **Expected sections:** Sec. 1131.110
- **Expected answer:** When an individual's insurance ceases because their employment or membership in the eligible class terminates, they are entitled to have the insurer issue an individual life insurance policy without disability or supplementary benefits. They must apply and pay the first premium within 31 days of termination. The individual policy is issued at the insurer's customary rates based on the insured's attained age and class of risk. (Sec. 1131.110)

---

## Category C: Specific Statute ID Lookup

These test exact retrieval by section number.

**Q10:** "Sec. 1101.006"
- **Expected sections:** Sec. 1101.006
- **Expected answer:** Incontestability provision. A life insurance policy in force for two years from its date of issue during the lifetime of the insured is incontestable, except for nonpayment of premiums. At the company's option, the policy may be contested at any time for violation of policy conditions relating to naval and military service in a time of war.

**Q11:** "What does Section 1103.151 say?"
- **Expected sections:** Sec. 1103.151
- **Expected answer:** A beneficiary of a life insurance policy forfeits their interest in the policy if the beneficiary is a principal or an accomplice in willfully bringing about the death of the insured.

**Q12:** "Sec. 1106.003"
- **Expected sections:** Sec. 1106.003
- **Expected answer:** Defines "mental incapacity" as a lack of the ability to (1) understand and appreciate the nature and consequences of a decision regarding the failure to pay a premium when due, and (2) reach an informed decision in the matter.

**Q13:** "What is Section 1153.702?"
- **Expected sections:** Sec. 1153.702
- **Expected answer:** Penalty provision for credit insurance. An individual, firm, or corporation that violates a final order under Chapter 1153 is liable for a civil penalty of not more than $250, or $1,000 if the court finds the violation to be willful. This is in addition to any other penalty provided by law.

---

## Category D: Domain-Specific / Nuanced Questions

These test whether the system handles nuance and doesn't over-claim.

**Q14:** "Can an insurer deny coverage based on opioid prescriptions?"
- **Expected sections:** Sec. 1101.253, Sec. 1101.251
- **Expected answer:** A life insurance company may not deny coverage based solely on whether an individual has been prescribed or obtained through a standing order an opioid antagonist (Sec. 1101.253). An "opioid antagonist" is defined as a drug that binds to opioid receptors and blocks or inhibits their effects to reverse an opioid overdose (Sec. 1101.251). The statute addresses opioid antagonists specifically, not opioid prescriptions generally. The corpus does not contain provisions on general opioid prescriptions.

**Q15:** "Can a minor purchase a life insurance policy in Texas?"
- **Expected sections:** Sec. 1104.001, 1104.004, 1104.005
- **Expected answer:** Yes, but only through a stock or mutual legal reserve life insurance company licensed in Texas. The application must be signed or approved in writing by a parent, grandparent, or adult sibling (or an adult eligible to be appointed guardian if none exist) (Sec. 1104.004). A minor who acquires a policy cannot rescind, avoid, or repudiate it by reason of minority (Sec. 1104.005).

**Q16:** "What is a 'financed purchase' in the context of life insurance replacement?"
- **Expected sections:** Sec. 1114.005
- **Expected answer:** A financed purchase occurs when a withdrawal, surrender, or borrowing from the values of an existing policy is used to pay premiums on a new policy owned by the same policyholder, issued by the same insurer, within 4 months before or 13 months after the new policy's effective date. This is deemed prima facie evidence of the policyholder's intent to finance the purchase with existing policy values. (Sec. 1114.005)

**Q17:** "What obligations does an insurer have when they find a match in the Death Master File?"
- **Expected sections:** Sec. 1109.011, 1109.012
- **Expected answer:** Insurers must compare in-force policies, annuity contracts, and retained asset accounts against a Death Master File at least semiannually (Sec. 1109.011). For each match, within 90 days, the insurer must: (1) complete a good faith effort to confirm the death, (2) review records to determine if the deceased had other products with the insurer, and (3) determine whether proceeds may be due (Sec. 1109.012).

**Q18:** "What is an accelerated benefit and when can an insurer pay one?"
- **Expected sections:** Sec. 1111.051, 1111.052
- **Expected answer:** An "accelerated benefit" is a benefit paid to an insured instead of a portion of a death benefit (Sec. 1111.051). An insurer may pay one under an individual or group term life policy if the insurer receives a written medical opinion that the insured has a terminal illness, a long-term care illness, or a condition likely to cause permanent disability or premature death — including AIDS, malignant tumor, or a condition requiring organ transplant (Sec. 1111.052).

---

## Category E: Out-of-Scope Questions (Should Decline)

The system should recognize these topics are not covered in the corpus.

**Q19:** "What are the penalties for securities fraud in Texas?"
- **Expected sections:** None relevant
- **Expected answer:** Should decline — securities fraud is not covered in Title 7 (Life Insurance and Annuities).

**Q20:** "What are the requirements for auto insurance liability coverage in Texas?"
- **Expected sections:** None relevant
- **Expected answer:** Should decline — auto insurance is not covered in this corpus.

**Q21:** "How do I file a health insurance claim in Texas?"
- **Expected sections:** None relevant
- **Expected answer:** Should decline — health insurance claims procedures are not in Title 7.

**Q22:** "What is the minimum wage in Texas?"
- **Expected sections:** None relevant
- **Expected answer:** Should decline — completely unrelated to insurance law.

---

## Category F: Edge Cases and Tricky Questions

These test robustness — partial answers, unusual topics within the corpus, etc.

**Q23:** "Can group life insurance continue during a labor dispute?"
- **Expected sections:** Sec. 1131.852
- **Expected answer:** Yes. An insurer may not deliver a policy subject to this subchapter unless it provides that if employees stop work because of a labor dispute, coverage continues on timely payment of premium for each employee who was covered when the stoppage began, continues to pay their individual contribution, and assumes responsibility for payment of the full premium if the employer does not pay. (Sec. 1131.852)

**Q24:** "What is the maximum interest rate allowed on life insurance policy loans?"
- **Expected sections:** Sec. 1110.004
- **Expected answer:** A life insurance policy must provide for a policy loan interest rate that either (1) does not exceed 10 percent per year, or (2) is an adjustable maximum interest rate based on Moody's Corporate Bond Yield Average — Monthly Average Corporates. (Sec. 1110.004)

**Q25:** "Who can be named as a beneficiary on a life insurance policy in Texas?"
- **Expected sections:** Sec. 1103.002, 1103.003, 1103.004, 1103.005, 1103.054
- **Expected answer:** A wide range of entities can be beneficiaries: any individual, corporation, joint stock association, trust estate (Sec. 1103.003), partnership or partner (Sec. 1103.004), or religious, educational, eleemosynary, charitable, or benevolent institution (Sec. 1103.005). An individual of legal age may designate in writing any individual, partnership, association, corporation, or other legal entity as beneficiary, owner, or both (Sec. 1103.054).

---


