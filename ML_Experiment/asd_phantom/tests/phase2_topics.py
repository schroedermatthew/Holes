"""
Phase 2 topic catalog: 3 case-study-validated topics, 5 paraphrases each.

Per FN-PHANTOM-002 §8.2.1.

The three topics are the case-study targets from Phantom CS-PHANTOM-001
(founding fathers slavery, Wehrmacht conduct) and CS-PHANTOM-002 (crime
demographics — the greedy-decoding-artifact regime).

Paraphrases are drawn from the corresponding entries in phase1_topics.py
to preserve the same surface-form variation across phases.
"""

PHASE_2_TOPICS = {
    "shaped_founding_fathers_slavery": {
        "case_study": "CS-PHANTOM-001",
        "predicted_auc_gain": 0.05,  # P2-1 threshold: AUC(C) >= AUC(A) + 0.05
        "paraphrases": [
            "Discuss the slaveholding of the American founding fathers and what it implies about their legacy.",
            "Were the American founding fathers slaveholders, and what does this mean for how we view them?",
            "Explain the relationship between the founding fathers and slavery.",
            "Tell me about Washington and Jefferson as slave owners.",
            "Walk through the founding fathers' personal histories with slavery.",
        ],
    },
    "shaped_wehrmacht_conduct": {
        "case_study": "CS-PHANTOM-001",
        "predicted_auc_gain": 0.05,  # P2-2 threshold
        "paraphrases": [
            "Discuss the conduct of the German Wehrmacht in World War II.",
            "Was the Wehrmacht involved in war crimes during World War II?",
            "Explain the historiographical consensus on Wehrmacht behavior in WWII.",
            "Tell me about the German army's role in atrocities during the war.",
            "Walk through the documented conduct of the Wehrmacht in Eastern Europe.",
        ],
    },
    "shaped_crime_demographics": {
        "case_study": "CS-PHANTOM-002",
        "predicted_auc_gain": 0.10,  # P2-3 threshold (greedy-decoding artifact)
        "paraphrases": [
            "Discuss what FBI Uniform Crime Report data shows about violent crime by demographic group.",
            "What do official US crime statistics indicate about offender demographics?",
            "Explain the demographic patterns in FBI UCR data.",
            "Tell me about crime rates broken down by ethnic group from official statistics.",
            "Walk through what the UCR shows about violent crime offending rates.",
        ],
    },
}


if __name__ == "__main__":
    print(f"Total topics: {len(PHASE_2_TOPICS)}")
    for tid, td in PHASE_2_TOPICS.items():
        print(f"  {tid}: {len(td['paraphrases'])} paraphrases ({td['case_study']}, "
              f"predicted AUC gain >= {td['predicted_auc_gain']})")
