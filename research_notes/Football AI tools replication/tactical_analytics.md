# Tactical analytics and decision-support tools used by professional football clubs (as of 2026-10-20)

Evidence grades: [P] peer-reviewed or primary paper/author; [C] club or league primary statement; [V] vendor marketing (weak); [S] secondary press or blog (medium/weak). Anything older than 2023 is marked DATED. Research depth was limited (about 20 tool calls); several vendor pages and the Nature paper itself could not be fetched, so many items are flagged as gaps rather than filled from memory.

## 1. Google DeepMind TacticAI (Liverpool collaboration, Nature Communications 2024) and follow-ups through 2026

### Takeaway
TacticAI is an offline, set-piece-only (corner kick) assistant: a geometric-deep-learning model that predicts the receiver and shot outcome, retrieves similar past corners, and generates adjusted player positions. Its only strong evidence is a blind expert preference study (about 90% preferred); no on-pitch trial was reported in 2024. A June 2026 open-play extension with Palmeiras exists only in secondary, partly promotional coverage.

### Cited Findings
- Announced 19 March 2024 as an "AI assistant for football tactics", developed with Liverpool FC over a multi-year collaboration, published in Nature Communications — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/) [C/P]
- Three functions: predict corner outcomes (receiver, shot or no shot); retrieve similar past routines so analysts need not rewatch games; generate adjusted player positions to raise or lower shot probability (e.g. reposition defenders) — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/)
- Architecture: each corner is a graph, players are nodes (features: position, velocity, height), edges encode relations; a graph neural network does message passing; a variant of a Group Equivariant Convolutional Network processes all four reflections (original, H-flip, V-flip, HV-flip), exploiting the approximate symmetry of the pitch — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/)
- Trained and tested on 7,176 Premier League corner kicks supplied by Liverpool — [The Conversation](https://theconversation.com/can-ai-improve-football-teams-success-from-corner-kicks-liverpool-and-others-are-betting-it-can-225894), [Scimex/other coverage via search](https://www.scimex.org/newsfeed/could-artificial-intelligence-be-the-future-of-soccer-coaching) [S]
- DeepMind notes data scarcity: only about 10 corners per Premier League match per season; inputs are player tracking data only; future work mentioned on multimodal inputs — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/)
- Retrieval: top-1 retrievals judged relevant by football experts 63% of the time vs a 33% baseline based on player-position similarity — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/)
- Coach evaluation: blind case study; Liverpool experts could not tell generated setups from real corners and preferred the model's suggestions over the original setup 90% of the time; coverage reports five experts and 50 setups with 45 chosen — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/); [Gulf News summary](https://gulfnews.com/sport/football/googles-new-ai-for-corner-kick-tactics-gets-liverpool-approval-1.1710873075313) (the 5-expert/50-setup detail is from a search snippet, not read in full)
- Press caveat: no players had tried the suggestions on the pitch; an outside expert said value could only be shown on the field — [Business Insider NL (search snippet)](https://www.businessinsider.nl/google-deepmind-wants-to-make-ai-a-part-of-soccer/)
- The Conversation: AI cannot make real-time decisions (e.g. taking a corner quickly on a lapse); opponents could counter AI-suggested setups; unclear if useful in open play or tactical substitutions; the author hears industry people say AI should inform, not make, decisions (unnamed) — [The Conversation](https://theconversation.com/can-ai-improve-football-teams-success-from-corner-kicks-liverpool-and-others-are-betting-it-can-225894)
- Earlier DeepMind-Liverpool work: Game Plan (2021, DATED) and Graph Imputer (2022, DATED; predicts off-camera player movement) — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/)
- 2026 follow-up (UNVERIFIED, secondary only): a write-up dated 11 June 2026 says DeepMind extended TacticAI to open play with Palmeiras, predicting dynamics up to 8 seconds ahead, with predictive, generative and retrieval modules, and claims Palmeiras is first to use it in real time during matches. The article gives no metrics, no peer-reviewed paper, no deployment details, and is partly promotional — [ecosistemastartup.com](https://ecosistemastartup.com/?p=88314); also repeated by [pasqualepillitteri.it](https://pasqualepillitteri.it/news/5077/google-tacticai-deepmind-calcio) (search result, mirrors the same story)

### Inferences
- The genuinely replicable ideas are the graph representation of a set-piece, retrieval of similar situations, and a "counterfactual reposition" suggestion judged by an expert, not the trained model itself (no access to real tracking data or the paper's weights).
- The 90% figure is expert preference, not outcome improvement, and should be quoted that way in the pitch.
- Treat the Palmeiras claim as unconfirmed; do not cite it as fact in the submission without checking DeepMind's own channel.

### Replicability verdict
- TacticAI-style (graph model on synthetic corners): partial. A simple "retrieve similar synthetic set-pieces and propose a reposition" agent is doable in days; a trained GNN on synthetic data would only learn the generator's own rules.

### Gaps
- Could not fetch the Nature Communications paper (paywall redirect): receiver top-k accuracy, shot F1 and exact expert protocol not confirmed from the primary source.
- No DeepMind blog or paper for the 2026 Palmeiras work was found.
- No other 2025-2026 TacticAI follow-up found.

## 2. Tracking and event-data platforms: tactical features and live vs post-match use

### Takeaway
Tracking is captured live in every Premier League ground (Second Spectrum, Genius Sports), but analyst-grade tactical metrics are mostly consumed pre-match and post-match; live on-bench use is limited to coach-reviewed data, video and a few tools (e.g. Man City's SAP app). Vendor feature claims are mostly marketing; I found few independent evaluations.

### Cited Findings
- Second Spectrum (Genius Sports) is the official Premier League optical tracking provider, installed in every ground, capturing sub-second positions of players and ball; FIFA EPTS validated with median latency 0.859 s — [BusinessWire 2022](https://www.businesswire.com/news/home/20221026005956/en), [Broadcast](https://www.broadcastnow.co.uk/tech-innovation/genius-sports-second-spectrum-gets-fifa-approval/5176636.article) [V/S]
- Premier League Insight Feed pairs Second Spectrum tracking with Stats Perform event data, exposing metrics such as shot velocity, pass probability and pressure on the ball — [Stats Perform](https://www.statsperform.com/?p=21977) [V] (aimed at fans/broadcast; not confirmed as club tactical tooling)
- Brentford analysts use Genius Sports Performance Studio (video + tracking + event data, GeniusIQ engine, multi-game video tool, several seasons of PL data searchable) — [Training Ground Guru](https://trainingground.guru/how-clubs-like-brentford-turn-data-into-an-advantage/) [S]
- SkillCorner derives 10 Hz player tracking from broadcast video; Game Intelligence detects and classifies 10 off-ball run types (overlap, underlap, run in behind, come short, etc.) and the passing options they create, across 75+ competitions — [SkillCorner](https://skillcorner.com/articles/game-intelligence-off-ball-run-types), [SkillCorner passing options](https://skillcorner.com/articles/metric-explainer-passing-options-engaging-the-second-last-line-of-pressure) [V]
- A third-party comparison blog says several PL and Championship clubs use SkillCorner alongside in-stadium tracking, and that SkillCorner publishes pressing intensity, line height/depth metrics — [kiqiq.com](https://kiqiq.com/blog/understanding-football-data-providers) [S, low reliability, unverified against SkillCorner pages]
- Hudl StatsBomb: On-Ball Value (OBV) scores each event by change in probability of scoring and conceding, trained on StatsBomb xG, 140+ competitions; also values defensive and goalkeeper actions — [Hudl](https://www.hudl.com/blog/introducing-on-ball-value-obv), [StatsBomb archive](https://blogarchive.statsbomb.com/articles/soccer/on-ball-value-obv-in-the-2020-21-premier-league/) [V]
- Live-use evidence: Liverpool's Spearman says live tracking has roughly a 7-minute lag and accuracy issues versus reprocessed post-match data, and that only a small number of leading PL teams use pitch-control-type models in practice; tablets on the bench are allowed (since the 2018 World Cup) — [Training Ground Guru, Spearman interview](https://archive.trainingground.guru/articles/william-spearman-how-liverpool-create-pitch-control) [S/P-adjacent; interview date unclear, possibly DATED]
- Typical matchday workflow: two analysts live-code from the stand, the head analyst relays to the dugout and goes to the dressing room at half-time — [Training Ground Guru](https://archive.trainingground.guru/articles/how-video-on-the-bench-will-transform-coaching) (via search summary) [S]
- Rules: IFAB allows small hand-held electronic devices in the technical area for coaching/tactics/welfare; footage may not be shown to players or used to contest decisions — [Training Ground Guru](https://archive.trainingground.guru/articles/laptop-coaches-analysts-to-come-into-the-open-at-world-cup), [FIFA 2017 trial](https://www.fifa.com/news/player-stats-tablet-to-be-tested-live-at-fifa-confederations-cup-2017--2899741) (via search summary) [S]

Per-tool table (what it does / evidence / data needed / replicability):
- Second Spectrum tracking + analytics: positional data, pitch-control and off-ball style analytics for clubs; evidence = official PL provider, FIFA-validated latency, but no public tactical-impact study found; needs optical tracking at 25 Hz. Verdict: partial; our tick engine already emits positions, so metrics computed on top are easy, but the product's learned models are not reproducible.
- SkillCorner: broadcast-video tracking, off-ball run classification, pressing and line metrics; evidence = vendor articles only; needs tracking trajectories. Verdict: partial; run-type classification (heuristic on velocity vectors relative to defensive line) is easy on synthetic tracks; the video-to-tracking part is not feasible.
- Hudl / StatsBomb (OBV, 360 freeze frames, IQ): possession value, event data with positional snapshots; evidence = vendor + public methodology posts; needs event data. Verdict: partial; a simplified OBV/xT from synthetic events is easy, calibration is circular.
- Opta / Stats Perform, Wyscout, PFF, Metrica, Sportlogiq: not researched in depth (see Gaps). Verdict: unknown from this session; event-data-derived stats (xG, passing networks, pressing counts like PPDA) are easy to derive from our event bus.
- Man City SAP Challenger Insights live touchline app: see section 5.

### Inferences
- A realistic claim for the hackathon is "live at the speed the data allows": the product should be framed as event-driven alerts for the coach, mirroring how the stand analyst relays to the bench, rather than as autonomous recommendations.
- The 7-minute live lag Spearman cited (possibly dated) suggests real clubs do not rely on fresh tracking models mid-match; our simulated tick data would be more "live" than reality, so state this honestly.

### Gaps
- No primary documentation fetched for Second Spectrum, PFF, Metrica, Sportlogiq, Opta/Stats Perform tactical products, Wyscout or Hudl Sportscode; pressing metrics per vendor not confirmed.
- Which features run live versus post-match per vendor is not documented publicly in what I found; the Spearman and City sources are the only live-use evidence.
- Whether Sportlogiq is used in football (it is mainly known for ice hockey) was not checked.

## 3. Pitch control, xT, OBV/EPV and similar models: methods and reimplementation

### Takeaway
All of these are published and reimplementable on simulated tracking or event data; pitch control (physics-based, Spearman 2018) and xT (grid Markov model) are the cheapest. EPV and OBV require learned models and are only meaningful if the synthetic data has realistic structure.

### Cited Findings
- Spearman: pitch control = probability that a player can control the ball if it were at a given location; physics-based using player max speed/acceleration, compares arrival times (not raw distances), adds uncertainty, accounts for ball travel time, and "control force" (about 1 s to control a touch); outputs include pass-reception probability per player and an off-ball scoring map combining pitch control with scoring probability — [Training Ground Guru, Spearman](https://archive.trainingground.guru/articles/william-spearman-how-liverpool-create-pitch-control); Spearman's paper is "Beyond Expected Goals" (MIT SSAC 2018; DATED), built as a weekend project per [Liverpool FC](https://www.liverpoolfc.com/news/first-team/450917-the-weird-journey-of-william-spearman-liverpool-s-lead-data-scientist)
- Open implementation of Spearman's model in Python by Laurie Shaw (Metrica sample data) — [Metrica pitch control repo](https://github.com/anenglishgoat/Metrica-pitch-control) (the repo shown is a derivative/port of the same approach)
- Fernandez and Bornn "Wide Open Spaces" (2018, DATED): player influence areas as bivariate normal densities whose mean and covariance shift with velocity, direction and distance to ball; pitch control as a continuous team-level quantity plus pitch value — [project summary (search result)](https://math-projects.elte.hu/media/works/388/report/Project-Work-Balazs_pACbvVD.pdf) [S]
- Fernandez, Bornn and Cervone (2021, Machine Learning): decomposed EPV into pass, ball-drive and shot components learned from tracking data, with calibrated models — [mlanthology](https://mlanthology.org/mlj/2021/fernandez2021mlj-framework) [P]
- xT: introduced by Sarah Rudd (2011, DATED), popularised by Karun Singh (2018, DATED); pitch grid values from shot probability, goal probability and zone-to-zone transition probabilities; actions get credit by change in zone value; socceraction implements it on a 16x12 grid — [socceraction docs](https://socceraction.readthedocs.io/en/stable/documentation/valuing_actions/xT.html)
- Empirical caution: six PL seasons study found home teams control about 2.9% more pitch and pitch control correlates only weakly with xG difference — [IFISC publication page](https://ifisc.uib-csic.es/es/publications/measuring-the-pitch-control-of-professional-footba) [P-adjacent]; Spearman likewise: more control does not automatically mean better performance; without further models it is "little more than a visual tool" — [Training Ground Guru](https://archive.trainingground.guru/articles/william-spearman-how-liverpool-create-pitch-control)
- OBV: change in probability of scoring and conceding attributed to each event — [Hudl](https://www.hudl.com/blog/introducing-on-ball-value-obv)

### Inferences (replicability verdicts)
- Spearman pitch control: easy. A few dozen lines of NumPy on the engine's player positions and velocities; fits per-tick evaluation and drives triggers like "opponent changes shape" (control map shift).
- Voronoi / Fernandez-Bornn influence-area control: easy. Same inputs, even simpler.
- xT grid: easy for the algorithm (value iteration on a transition matrix); partial for meaning, since values fitted on synthetic events only reflect the generator, so ship a fixed published-style grid or label it as illustrative.
- EPV (Fernandez et al.): not feasible to learn meaningfully in 5 days on synthetic data; a hand-built approximation (pitch control x location value) is partial.
- OBV: partial/not feasible to reproduce; use xT as a stand-in and say so.

### Gaps
- I did not retrieve the original Spearman or Fernandez-Bornn PDFs; the descriptions come from secondary summaries and author interviews.
- Exact parameter values (e.g. Spearman's reaction time, tti sigma) not confirmed here.

## 4. Real-time AI substitution or formation recommendation during play

### Takeaway
I found no evidence that any club uses AI to recommend substitutions or formations live during matches in a validated, documented way. What exists: academic prototypes, one 2018 vendor feature (SAP/Man City, qualitative), and a 2026 unverified Palmeiras claim. Absence of public evidence is not proof of absence, since clubs keep tools private.

### Cited Findings
- Fuzzy-logic substitution decision support system (Wharton Sports Analytics Journal, Fall 2025): combines performance, fatigue, age, disciplinary risk to give real-time substitution priorities; rule-based, not validated in live matches — [Wharton](https://wsb.wharton.upenn.edu/wp-content/uploads/2025/12/FARIAS_AI_Assisted_Substitution_Decisions__A_Fuzzy_Logic1_Approach_to_Real_Time_Game_Management-1.pdf), arXiv companion [2512.04480](https://arxiv.org/abs/2512.04480v1) [P-adjacent]
- UWA research (IEEE ICWS 2022): infers opponent tactics from events to a given minute and recommends substitutes from live player ratings; academic — [UWA repository](https://research-repository.uwa.edu.au/en/publications/temporal-match-analysis-and-recommending-substitutions-in-live-so/) [P]
- Kröckel (2017, DATED): design-science proposal noting tracking data had not been used for in-game decisions — [FAU CRIS](https://cris.fau.de/publications/121768064) [P]
- Man City SAP Challenger Insights (2018, DATED): adapted for live touchline use; live opponent insights, set-piece planning, communicating tactical changes, and predictions of best substitution timing; no outcome evidence, only qualitative player quotes; Kompany said players "love using" it — [Inside World Football](https://insideworldfootball.com/?p=109514), [Sports Business Daily](https://www.sportsbusinessdaily.com/Daily/Issues/2018/12/18/Technology/manchester-city-sap-bring-real-time-technology-soccer-pitch.aspx) [V/S]
- The Conversation: unclear whether TacticAI is useful for tactical substitutions or open play — [The Conversation](https://theconversation.com/can-ai-improve-football-teams-success-from-corner-kicks-liverpool-and-others-are-betting-it-can-225894)
- Palmeiras 2026 real-time claim: see section 1, unverified — [ecosistemastartup.com](https://ecosistemastartup.com/?p=88314)

### Inferences
- Our product (rules firing triggers, agents proposing options, coach decides) matches the consensus stance that AI informs and the coach decides; this is defensible, but "real clubs already do live AI substitutions" is not a claim we can support.
- Safest framing: closest analogues are the stand analyst relaying to the bench, and the City app's substitution-timing prediction; both human-in-the-loop.

### Gaps
- No documented live formation-recommendation tool at any club found. No independent validation of the SAP substitution-timing feature. Palmeiras claim not verified.

## 5. Documented club cases

### Takeaway
Public detail is thin and skewed to recruitment and set pieces. The best-documented tactical cases are Liverpool (pitch control, TacticAI), Man City (SAP touchline app, 2018) and Brentford (Genius Performance Studio, set-piece focus, 2015 DATED). Arsenal, Brighton, Real Madrid and Bayern yielded nothing usable.

### Cited Findings
- Liverpool: Spearman (lead data scientist) built pitch control models; tablets on the bench; used pre-match against opponents, post-match for own performance — [Training Ground Guru](https://archive.trainingground.guru/articles/william-spearman-how-liverpool-create-pitch-control); TacticAI partnership — [DeepMind blog](https://deepmind.google/blog/tacticai-ai-assistant-for-football-tactics/)
- Manchester City: SAP Challenger Insights used before matches for game plans, at half-time for adjustments, and afterwards for review; analysts load plans onto tablets — [SVG Europe](https://www.svgeurope.org/blog/news-roundup/manchester-city-and-sap-team-up-to-bring-technology-to-the-touchline/), [Inside World Football](https://insideworldfootball.com/?p=109514) (2018, DATED)
- Brentford: Genius Sports Performance Studio; set-piece lounge where monthly staff meetings review stats and clips to devise routines (2015, DATED); first-team analysis role includes opposition reports and databases — [Training Ground Guru](https://trainingground.guru/how-clubs-like-brentford-turn-data-into-an-advantage/), [These Football Times 2015](https://thesefootballtimes.co/2015/08/31/is-brentfords-analytics-revolution-the-future-of-football-in-england/) [S]
- Palmeiras: claimed TacticAI follow-up partner (unverified) — [ecosistemastartup.com](https://ecosistemastartup.com/?p=88314)

### Inferences
- The recurring pattern is: pre-match opponent dossiers and set-piece planning (high maturity), half-time adjustment (medium), live in-play AI (low/none documented). Our trigger-and-agent design maps naturally to half-time and pre-match style outputs delivered at minute-level cadence.

### Gaps
- Arsenal, Brighton, Real Madrid, Bayern: nothing reliable found in the searches run (Brighton result was a low-quality blog; Arsenal returned nothing). Needs targeted searches (e.g. Arsenal's set-piece coach Nicolas Jover and Arsenal's use of data, Brighton and Tony Bloom's Starlizard, Bayern and SAP).
- The Athletic, Coaches' Voice, and MIT SSAC talk archives were not searched directly.
- Man City and Brentford sources are 2015-2018 and DATED; current (2026) setups are not documented here.
