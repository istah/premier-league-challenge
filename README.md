# Premier League Challenge

Solo entry for the Microsoft Inside the Game hackathon, targeting **Best Multi-Agent System**.

Synthetic football events go through three agents built on Microsoft Agent Framework and Foundry: Analyst (stats and pivotal moments), Explainer (why it mattered) and Personalizer (rewrites for analyst or fan).

## Run
```
cp .env.example .env   # fill in Foundry project endpoint + model
az login
uv run python -m plc fan        # or: analyst
uv run python -m plc.events 3   # dump synthetic events
uv run pytest
```
