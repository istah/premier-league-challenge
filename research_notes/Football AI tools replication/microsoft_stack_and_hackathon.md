# Microsoft stack and "Inside the Game" hackathon: sport patterns, rules, and verified facts (as of 2026-10-20)

Method note: ~20 tool calls. Learn pages fetched carry their own `ms.date` / `updated_at`, quoted below. Search-engine summaries and third-party pages are marked UNVERIFIED where they are the only source.

## 1. Official hackathon page and rules

### Takeaway
The official rules document was NOT retrievable. Microsoft Reactor pages confirm the event exists and its brief, but contain no dates, categories, judging criteria, prizes or team size. A third-party catalog (Stavleak) lists "Best Multi-Agent System / Best Multi-Agent Orchestration" as a special nomination and gives team size up to 4, but it is not official. The submission deadline appears to be 27 Oct 2026 11:59 PM PT (one week from today).

### Cited Findings
- The Reactor series "Inside the Game: Developer Hackathon", "presented by Microsoft and the Premier League", brief: build AI-driven solutions that "transform synthetic football events into explainable match intelligence" for broadcast and streaming. The page lists no rules, categories, judging, prizes, team size or submission link; contact reactor@microsoft.com. — [Reactor series S-1709](https://developer.microsoft.com/en-us/reactor/series/S-1709/)
- Reactor livestream "Build AI-powered soccer insights apps with AKS and ACA", 14 Oct 2026 16:00-17:00 UTC, speaker Brian Benz; reference architecture for AI apps/agents; example scenarios: team play styles, counterattacks, player performance patterns; on-demand recording exists. — [Reactor event 27536](https://developer.microsoft.com/en-us/reactor/events/27536/)
- Series lists more sessions: Episode 1 AI Fundamentals (26 Oct, 15:00 UTC), Episode 2 Generative AI (27 Oct, 15:00 UTC), "AI Genius" session (28 Oct, 04:00 UTC). — [Reactor event 27536](https://developer.microsoft.com/en-us/reactor/events/27536/)
- Registration landing page exists but fetch returned only "Registration"; no content retrieved. — [events.microsoft.com landing](https://events.microsoft.com/flow/microsoft/plmshackathon/registration/page/landing)
- Search summary (UNVERIFIED, from a Microsoft MVP post on X): runs 29 Sep to 20 Oct 2026, worldwide, free, about $50,000 total cash pool plus tickets, submission deadline 27 Oct 2026 11:59 PM PT. — [MVP X post](https://x.com/MVPAward/status/2110415336897990707) (snippet only, not opened)
- Third-party catalog (UNVERIFIED, Russian-language, says official rules are on GitHub): solo or teams up to 4; themes real-time match analysis, automatic description of key moments, AI explainability, synthetic dataset creation, multilingual stories; special nominations Best Use of Microsoft Foundry Project, Best Enterprise Solution, Best Multi-Agent System / Multi-Agent Orchestration, Best Azure Cloud Native Integration; prizes per participant: 1st e-gift card $4,000 + match ticket $1,000 + store voucher $50, 2nd $2,500 + $1,000 + $50, each nomination $1,500 + $50; one main prize plus one nomination max; no formal judging weights, jury assesses "meaningful use of the stack"; dates in Astana time: contest/submissions open 6 Oct 21:00, registration deadline 21 Oct 00:00, submission deadline 28 Oct 11:59, judging ends 11 Nov, winners by 21 Nov. 28 Oct 11:59 Astana (UTC+5) equals 27 Oct 23:59 PDT, consistent with the MVP post. — [Stavleak](https://www.stavleak.com/ru/catalog/microsoft-premier-league-hackathon-2026)
- Data policy as stated by participant repos (not official): synthetic, football-realistic data only; no real Premier League data. Public participant repos show the brief as a five-stage pipeline (ingest, interpret, explain, render, personalize) and the NDJSON event fields `event_id, match_id, sequence, period, clock_s, type, team_id, player_id, score` with event types pass/carry/shot/tackle/interception/pressure/possession_change etc. — [bikilath/inside-the-game](https://github.com/bikilath/inside-the-game); [AmirMirj repo](https://github.com/AmirMirj/Inside-the-Game-Developer-Hackathon) (tags "Real-time football analysis", "Innovation of football statistics")

### Inferences
- "Best Multi-Agent System" very likely exists as a category (third-party listing matches the user's context), but the exact wording, weights and eligibility must come from the official rules.
- Judges are told to weigh "meaningful use of the stack"; the brief stresses explainability, so a demo showing why an insight was produced (traces, evaluator scores, approval gates) fits.
- Registration deadline (21 Oct per Stavleak, Astana time) may be imminent or passed; check immediately.

### Gaps
- Official rules, judging criteria and weights, submission format (video? repo? length?), IP/licence terms, technology restrictions: not found. Confirm via the registration page (needs browser) and reactor@microsoft.com.
- Category list not confirmed from a Microsoft source.

## 2. Microsoft + sport case studies and reference architectures

### Takeaway
Only the Premier League partnership is supported by a Microsoft page: Azure infrastructure, Microsoft Foundry with an agentic architecture, a fan "Companion" assistant, near-real-time insights. I found no sourced NFL, NBA, F1 or football-club Fabric/Azure ML case study, and no Fabric RTI sports reference architecture, in this pass.

### Cited Findings
- Microsoft customer page: Premier League moving core infrastructure to Azure; Microsoft Foundry and "an agentic architecture" support near-real-time fan experiences; Premier League Companion described as "Your personalised AI assistant"; AI insights answer questions like all-time top scorers and current-season defensive stats using near-real-time data; Azure-powered live insights across digital and broadcast at key moments; Microsoft 365 Copilot used by staff. No dates on the page. — [Microsoft Premier League page](https://www.microsoft.com/en/customers/brand-collections/premier-league-innovations)
- Press coverage (secondary) says Companion handles open-text questions in the app/website, with multilingual and voice input planned, and calls the product "Azure AI Foundry" where Microsoft says "Microsoft Foundry" (naming drift). — [Windows Report](https://windowsreport.com/microsoft-becomes-the-ai-brain-behind-premier-leagues-digital-future/)
- A search summary mentions a motorsport team (Dener Motorsport) planning Fabric Real-Time Intelligence for in-race insights; page not opened, treat as UNVERIFIED. — search result summary only

### Inferences
- The Premier League story gives the demo narrative hook: Foundry + agents + near-real-time + personalization. Reuse that vocabulary.

### Gaps
- NFL (Surface/Teams), NBA, F1, club Fabric/Azure ML case studies: not found or not fetched. Search Microsoft customer stories directly.
- Any Fabric RTI sports/IoT reference architecture: not found.

## 3. Event Hubs -> Eventstream -> Eventhouse -> Activator: documented limits, status, cost

### Takeaway
Eventstream docs (updated 2026-09-29) list Azure Event Hubs as a standard source and Eventhouse and Activator as destinations, none labelled preview in the tables; stated limits are small: 1 MB message, 90-day retention, at-least-once delivery, minimum F4 capacity. No per-step dollar cost figure was retrieved; cost is capacity-based.

### Cited Findings
- Eventstream source list includes Azure Event Hubs (no preview label), custom endpoint (with Kafka protocol endpoints), sample data; preview labels appear on e.g. Azure Data Explorer, MQTT, HTTP, SQL operator. Destinations: Custom endpoint, Eventhouse (direct ingestion or event processing before ingestion), Lakehouse, Spark Notebook (Preview), Derived stream, Activator. Page `ms.date` 2026-09-02, `updated_at` 2026-09-29. — [Eventstreams overview](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview)
- Limits: max message size 1 MB; max retention 90 days; delivery guarantee at least once; "use eventstreams with at least four capacity units: F4". An Event Hubs namespace is auto-created when an eventstream is created. Schema-aware Eventstream is Preview. — [Eventstreams overview](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview)
- Activator destination prerequisites: Fabric capacity or Trial licence, Contributor+; each event must be a JSON dictionary with one key as unique object ID. Rules are created from the Eventstream Rules pane; actions include email or Logic App (page example). `ms.date` 2026-03-22. No preview banner in the fetched text. — [Add Activator destination](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/add-destination-activator)
- Activator: no-code event detection; "subsecond for stateless rules on streaming data"; aggregation rules depend on lookback window; actions include Teams, email, Power Automate, pipelines, notebooks, UDFs; "You only incur cost when activators are actively running", capacity-scoped, pay-as-you-go while rules run; a "Publish business event" action is marked preview; Activator on Fabric Warehouse SQL queries is preview; ontology entities preview. `ms.date` 2026-04-17, `updated_at` 2026-10-13. — [What is Fabric Activator](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction)

### Inferences
- Per your global Fabric rules: pace all ingest, no bursts. Event Hubs -> Eventstream with a synthetic replay should use a throttled sender (>=1s sleeps or a realistic match clock rate); one match is small, so steady-state CU is low, but state the CU profile in the demo notes.
- F4 minimum applies to eventstreams; a Fabric trial capacity is documented as acceptable for Activator destination.

### Gaps
- Exact CU rates per step (Eventstream, Eventhouse, Activator) and Event Hubs tier pricing: not retrieved. Check the Fabric capacity-consumption pages and Azure pricing.
- Activator Eventhouse limits (object ID count, lookback caps): see "Activator limitations" page, not fetched.

## 4. Fabric Activator on Eventstream: preview or GA?

### Takeaway
Not explicitly stated on the current Learn pages: neither the Activator introduction nor the Activator-destination page carries a preview banner, and the Eventstream overview table lists Activator without "(preview)" while labelling other items. That is consistent with GA but is an inference from absence; no GA announcement was retrieved.

### Cited Findings
- Eventstream overview marks several features "(preview)" but not the Activator destination. — [Eventstreams overview](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/overview)
- A search summary says the Eventstream release notes of Nov 2024 listed Activator destination as preview and a later blog says Activator reached GA (no date); UNVERIFIED snippets. — [What's new in Fabric event streams](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/whats-new) (not opened)

### Inferences
- Treat as GA for planning but verify in the portal (a preview tag would show on the destination) and in the "What's new" page before claiming "GA" in the submission.

### Gaps
- Definitive GA date/statement not found.

## 5. Microsoft Agent Framework: status, orchestrations, packages, approvals, hosting, observability

### Takeaway
As of 2026-10-20, Python `agent-framework` is 1.22.0 (released 2026-10-15, no pre-release suffix) and the five orchestrations (Sequential, Concurrent, Handoff, Group Chat, Magentic) are documented with stable names since Python 1.19.0. Docs do not carry a per-pattern preview label. Tool approval via `@tool(approval_mode="always_require")` is documented and exactly as you wrote it.

### Cited Findings
- PyPI: `agent-framework` 1.22.0, released Oct 15 2026, `pip install agent-framework`, Python 3.10-3.15 (3.10 deprecated, 3.11+ recommended). Related packages: `agent-framework-core` (includes workflows and orchestrations), `agent-framework-foundry`, `agent-framework-copilotstudio` (preview, needs `--pre`), `agent-framework-lab`. — [PyPI agent-framework](https://pypi.org/project/agent-framework/)
- GitHub releases: python-1.22.0 (Oct 15), 1.21.0 (Oct 8), 1.20.0 (Oct 2: native workflows hosted over Foundry Responses and Invocations; Foundry hosting redesigned around request-scoped agent factories, breaking), 1.19.0 (Sep 18: stable orchestration names); dotnet-1.25.0 (Oct 14). Packages named in notes include `agent-framework-orchestrations` and `agent-framework-foundry-hosting`. Many sub-packages still carry beta versions like `1.0.0b261015`. Python 1.21.0 warns against hosting a WorkflowAgent through the `agent=` shortcut. Python 1.22.0 redacts sensitive telemetry and has a persisted-record format change (do not mix pre-1.22 and 1.22 workers on one store). The page was read only up to character 100,000 of ~120,000. — [GitHub releases](https://github.com/microsoft/agent-framework/releases)
- Orchestrations page lists Sequential, Concurrent, Handoff, Group Chat ("Agents collaborate in a shared conversation"), Magentic ("A manager agent dynamically coordinates specialized agents"); orchestrations support human-in-the-loop via tool approval and request info. `ms.date` 2026-02-12, `updated_at` 2026-08-25. — [Orchestrations overview](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/overview)
- Concurrent (page `ms.date` 2026-10-15), Python: `from agent_framework.foundry import FoundryChatClient`; `FoundryChatClient(project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], model=os.environ["FOUNDRY_MODEL"], credential=AzureCliCredential())`; `chat_client.as_agent(instructions=..., name=...)`; `from agent_framework.orchestrations import ConcurrentBuilder`; `ConcurrentBuilder(participants=[a, b, c]).build()`; `.with_aggregator(callable)` custom aggregator; `intermediate_output_from=[...]` surfaces per-participant `"intermediate"` events; run with `await workflow.run(prompt)` then `events.get_outputs()`, or `workflow.run(prompt, stream=True)`. Default aggregator returns one `AgentResponse` with one assistant message per participant. — [Concurrent orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/concurrent)
- Tool approval (page `ms.date` 2026-10-15): `@tool(approval_mode="always_require")`; check `result.user_input_requests`; each has `.function_call.name/.arguments`; reply with `Message(role="user", contents=[req.to_function_approval_response(True|False)])` using the same `AgentSession`. Approval responses are bound to a pending request in the same session by default (security change); samples use `never_require` only for brevity. `create_harness_agent(...)` adds approval middleware with standing approvals. — [Tool approval](https://learn.microsoft.com/en-us/agent-framework/agents/tools/tool-approval)
- Foundry says tracing is OpenTelemetry-based, integrated with Azure Monitor Application Insights, and supports Microsoft Agent Framework among other frameworks (page `ms.date` 2026-10-15). — [Foundry observability](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability)

### Inferences
- Your plan (Concurrent for analysts + own routing table as orchestrator) is supported. A custom aggregator is the natural place to put a deterministic merge/ranking step.
- Hosting as Foundry Agent Service agents: the 1.20.0 release says Foundry-hosted native workflows exist, but the exact current hosting API and package (`agent-framework-foundry-hosting`) were not read in detail; treat hosting as unverified until run.
- Package names to verify with `pip index versions`: `agent-framework`, `agent-framework-foundry`, `agent-framework-orchestrations`, `agent-framework-foundry-hosting`.

### Gaps
- Per-pattern GA/preview labels: none found; the "is Magentic/Handoff GA" question is unanswered beyond "stable names since 1.19.0".
- Exact hosting recipe and Agent Framework -> Foundry tracing setup call (e.g. which `configure_*` function): not retrieved.
- A techstrong.ai article claims "1.0" orchestration stability; secondary, not verified.

## 6. Foundry agent evaluators

### Takeaway
Current Foundry docs (`ms.date` 2026-09-30, updated 2026-10-08) list: Task Completion (preview), Task Adherence (preview), Intent Resolution (preview), Tool Call Accuracy (no preview label), plus Tool Selection, Tool Input Accuracy, Tool Output Utilization, Tool Call Success, Task Navigation Efficiency, Customer Satisfaction (preview) and two composites. Groundedness is a RAG-quality evaluator, not on the agent list, but is usable with agentic inputs.

### Cited Findings
- Output is binary Pass/Fail (scaled 1-5 scores converted by threshold). Status per page: Task Completion (preview), Customer Satisfaction (preview), Task Adherence (preview), Intent Resolution (preview), Output Quality (preview, `builtin.output_quality`), Tool Use Quality (preview, `builtin.tool_use_quality`); Task Navigation Efficiency, Tool Call Accuracy, Tool Selection, Tool Input Accuracy, Tool Output Utilization, Tool Call Success have no preview label. Quality Grader is deprecated. — [Agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- Required inputs: Task Completion, Task Adherence, Intent Resolution: (`query`, `response`) or `messages`, optional `tool_definitions` (Task Adherence and Task Completion); all need parameter `deployment_name`. Tool Call Accuracy / Tool Selection: (`query`, `tool_definitions`) or (`messages`, `tool_definitions`), `response`/`tool_calls` optional. Tool Input Accuracy / Output Utilization: (`query`, `response`, `tool_definitions`) or (`messages`, `tool_definitions`). Tool Call Success: `response` or `messages`. Task Navigation Efficiency: (`actions` or `messages`) plus `expected_actions`, `matching_mode` in `exact_match | in_order_match | any_order_match`. — [Agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- Config shape: `{"type": "azure_ai_evaluator", "name": ..., "evaluator_name": "builtin.task_adherence", "initialization_parameters": {"deployment_name": ...}, "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"}}`. Output fields include `metric`, `label`, `score` (for 1-5 evaluators), `reason`, `threshold`, `passed`. `tool_definitions` is a list of `{name, description, parameters (JSON Schema)}`. — [Agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- Composite evaluators doc recommends a GPT-5.6-family judge, `gpt-5.6-luna` as lowest cost. Limited support (avoid several tool evaluators and groundedness) when conversation uses Azure AI Search, Bing grounding, SharePoint, Code Interpreter, Fabric Data Agent, Web Search; supported: File Search, function tools, MCP. — [Agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- Billing: risk/safety evaluations and playground evaluations are consumption-billed; playground evaluations are on by default for all Foundry projects. — [Foundry observability](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability)

### Inferences
- For a multi-agent system, apply Task Completion / Task Adherence / Intent Resolution to the orchestrator's final output and Tool Call Accuracy to each analyst's tool use. Use function tools or MCP so tool evaluators are supported.
- Show the preview status honestly in the submission ("preview evaluators").

### Gaps
- Groundedness input schema (context field) not read here; check the RAG evaluators page.
- Region and rate limits for evaluation runs not retrieved.

## 7. Microsoft-Decision-1

### Takeaway
It exists and is reported generally available in Foundry (released 2026-10-09). It is a text-only scoring model (post-trained Qwen3.5-9B) that returns probabilities for yes/no, choice and ordered-scale questions and no text. The exact JSON request/response field names could NOT be verified; do not hard-code them.

### Cited Findings
- InfoWorld, reporting 2026-10-13: available via Microsoft Foundry and OpenRouter; built by post-training Qwen3.5-9B; takes a fixed set of options and "returns a calibrated probability for each one in a single pass" (quoting Microsoft's blog); supports yes/no, choice, ratings, rubric-based assessments; multiple decisions in one request; no rationale; results may vary with question wording; $0.042 per 1M input tokens, output free; Microsoft's accuracy and speed claims are self-reported; Forrester and Kanerika quotes warn that precise-looking probabilities can overstate certainty. — [InfoWorld](https://www.infoworld.com/article/4234290/microsoft-separates-decision-making-from-generative-ai-with-a-new-model.html)
- Aggregator page: endpoint path `/providers/microsoft/v1/systemone`; model ID `Microsoft-Decision-1` (not the lowercase slug); input is a state (text or JSON) plus typed questions (yes/no probability, choice with per-option probability, ordered-scale score); 32,768-token input; supports structured outputs; Foundry deployment version 1, GlobalStandard or DataZoneStandard; released 2026-10-09; the page itself says request/response schema snippets are "not sourced yet". — [llmreference.com](https://www.llmreference.com/model/microsoft-decision-1/microsoft-foundry)
- Search summary of the Microsoft Tech Community announcement (Oct 9 2026, title "Introducing Microsoft-Decision-1 in Microsoft Foundry for decision and classification workloads") and others: catalog mentions explicit abstention ("cannot tell"); "model parameter is your deployment name". The announcement body could not be fetched (only the title returned). — [Tech Community post](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-decision-1-in-microsoft-foundry-for-decision-and-classific/4562742)

### Inferences
- Because the response is probabilities, it fits "bounded yes/no/choice calls" (e.g. "is the press collapsing?"). Surface the probability plus a separate LLM-written rationale; the model supplies none.

### Gaps
- Official response JSON schema (field names for probabilities/labels), request body shape, rate limits, regions, official price on the Foundry pricing page: not verified. First action: deploy it in the Foundry portal, call once, and copy the real response.
- Benchmark claims unverified; one review reportedly found no published figures.

## 8. What strong multi-agent demos look like to judges

### Takeaway
No Microsoft-authored winners' write-ups for this hackathon or the Microsoft AI Agents Hackathon were retrieved, so no evidence-based answer. Only inferences from the brief and generic guidance.

### Cited Findings
- The brief itself emphasises "explainable match intelligence" and a five-stage pipeline in participant repos (ingest, interpret, explain, render, personalize). — [Reactor series](https://developer.microsoft.com/en-us/reactor/series/S-1709/); [bikilath repo](https://github.com/bikilath/inside-the-game)
- A participant repo ships a "Judge quick start" and a DEMO.md walkthrough, i.e. teams are making judging reproducible. — [AmirMirj repo](https://github.com/AmirMirj/Inside-the-Game-Developer-Hackathon)
- Generic hackathon rubric (innovation, technical implementation, impact, demo, completeness) from a non-Microsoft blog; not specific to this event. — [reskilll blog](https://blogs.reskilll.com/what-hackathon-judges-look-for-complete-judging-criteria-breakdown-2026/) (search snippet)

### Inferences
- Likely valued: visible agent roles with distinct tools, a trace view of orchestration, approval gate shown live, evaluator scores on a fixed scenario set, deterministic fallback when a cloud call fails, one replayed synthetic match with timed moments.
- Everything in the Foundry/Fabric path should be rehearsed live before recording; keep a local fallback.

### Gaps
- Past winners' write-ups (Microsoft AI Agents Hackathon, Azure/Fabric hackathons): not found in this pass.

## Verify-before-demo checklist (distilled)
1. Official rules, categories, deadline (27 Oct 23:59 PT reported) and registration status.
2. Decision-1: deploy, call, capture real response schema.
3. `pip index versions` for the four agent-framework packages; pin versions (1.22.0 changes persisted state format).
4. Foundry hosting recipe for workflows/agents (1.20.0 redesign; avoid `agent=` shortcut for WorkflowAgent).
5. Evaluators: confirm preview status in portal; judge model deployment (GPT-5.6 family recommended for composites).
6. Eventstream -> Eventhouse -> Activator: confirm no preview tag on destination, capacity at least F4 or trial, paced replay.
