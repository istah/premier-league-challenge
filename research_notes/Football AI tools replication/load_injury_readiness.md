# Football load, readiness, fatigue and injury-risk monitoring: real tools, validation, and what we can replicate on synthetic data

Research date: 2026-10-20. About 15 tool calls. Most searches returned abstracts or snippets only, so the "Gaps" sections are long on purpose. Evidence grade key: A = peer-reviewed systematic review or scoping review, B = single peer-reviewed study or editorial, C = journalism quoting clubs or vendors, D = vendor marketing or blog. Anything older than 2022 is tagged [DATED].

## 1. Vendors and what coaches actually get

### Takeaway
The only vendor with a clearly described coach-facing "AI risk" output is Zone7: a daily emailed list of flagged players (overload or underload), not a published probability or score. For the other vendors (Catapult, Kinexon, STATSports, Playermaker, Kitman, Orreco, Sportlogiq) I found little reliable, independent description of outputs. The Zone7 evidence is almost entirely vendor- or club-reported (grade C/D).

### Cited Findings
- Zone7 sends daily alerts, typically emailed before training, listing players who may be nearing a "danger zone". Flags can reflect overload or underload. Rangers typically get 1-2 flagged players a day, which staff then investigate. The ESPN article gives no risk scores, probabilities or thresholds. [C, 2023] — [ESPN](https://africa.espn.com/football/story/_/id/37613690/algorithm-really-predict-injuries)
- Zone7 says more than 50 clubs use it, many anonymously. Named: Getafe (since 2017-18) and Rangers (summer 2020). Maccabi Tel Aviv trialled it in 2017 while the coach ignored it. [C] — [ESPN](https://africa.espn.com/football/story/_/id/37613690/algorithm-really-predict-injuries)
- Getafe's head of performance reports a 40% fall in injury volume in year one and 66% in year two. These are club-reported before/after figures with no control group, and the engine had more data in year two. [C] — [ESPN](https://africa.espn.com/football/story/_/id/37613690/algorithm-really-predict-injuries)
- No false-positive rate, sensitivity or precision was reported anywhere in the ESPN piece. Zone7's founder said "We are not there yet as a company". Rangers' Milsom called the club "data-informed and not data-driven". Cruyff called it "not a deciding tool". [C] — [ESPN](https://africa.espn.com/football/story/_/id/37613690/algorithm-really-predict-injuries)
- A company-run test with 11 professional teams is described on a Harvard Digital Initiative student platform: 423 injuries across the teams, a model built per team, and the algorithm was not trained on those clubs beforehand. I did not see accuracy figures. [D] — [Harvard D3](https://d3.harvard.edu/platform-digit/submission/zone7-future-of-ai-in-football-soccer/)
- Zone7 claims of up to 50% injury reduction appear in trade press, which is company marketing. [D] — [Soccerscene](https://soccerscene.com.au/?p=30803)
- Zone7's co-founder and CTO (E. Eliakim) co-authored a BMJ Open Sport & Exercise Medicine paper on injury costs in the Premier League, so that literature is not independent. [B, 2020] — [Correction notice](https://pmc.ncbi.nlm.nih.gov/articles/PMC7299022)
- Catapult claims its athlete monitoring is "trusted by over 1,200 football teams" including Real Madrid and Chelsea. Its consumer product shows distance, load, heart rate, accelerations and decelerations on a web dashboard. Company claim. [D] — [PYMNTS](https://www.pymnts.com/fitness/2021/catapult-debuts-fitness-tracker-for-athletes-coaches/) [DATED], [CB Insights](https://www.cbinsights.com/company/catapult-sports)
- Kitman Labs (Irish, founded 2012) pairs statistics, research and practitioner experience to flag likely injuries and gives each player a profile based on training data. Football clients named in press: Everton, Norwich City, Seattle Sounders. It also has a Premier League deal for a youth "football intelligence platform". [C/D, mostly 2015-2018] [DATED] — [Health Club Management](https://www.healthclubmanagement.co.uk/health-club-management-news/Bath-Rugby-Club-signs-deal-with-Kitman-Labs-tech-company-in-a-bid-to-keep-its-players-from-injury/317154), [GeekWire](https://www.geekwire.com/2015/sounders-partner-kitman-labs-use-injury-prevention-technology/), [Business Post](https://www.businesspost.ie/article/kitman-labs-scores-with-major-premier-league-deal/)
- Playermaker: boot-mounted wearable for real-time motion tracking and foot-ball interactions (CB Insights profile). [D] — [CB Insights](https://www.cbinsights.com/compare/catapult-2-vs-playermaker)
- Consumer wearables: the largest sleep/HRV comparison (CQUniversity, in Sensors) is summarised by WHOOP as 99% HRV accuracy, with critics noting it used previous-generation sensors and low-activity sleep. Another HRV study (small, n=13, Polar H10 reference) reports concordance Oura Gen 4 0.99, WHOOP 4.0 0.94, Garmin Fenix 6 0.87, but that figure comes from a blog summary. None test accuracy during hard training. [D/C, 2022-2025] — [WHOOP](https://www.whoop.com/thelocker/whoop-proven-most-accurate-wearable-in-heart-rate-heart-rate-variability-measurements), [the5krunner](https://the5krunner.com/2025/10/06/garmin-beaten-by-oura-whoop-in-hrv-accuracy-showdown)
- A running-app company's informal analysis found Garmin Training Readiness correlated about 0.056 with running efficiency within athletes (n=39). Non-peer-reviewed, interested party. [D] — [athletedata.health](https://athletedata.health/guides/whoop-vs-oura-vs-garmin)

### Inferences
- The honest real-world output shape is "a short daily flag list for staff to investigate", not a numeric injury probability. Our dashboard can copy that shape (flag + contributing factors + "staff to review").
- Readiness colour (green/amber/red) is common product design, but I found no validation for any vendor's colour thresholds.

### Gaps
- Nothing reliable found on Kinexon, STATSports, Sportlogiq or Orreco outputs (Orreco returned zero results). Polar's football use was not searched. Fill these from vendor sites only if needed, labelled as grade D.
- No independent evaluation of Zone7 found. Full text of the Harvard-hosted write-up (accuracy figures) not retrieved.
- Which Premier League clubs use which vendor is mostly undisclosed.

## 2. Published validation

### Takeaway
ACWR is contested: widely adopted and IOC-endorsed in 2016, but heavily criticised (Impellizzeri 2020, 2021) as conceptually flawed and not a valid injury predictor. ML injury prediction in football has weak, heterogeneous evidence with questionable clinical value even where AUC is high. Subjective wellness is at least as sensitive as HRV for fatigue, and HRV-guided training has small effects, mostly shown in endurance athletes, not football.

### Cited Findings
- ACWR (Gabbett 2016) is built on Banister's fitness-fatigue model. Common calculation: last 7 days vs the mean of the previous 3-6 weeks; 0.8-1.3 called a "sweet spot", 1.5+ elevated risk. [B, 2021 editorial] — [Zouhal et al. editorial](https://pmc.ncbi.nlm.nih.gov/articles/PMC8138569/)
- Critiques: heterogeneous load measures (sRPE, HR, GPS), arbitrary windows with no rationale, and training load is not a surrogate for mechanical load. [B] — [Zouhal et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8138569/)
- Impellizzeri et al. 2020 (IJSPP, "Conceptual Issues and Fundamental Pitfalls") and 2021 (Sports Medicine, "Time to Dismiss ACWR and Its Underlying Theory") argue the ratio and its theory should be dismissed; the 2021 paper compared the ratio with fixed and randomly generated chronic loads. I read only abstracts and summaries. [B, 2020-21] — [Search summary of Impellizzeri 2021 PDF](https://iris.univr.it/retrieve/e34cfb98-e922-4c2f-aab5-18583ab7e31b/Impellizzeri_What%20Role%20Do%20Chronic%20Workloads%20Play_SportMed_2021.pdf), [SimpliFaster](https://simplifaster.com/articles/acwr-high-performance-tool/) (blog, D)
- Defenders: IOC 2016 consensus suggested ACWR; Myers et al. 2020 reported "level A" support for sRPE-ACWR for non-contact injuries. [B] — [Zouhal et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8138569/)
- In that editorial's Research Topic: ACWR spikes unrelated to injury in professional soccer (Suarez-Arrones); workload ratios associated with injury but no "sweet spot" (Sedeaud). [B] — [Zouhal et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC8138569/)
- ML review (BJSM 2025, Leckey et al., scoping): 1,241 records, 38 studies charted, football most studied. AUC was the main metric (71%). Tree-based models best in 60% of studies; logistic regression beat ML in 4 of 12 comparisons. Three studies had AUC > 0.9 but clinical relevance is questioned. Stated limits: small datasets, heterogeneous injury definitions and outcomes, wide prediction windows and broad injury definitions. [A, 2025] — [UP repository](https://www.repository.up.ac.za/handle/2263/100173?show=full)
- Earlier systematic review of ML for sport injury prediction and prevention (Van Eetvelde 2021, search March 2020). Only abstract-level detail retrieved. [A, DATED] — [JEO](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8046881/)
- Wellness vs HRV (Rabbani 2019, n=9 professional players, 4 days post-match): Hooper Index signal-to-noise 5.5 vs 1.5 for HRV; TE/SWC 3.1 vs 4.4; within-player correlation between the two only r = -0.41. Small single-league sample. [B, DATED] — [Frontiers in Physiology](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6390199/)
- Saw, Main, Gastin 2016 (BJSM, 56 studies): subjective and objective measures generally did not correlate; subjective measures tracked acute and chronic load with superior sensitivity. [A, DATED] — [BJSM](https://bjsm.bmj.com/content/50/5/281)
- HRV-guided training: Düking 2021 meta-analysis (8 studies, 198 participants, mostly endurance): medium effect on submaximal physiological parameters (g = 0.296), small non-significant effects on performance and VO2peak. I found no team-sport or football-specific HRV-guided training review. [A, 2021] — [search summary](https://pubmed.ncbi.nlm.nih.gov/34489178/), [Granero-Gallegos 2020](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7663087/)
- Zone7 injury-reduction claims: no independent study found (see section 1).

### Inferences
- Why ML often fails to generalise (partly my reasoning, partly the review's stated limits): rare outcome, small per-club samples, inconsistent injury definitions, per-club distribution shift, and AUC reported without calibration. The review's abstract does not mention external validation, calibration or leakage; I could not check the full text.
- For a hackathon, the defensible stance is "illustrative risk indicator on synthetic data", not "predictor".
- Hooper-style wellness is cheap and at least as sensitive as HRV in the one small football study, which supports giving the wellness check-in equal weight to HRV in our score.

### Gaps
- Primary text of Gabbett 2016 and Impellizzeri papers not read. Mathematical coupling critique not confirmed from a source here.
- Full text of Leckey 2025 not read (external validation, leakage, calibration unknown).
- No systematic review of HRV monitoring specifically in football found.
- Prospective evidence that any monitoring programme reduces football injuries (RCT-level) not found.

## 3. In-match physical monitoring

### Takeaway
Wearable tracking in matches is permitted in principle, but live data reaching the bench has regulatory history, and I found no evidence of published fatigue thresholds that clubs apply in real time. Published research is retrospective and shows second-half declines that are position- and metric-dependent.

### Cited Findings
- IFAB approved wearable EPTS in competition in February 2015 with conditions (preventive medical benefit, no danger); original rules barred data going to coaches during play, final decision lay with each association, league or competition. [C, DATED] — [Loeb & Loeb](https://www.loeb.com/-/media/files/pdfs/socolow_brian_april_2016.pdf), [IFAB circular](https://downloads.theifab.com/downloads/circular-1_en?l=en)
- The 2018/19 Laws introduced a FIFA quality mark and allowed EPTS data to be received in the technical area during the match. [C, DATED] — [IFAB circular 13/FA summary](https://thefa.com/-/media/cfa/surreyfa/files/referees/laws_of_the_game_2018_19_law_changes_explained_en.ashx?la=en). I could not confirm the current 2026/27 wording.
- A-League study (68 matches, 508 GPS files, Biology of Sport 2023): strikers had lower second-half peak demands on all three measures; defensive midfielders, wide defenders and wingers had lower peak acceleration. [B, 2023] — [Biology of Sport](https://www.termedia.pl/Positional-and-temporal-differences-in-peak-match-running-r-ndemands-of-elite-football,78,46979,0,1.html)
- A 2012 semi-professional study found total distance and mean speed fell but high-speed running and sprint distance did not differ between the first and second 15 min of each half, attributed to pacing. [B, DATED] — [DOI](https://dx.doi.org/10.1055/s-0032-1327647)
- Women's football study (24 matches): significant second-half decrease, forwards sharpest drop in high-speed running. [B] — same search, [Biology of Sport listing](https://doaj.org/article/e0ecddd10f2e427cb558e7d82c7d3241)

### Inferences
- Position-specific, player-relative baselines are the defensible design (compare a player's late-game output to their own earlier output), not one universal sprint-count cutoff.
- No source gave a numeric sprint-count or high-speed-distance threshold that triggers a substitution. Do not invent one; present any threshold in our app as a configurable demo parameter.
- Pacing and tactical context confound fatigue: a decline can reflect game state, not fatigue.

### Gaps
- No published thresholds for live fatigue alerts or substitution triggers found.
- No evidence of how Premier League clubs use live GPS/HR in-match today. Current IFAB Law 4 EPTS text not verified.
- Match HR telemetry specifically (5-minute HR) not researched.

## 4. Data practices: consent, GDPR, unions

### Takeaway
Wearable and biometric data is legally sensitive; FIFPRO and FIFA's Charter treats performance data as personal data with GDPR-style rights. Whether player consent is truly voluntary in employment is an open issue flagged by lawyers. Your pitch claim "real use needs consent" is directionally supported but should be stated with that nuance.

### Cited Findings
- Law-firm analysis: wearables (GPS trackers, smart garments, heart-rate monitors, recovery platforms) generate "some of the most legally sensitive forms of sports data"; under GDPR player data "may qualify as special-category personal data"; "whether player consent is truly voluntary in an employment context" is listed as an open issue. Disputes often turn on contractual allocation of rights rather than "ownership". [C, 2026-07] — [Morgan Lewis](https://www.morganlewis.com/pubs/2026/07/soccers-big-data-dilemma-who-owns-the-data-behind-the-beautiful-game)
- UK GDPR gives no one ownership of personal data. [C] — [Data Protection People](https://dataprotectionpeople.com/resource-centre/player-data-rights-under-uk-gdpr-a-guide-for-sports-clubs/)
- FIFA and FIFPRO agreed in 2019 to build a data-protection framework on GDPR and Swiss law; the Charter of Player Data Rights launched in September 2022. Rights listed: be informed, access, revoke, restrict processing, portability, rectification, complain, erasure. [A-grade primary, 2019/2022, slightly DATED] — [FIFPRO 2019](https://fifpro.org/en/articles/2019/11/fifa-and-fifpro-develop-standards-on-management-of-personal-player-performance-data), [FIFPRO 2022](https://www.fifpro.org/articles/2022/09/charter-of-player-data-rights-launched-for-professional-footballers)
- FIFPRO survey: 80% of players want access to their data to improve performance, but they worry about collection and use. [C] — [FIFPRO](https://www.fifpro.org/articles/2022/09/charter-of-player-data-rights-launched-for-professional-footballers)
- FIFPRO took a stake in Sports Data Labs for player data collection, consent management and monetisation. [C] — [SportBusiness](https://tech.sportbusiness.com/news/players-to-earn-from-data-capture-in-fifpro-sdl-pact/)
- Project Red Card: over 1,400 sportspeople challenging commercial use of performance data (including GPS data from Premier League and Championship matches sold to betting/gaming firms) without consent or pay. [C] — [Gambling Insider](https://www.gamblinginsider.com/?p=54550)
- The English PFA took part in FIFPRO's Player IQ Tech Experience Tour; FIFPRO says unions are best placed to act on data rights. [C, 2023] — [FIFPRO](https://fifpro.org/en/articles/2023/04/player-data-rights-why-unions-have-an-integral-role-to-play)
- A 2024 non-peer-reviewed preprint of 150 European footballers reports 78% concerned about misuse of biometric data. [D] — [Preprints.org](https://www.preprints.org/manuscript/202411.0558)

### Inferences
- Safe wording: "Real deployments would treat this as special-category health data, requiring a lawful basis, transparency and player access, with consent only one possible basis and questionable in employment." Avoid "consent is legally required" as a flat claim.
- Our synthetic players have no real data subjects, so we can show the consent UX without any privacy exposure.

### Gaps
- No recent PFA position on wearable data found. Full text of the Charter not read. Article 9 GDPR treatment of consent in employment not sourced from a primary source.

## 5. Transparent vs black box

### Takeaway
ACWR, z-score vs baseline, and wellness composites are fully transparent but contested or weak. Vendor ML (Zone7, Kitman) is proprietary and unvalidated publicly. Tree-based and logistic models are the middle ground and are what the literature supports.

### Cited Findings
- Tree-based models (Random Forest, XGBoost) top-performing in 60% of reviewed ML studies; logistic regression won 4 of 12 head-to-heads. [A, 2025] — [Leckey et al.](https://www.repository.up.ac.za/handle/2263/100173?show=full)
- Zone7 reports no published accuracy metrics; models are built per team; client data reportedly not retained after the relationship ends (founder's unverified claim). [C/D] — [ESPN](https://africa.espn.com/football/story/_/id/37613690/algorithm-really-predict-injuries)
- Staff language across sources stresses human-in-the-loop ("data-informed", "not a deciding tool"). [C] — [ESPN](https://africa.espn.com/football/story/_/id/37613690/algorithm-really-predict-injuries)

### Inferences
- Replication verdicts on synthetic data, with what would be dishonest to claim:

| Approach | Verdict | Dishonest to claim |
|---|---|---|
| ACWR from training_sessions load (rolling 7d / 28d, optionally EWMA) | Easy | That it predicts injuries or that 0.8-1.3 is a validated safe zone. On synthetic data it only demonstrates the calculation. |
| HRV and resting HR vs personal baseline (z-score, e.g. against a 4-week mean/SD) | Easy | That it is "validated readiness". Evidence for HRV-guided training is small and mostly endurance-based. Synthetic HRV is whatever we generated. |
| Wellness check-in composite (Hooper-style) | Easy | That it outperforms HRV in general. One n=9 study plus a 2016 review support its sensitivity only. |
| Composite injury-risk score (ACWR + HRV + history + age) | Partial | Any accuracy figure. If injuries in synthetic data were generated from those same features, a model "recovering" them is circular and proves nothing. Present as a rules-based indicator and say weights are illustrative. |
| ML injury classifier (RF/XGBoost/logistic) | Partial, only if injuries are generated independently of the features; otherwise circular | AUC as evidence of real-world performance. Real-world AUC > 0.9 is itself viewed sceptically. Report calibration and a baseline logistic model. |
| Zone7-style flag list ("who to look at today") | Easy to mimic the output form | That it replicates or matches Zone7. Its models, data (reportedly 200M hours, company claim) and accuracy are unverified. |
| Late-game fade profile from match_tracking (per-5-min distance, sprints, HR vs own early-match baseline) | Easy to build | That a decline equals fatigue (pacing and game state confound it) or that thresholds are published. |
| Live substitution alert from tracking | Partial (simulate a stream) | That clubs use such alerts per published thresholds; none found. Real-time data to the bench is rule-governed. |
| Set-piece exposure | Not assessed in this research | n/a |
| Genuine vendor pipelines (Catapult/Kinexon GPS hardware, Playermaker, Sportlogiq video) | Not feasible | Any claim of hardware-grade tracking validity; our data is synthetic. |
| Wearable accuracy (Whoop/Oura/Garmin) | Not feasible to demonstrate | Any statement about device accuracy in training, which is unvalidated. |

### Gaps
- No source rated vendor models on explainability. This section's classification is my inference from what is public.
- Set-piece exposure monitoring was outside the sources found and not researched here.
