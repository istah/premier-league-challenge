# Architecture diagram

Solid boxes run today (offline, locally). Dashed boxes are planned: designed but not run live.

```mermaid
flowchart LR
  subgraph today["Runs today (offline)"]
    feed["Synthetic match feed<br/>(seeded engine)"] --> bus["Event bus<br/>(in-memory log)"]
    bus --> act["Activator rules<br/>(plain data)"]
    act -->|trigger + route| orch["Orchestrator<br/>(routing table)"]
    subgraph staff["Staff agents"]
      opp["Opponent Analyst"]
      own["Own-Style Analyst"]
      tac["Formation Tactician"]
      fc["Fact-checker"]
    end
    orch --> opp & own & tac
    opp & own & tac --> fc
    fc --> judge["Judge<br/>(rules gate)"]
    judge --> ui["Coach UI<br/>(notes, one-tap actions,<br/>voice override)"]
    ui -. "coach call beats AI" .-> orch
  end

  subgraph medal["Medallion (local modules)"]
    bronze[("Bronze<br/>raw synthetic")] --> silver[("Silver<br/>validated, per-player baseline")] --> gold[("Gold<br/>decision-ready facts")]
  end
  feed --> bronze
  gold --> act
  gold --> staff

  subgraph planned["Planned, not run live"]
    eh["Azure Event Hubs"]:::plan
    fab["Fabric: Eventstream, Eventhouse (KQL), Activator"]:::plan
    fry["Foundry: agents, Decision-1, evaluators"]:::plan
    llm["LLM rubric judge"]:::plan
  end
  bus -.-> eh -.-> fab
  fab -.-> act
  fry -.-> staff
  fry -.-> judge
  llm -.-> judge

  classDef plan stroke-dasharray: 5 5,fill:#f4f4f4,stroke:#888,color:#333
```

## Legend
- Solid arrow: data or control flow that runs today.
- Dashed arrow and dashed box: planned, designed but not run live.
- Bronze, silver, gold: data moves one way, each layer reads only the one before. Agents read gold only (the Fact-checker may also query silver and cite it). Agents never write to bronze or silver.
- "Coach call beats AI": a typed or dictated override replaces any suggestion; nothing is auto-applied.
- Today the medallion layers map to local modules; the Fabric Eventhouse version is planned.
