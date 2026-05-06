# Phase 1 - Orthogonality Test Report
_Input feature rows: 4500, (topic, paraphrase) pairs analyzed: 150_

## P1-1: distribution of |r| per Layer 1 feature

| feature | N | median | IQR | 80th pct | 95th pct |
|---|---:|---:|---:|---:|---:|
| drift | 150 | 0.127 | 0.181 | 0.275 | 0.442 |
| timing_cv | 150 | 0.132 | 0.164 | 0.247 | 0.336 |
| mean_depth_excess | 150 | 0.123 | 0.146 | 0.227 | 0.332 |
| isolated_frac | 150 | 0.134 | 0.172 | 0.253 | 0.355 |
| d2_excess | 143 | 0.149 | 0.178 | 0.244 | 0.352 |

**P1-1** (median < 0.30 AND 80th pct < 0.50 per feature): **PASS**

**F1-1** (median > 0.50 for any feature): not triggered
**F1-2** (80th pct > 0.70 for any feature): not triggered

## P1-2: pairwise feature correlations

| | drift | timing_cv | mean_depth_excess | isolated_frac | d2_excess |
|---|---:|---:|---:|---:|---:|
| drift | 1.000 | 0.162 | 0.184 | 0.403 | 0.151 |
| timing_cv | 0.162 | 1.000 | 0.047 | 0.159 | 0.037 |
| mean_depth_excess | 0.184 | 0.047 | 1.000 | 0.077 | 0.924 |
| isolated_frac | 0.403 | 0.159 | 0.077 | 1.000 | 0.047 |
| d2_excess | 0.151 | 0.037 | 0.924 | 0.047 | 1.000 |

Median off-diagonal |r| = 0.155

**P1-2** (median pairwise |r| < 0.60): **PASS**

## P1-3: topic-group effect (Kruskal-Wallis)

| feature | H | p | median(control) | median(mid) | median(shaped) |
|---|---:|---:|---:|---:|---:|
| drift | 3.335 | 0.1887 | 0.160 | 0.106 | 0.105 |
| timing_cv | 2.275 | 0.3206 | 0.103 | 0.117 | 0.157 |
| mean_depth_excess | 0.337 | 0.8447 | 0.134 | 0.129 | 0.109 |
| isolated_frac | 0.115 | 0.9443 | 0.142 | 0.136 | 0.123 |
| d2_excess | 0.660 | 0.7188 | 0.150 | 0.160 | 0.122 |

**P1-3** (no KW p < 0.01): **PASS**
**F1-3** (any KW p < 0.01): not triggered

## Overall

- **(O-LM) holds** (P1-1+P1-2+P1-3 all pass): **YES**
- **(O-LM) falsified** (F1-1 or F1-2): **NO**

Next step: Phase 2 - augmented detection on case-study topics (FN-PHANTOM-002 Section 8.2).
