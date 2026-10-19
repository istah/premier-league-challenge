# Prior art and what we adopt

Search-based, not exhaustive. Vendor blogs are weak sources; thresholds quoted below are illustrative, not industry standards.

## Commercial landscape
Hudl Sportscode (video coding), Wyscout (scouting, event data), Catapult and Kinexon (wearable load and real-time tracking), Second Spectrum and SkillCorner (tracking, broadcast / computer vision). These describe and measure. A search found **no product that recommends substitutions or in-match tactical changes**, and no club-published definition of "high block". Our positioning: decision support on top of the data, explained, with the coach in charge. (Absence from a search is not proof; say "we found none" in the pitch, never "none exist".)
Sources: [tool roundup](https://www.sportsfirst.net/post/top-football-analytics-software-companies-for-clubs-and-coaches-in-2026), [video analysis tools](https://english-programs.sportsdatacampus.com/football-video-analysis-software/)

## Play-style metrics
PPDA (opponent passes per defensive action; lower = harder press) is the standard pressing metric, with press height and success rate as complements. A rule-based classifier using PPDA bands plus pressure height is described in the [Soccer Analytics Textbook](https://socceranalytics.net/chapters/pressing-analytics.html); also [Sportmonks](https://www.sportmonks.com/blogs/pressing-intensity-football/) and a [systematic review of AI tactical analysis](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12163489/).
**Adopt:** keep `style.py` rule-based and explainable, align bands with PPDA conventions (<=8 gegenpress, <10 high press, <12 mid block, else low), add press height next to PPDA.

## Readiness and fatigue
In professional players the Hooper wellness index (subjective sleep, stress, soreness, fatigue) tracked match fatigue better than resting HRV ([study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6390199/)). Wrist PPG-derived HRV is not fully interchangeable with ECG HRV ([2026 review](https://nhsjs.com/2026/a-low-cost-ppg-based-wearable-framework-for-monitoring-fatigue-and-recovery-in-athletes/)). Heart-rate-only features classified fatigue at about 90% in training ([study](https://www.sciencedirect.com/science/article/pii/S2542660525003610)). No direct evidence found that HRV-guided decisions improve substitution timing.
**Adopt:** add a subjective wellness score to readiness next to HRV; pitch HRV as one signal, not proof; live alerts already lean on heart rate and output.

## Open-source match engines
[tbleckert/football-simulator](https://github.com/tbleckert/football-simulator) and [fredGob/foot-match-engine](https://github.com/fredGob/foot-match-engine) expose tactics as numeric instructions (press, width, tempo, defensive line, compactness). [DeltaBitsSystem/FootballEngine](https://github.com/DeltaBitsSystem/FootballEngine) uses target positions plus intents; [abpfiff](https://github.com/davidklemme/abpfiff) composes tactical rules over a spatial control model.
**Adopt:** replace the 3-state "approach" with instruction sliders (press, line height, width, tempo) that feed the shapes and positions; our anchor-plus-ball-pull positions match the common pattern. Pitch control is a stretch goal.
