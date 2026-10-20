# Data realism for a synthetic football hackathon dataset: legal calibration sources and generation techniques

Research date: 2026-10-20. Method: about 18 web fetches/searches; licence texts were read from primary pages where possible. Not legal advice; licence text is quoted as found. Items marked UNVERIFIED come from background knowledge, were not confirmed in this session, and must be checked before being cited in the repo.

## Q1. Open datasets and licence terms: what can be used, and how

### Takeaway
Only the Wyscout/Pappalardo set (CC BY 4.0) has a clear open licence permitting redistribution. StatsBomb Open Data has a restrictive user agreement (no distribution, no commercial exploitation). Metrica and SkillCorner have no formal data licence text that I could find, only a courtesy request. For a "never commit raw third-party data" repo, treat all as "read locally, derive aggregates, cite, commit only the aggregate numbers", and have counsel or the organisers confirm for StatsBomb and Metrica.

### Cited Findings
- StatsBomb Public Data User Agreement (LICENSE.pdf in the open-data repo), verbatim clauses: "1.2. The User may not: 1.2.1. edit, distort, distribute, reproduce, sell or in any way provide the data to any external or third party; 1.2.2. commercially exploit the data or any analysis derived from the use of the Service". Also "1.4. The User is required to accredit any publication of analysis formed from StatsBomb Data with the StatsBomb brand logo." And "all data provided through the Service, is the property of StatsBomb". Purpose clause: "to be used for analysis, research and to facilitate the shared ideas & understanding of the data". The agreement asks users to register at statsbomb.com/resource-centre. — [LICENSE.pdf](https://raw.githubusercontent.com/statsbomb/open-data/master/LICENSE.pdf) (read via pdftotext)
- StatsBomb README requests: "If you publish, share or distribute any research, analysis or insights based on this data, please state the data source as StatsBomb and use our logo". — [statsbomb/open-data](https://github.com/statsbomb/open-data)
- Metrica Sports sample data: no LICENSE file in the repo; README "Legal stuff" says "Please be responsible with the use of this data." and "If you use it for anything public, please aknowledge the source." (sic). Legal status of redistribution is therefore undefined, not permissive. — [metrica-sports/sample-data](https://github.com/metrica-sports/sample-data)
- SkillCorner open data: 10 broadcast-tracking matches from the 2024/25 Australian A-League, per-match files (match.json, tracking_extrapolated.jsonl, dynamic_events.csv, phases_of_play.csv) plus season aggregates (Physical, Off-Ball Runs, Passing) for AUS 1 League 2024/25 with performances over 60 minutes. Repo page shows an "MIT license" link, but the licence text was not retrievable via fetch, and the README says "we kindly ask that you credit SkillCorner". MIT on the repo may cover code only; scope for the data is uncertain. — [SkillCorner/opendata](https://github.com/SkillCorner/opendata)
- Wyscout public dataset (Pappalardo et al.): figshare record "Events" lists license CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/); each record is one ball touch with 7 event types (pass, foul, shot, duel, free kick, offside, touch); positions on a 0-100 scale; asks users to cite Pappalardo and Massucco, Scientific Data, 2019. CC BY 4.0 permits copying, redistribution and adaptation with attribution, so derived aggregates can be committed with citation. Caveat: the CC licence is stated by the dataset publisher; underlying Wyscout rights holders were not verified. — [figshare article 7770599 API](https://api.figshare.com/v2/articles/7770599); paper: [Nature Sci Data s41597-019-0247-7](https://www.nature.com/articles/s41597-019-0247-7) (page not fetched, redirect)
- PFF FC World Cup 2022 data: access requires filling a form; the blog post states no licence. "If you intend to publish your findings on social media, please tag us @PFF_FC." Terms are in the form/spec, which I could not read. — [PFF FC blog](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data)
- kloppy: BSD 3-Clause, "Copyright (c) 2020, PySport". Code licence only; says nothing about data. — [kloppy LICENSE](https://github.com/PySport/kloppy/blob/master/LICENSE)
- socceraction (SPADL, atomic-SPADL, VAEP, xT): MIT; "appreciate it if you include a link to this repo or cite our research" (Decroos et al. 2019; Van Roy et al. 2020). Page makes no statement on data licences of the providers it has loaders for. — [ML-KULeuven/socceraction](https://github.com/ML-KULeuven/socceraction)
- football-data.co.uk: no explicit licence; page states "NOT commerical or data training products using automated bots/scrapers/AI." and "All data provided by Football-Data are made available for the purposes of league match prediction only." Do not use for AI/training or commercial products; I would avoid it even for calibration unless the organisers agree. — [football-data.co.uk/data.php](https://www.football-data.co.uk/data.php)
- FBref (Sports Reference) data-use page returned HTTP 403, so terms are unverified. Understat: no terms page found by search; a soccerdata FAQ warns scraping tools are legally risky and breaching a site's terms matters. — [soccerdata FAQ](https://soccerdata.readthedocs.io/en/stable/_sources/faq.rst.txt)

### Inferences
- Safest hierarchy for the repo: (1) published paper figures (cite paper, quote the number); (2) Wyscout CC BY 4.0 aggregates computed locally; (3) SkillCorner season aggregate CSVs and StatsBomb aggregates, read locally only, commit only the derived numbers plus a citation; (4) do not use FBref/Understat/football-data.co.uk scraped data.
- StatsBomb 1.2.2 ("any analysis derived") is broad. A hackathon project is arguably non-commercial, but publication requires the StatsBomb logo, and a repo with its trademark conflicts with the "no third-party trademarks" hard rule. Recommendation: calibrate to peer-reviewed numbers that happen to use these datasets rather than touching StatsBomb data directly.
- Calibration provenance file should record: source, version/date, licence name, how the number was derived, and "raw data not committed".

### Gaps
- The current StatsBomb README may link to a newer licence than the LICENSE.pdf read here; confirm on the repo today.
- SkillCorner and Metrica data licence terms (beyond a credit request) not found; SkillCorner MIT text not read.
- PFF form terms, FBref data-use terms and Understat terms not retrieved.
- Wyscout provenance for CC BY claim not independently verified.

## Q2. Published reference distributions

### Takeaway
I verified only a handful of figures to a primary source (injury incidence, lnRMSSD variability, Dixon-Coles reference). Most match-statistic benchmarks (shots, xG per shot, pass completion, PPDA, running distances, late-game decline) could not be verified in this session; the generator should take them from the cited papers named below after a direct read, not from this note.

### Cited Findings
- Injury incidence, professional European football (UEFA Elite Club Injury Study, 23 teams, 2001-2008, 4,483 injuries over 566,000 h): overall 8.0 per 1,000 h; match 27.5 per 1,000 h; training 4.1 per 1,000 h (p<0.0001); thigh strain the most common subtype at 17%; match incidence rose within both halves. — [Ekstrand, Hagglund, Walden, BJSM 2011;45:553](https://bjsm.bmj.com/content/45/7/553) (figures confirmed in search abstract; page itself returned 403)
- Earlier UEFA Champions League study reported different rates (about 30.5 per 1,000 match h and 5.8 training), so do not mix the two. — same search result
- HRV: lnRMSSD typical error about 12%; smallest worthwhile change about +3% for resting vagal indices; day-to-day CV 10-20% under varying training load. — [Buchheit, Frontiers in Physiology 2014;5:73](https://pmc.ncbi.nlm.nih.gov/articles/PMC3936188/)
- Rugby union: intraday CV of 2-min lnRMSSD about 4%, interday about 7.7%. — [Nakamura et al. via search summary](https://scholars.georgiasouthern.edu/en/publications/intraday-and-interday-reliability-of-ultra-short-term-heart-rate-/)
- Position effects on running: in an EPL optical-tracking study, position was the only significant predictor of high-speed and sprint distance in possession; wingers highest, centre-backs lowest. — [Morgans et al., Biology of Sport 2025;42(3), DOI 10.5114/biolsport.2025.147011](https://repositorio.ipsantarem.pt/entities/publication/8bcaff81-dc71-4ed9-9ac3-824334021b17) (summary only; numbers not read)
- Midfielders cover significantly more total distance than defenders or forwards (300 outfield players, Spanish top flight). — [Pigozzi/Di Salvo, Int J Sports Med 2007;28:222](https://www.thieme-connect.de/products/ejournals/abstract/10.1055/s-2006-924294)
- Relative vs generic speed thresholds EPL 2 seasons: [PMC11474994](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11474994/) (numbers not extracted; read the position tables).
- PPDA: lower PPDA means more pressure; it is not game-state adjusted (a leading team sits deeper, so PPDA rises). Gives no numeric league range. — [StatsBomb blog archive](https://blogarchive.statsbomb.com/articles/soccer/premier-league-after-7-games-how-have-teams-pressed/)
- Goals model: Dixon and Coles (1997), JRSS-C 46:265-280, English league and cup 1992-95; independent Poisson (Maher 1982) with a low-score correction for 0-0, 1-0, 0-1, 1-1 (parameter rho) and exponential time decay (xi). Secondary sources only. — [Lancaster eprint](https://eprints.lancs.ac.uk/id/eprint/19492); [penaltyblog docs](https://penaltyblog.readthedocs.io/en/latest/models/overview.html)

### Inferences
- Use injury rates as an expected-value anchor: for a 25-player squad training about 10 h/week and playing about 2 h of matches per fortnight, 4.1 and 27.5 per 1,000 h imply a handful of time-loss injuries per season; validate generator output falls near that and that match hours produce roughly 6-7x training rate per hour.
- For HRV, simulate day-to-day lnRMSSD with player baseline plus noise whose CV is a few percent to about 10%, and plant SWC-sized shifts (about 3%) after load spikes. Treat the 3% SWC as a sensitivity target rather than a hard truth.
- UNVERIFIED background values to confirm before use: average shot xG about 0.09-0.11; penalty about 0.76-0.79; headers about 0.07-0.10; roughly 25 total shots (both teams) per match in top leagues; pass completion about 80-85% overall and lower in the final third; total distance about 10-12 km per outfield player with midfielders highest; high-speed running (above 19.8-21 km/h) several hundred metres to about 1 km, sprint distance around 200-300 m; typical PPDA about 8-14 across a league. Sources to check: Pappalardo et al. 2019 (Sci Data), Di Salvo 2007, Bush et al. 2015 (Human Movement Science), StatsBomb/Opta published leaderboards, Rampinini 2007 for late-game decline.

### Gaps
- No verified numbers for shots per match, xG per shot by type, pass completion by zone, PPDA range, sprint/HSR per position, distance per half, late-game decline, match heart-rate load (typical figures in literature: about 85% of HRmax mean, UNVERIFIED). Searches returned no usable snippets; Bush et al. 2015 and Rampinini et al. 2007 were not located.
- Smallest worthwhile change defined as 0.5 SD: not confirmed in this session (only the 3% figure above).

## Q3. Generation techniques and what is implementable in a day

### Takeaway
Layer simple parametric models: a Poisson/Dixon-Coles goal model for the scoreline, event-rate models consistent with it for shots/xG, a Banister two-component model for fatigue, and a Gaussian latent-factor model (Cholesky on correlation matrix) for sleep, HRV, output and injury risk. All run in stdlib or numpy in under a day. Learned generative models and RL environments are heavier and have licence implications.

### Cited Findings
- Google Research Football can serve as a simulator: Radke and Tilbury (arXiv 2503.19809, March 2025) collect "simulated soccer tracking data" in a schema resembling real tracking data, with extraction of high-level features and events, to ease the shortage of public tracking data. The paper is CC0 on arXiv; licence of the environment or released data was not stated on the abstract page. — [arXiv 2503.19809](https://arxiv.org/abs/2503.19809)
- GenTac (arXiv 2604.11786, April 2026): diffusion-based framework that learns from historical tracking data and samples long-horizon trajectories; also generalises to other sports. — [alphaxiv](https://www.alphaxiv.org/abs/2604.11786)
- PlayGen-MoG (arXiv 2604.02447, 2026): American football plays from a mixture-of-Gaussians head; SportsNGEN (arXiv 2403.12977, 2024): transformer generator trained mainly on tennis tracking. — [emergentmind](https://www.emergentmind.com/papers/2604.02447); [arXiv 2403.12977](https://arxiv.org/html/2403.12977v1)
- I found no 2025 diffusion paper specifically on synthetic football tracking (search was limited).
- Dixon-Coles: see Q2 for parameters and references.

### Inferences
- Recommended stack (all stdlib/numpy, about a day):
  1. Team strength: attack/defence parameters, home advantage; match goals via Poisson with the Dixon-Coles tau correction (rho slightly negative) and optional time-decayed form.
  2. Shot generation: draw shots count so that sum of shot xG per team matches the lambda from step 1 (xG conserved to goals in expectation); shot type mix (open play, header, penalty, set piece) with type-specific xG; goals as Bernoulli(xG) conditioned on the scoreline (or draw score first, then allocate shots, so events always sum to the score).
  3. Possession chains: Markov chain over zones (about 12-18 pitch zones) with pass-success rate by zone; calibrate to published zone pass-completion once verified.
  4. Fatigue/load: Banister impulse-response, performance(t) = p0 + k1*sum w(s) e^{-(t-s)/tau1} - k2*sum w(s) e^{-(t-s)/tau2}, with typical tau1 about 40-60 days and tau2 about 7-15 days (UNVERIFIED parameter ranges; Banister 1975, Busso 2003); within-match output decay as a function of cumulative load, plus late-half fall in sprint count.
  5. Correlated variables: latent factor "readiness" = f(sleep, prior load) -> HRV (lnRMSSD) -> match output -> injury hazard; generate with a Gaussian copula or simple linear-Gaussian structure and a logistic hazard for injury.
  6. Agent-based tick engine: you already have one; keep it and condition sprint/speed on position and fatigue state rather than adopting Google Research Football.
- Learned generative models (diffusion, transformers) need real tracking data for training, which conflicts with the licences in Q1 and the hard rules. Not recommended.
- Critical power / W' balance is optional and mostly cycling/running; skip unless a drill needs it.

### Gaps
- No Banister parameter values for football were verified; no source for copula parameters.
- GRF licence (Apache 2.0, UNVERIFIED) and whether its output can be redistributed was not checked.

## Q4. Consistency checks to add

### Takeaway
Encode invariants as asserts in the generator (cross-table conservation), add distribution tests against the cited reference values, fix seeds, and keep a ground-truth file listing planted effects. These come from design practice rather than a literature source; no external citation was needed.

### Cited Findings
- Dixon-Coles low-score correction implies the scoreline distribution should reproduce an excess of 0-0 and 1-1 relative to independent Poisson; a test can check this. — [Wikipedia summary](https://en.wikipedia.org/wiki/Statistical_association_football_predictions)
- Injury rate test: match 27.5 vs training 4.1 per 1,000 h. — [Ekstrand 2011](https://bjsm.bmj.com/content/45/7/553)

### Inferences
- Conservation invariants:
  - count of goal events in match_events == score in the match table, for both teams; sum shot xG within a tolerance of expected goals.
  - tracking minutes per player == minutes in lineup/substitutions; no tracking after a red card or substitution; total distance == sum of 5-min bins; sprint distance <= high-speed distance <= total distance in every bin; heart rate between resting and max; no speed above human max (about 10-12 m/s).
  - injury date falls in a window where the player has training or match records; player_status "injured" days match injury start/end; no match minutes while injured.
  - wearable_daily sleep/HRV exist for each active player-day; training_hr aggregates agree with training_sessions load.
- Distribution tests: Kolmogorov-Smirnov or simple quantile bands against published means; check injury rate per 1,000 h, home-win rate, goals per match mean, shots, pass completion by zone.
- Determinism: one seeded `random.Random` instance per table/entity (derive from master seed + entity id) so that adding a table doesn't shift others; CI test that the same seed gives identical SHA-256 of CSVs.
- Planted effects with ground truth: write `ground_truth.json` (effect names, sizes, injection mechanism, seed) kept outside the participant-facing data, with a documented effect size such as "each 10% drop in lnRMSSD below baseline raises next-7-day injury hazard by X".
- Use calibration provenance per parameter: value, source, licence, date, derivation.

### Gaps
- No external standard for synthetic sports-data validation was found; the above is recommended practice.

## Q5. Pitfalls and disclosure

### Takeaway
Planted effects will be recovered by any competent model, so results measure the generator, not football. Disclose it everywhere, and avoid designs where the answer is a trivial function of a leaked column.

### Cited Findings
- Radke and Tilbury frame simulated tracking data as a stand-in for scarce public data, i.e. for building and testing models, not as evidence about real football. — [arXiv 2503.19809](https://arxiv.org/abs/2503.19809)
- StatsBomb agreement states that conclusions from its data "are not necessarily the opinions or analytical insights of StatsBomb", and requires accreditation of any published analysis; the same logic implies synthetic outputs must not be attributed to a provider whose data only calibrated aggregates. — [LICENSE.pdf](https://raw.githubusercontent.com/statsbomb/open-data/master/LICENSE.pdf)

### Inferences
- Leakage risks: (a) injury label generated from a column that is also a feature (for example hazard computed from HRV and HRV given to the model), making AUC unrealistically high; use noisy proxies and keep the latent state hidden; (b) the same latent factor driving several tables so that any pair correlates; (c) generator parameters equal to the "findings" the challenge expects; (d) post-event columns (injury_type, days_out) leaking labels; (e) time leakage from random rather than chronological splits.
- Add label noise, unexplained variance (planted effects explain, say, 5-15% of variance), and a few null relationships (decoys) so that participants can be told which is which after the event.
- Disclosure: banner in README, dataset card and every dashboard ("synthetic data, fictional players, calibrated to published aggregates; not evidence about real players or clubs"); list calibration sources with licences; keep statement that no raw third-party data is committed.
- Do not name providers in a way that implies endorsement or use their logos, to respect the no-trademark rule; cite papers instead.

### Gaps
- No literature found specifically on leakage in synthetic sports benchmarks; points above are practitioner reasoning.
