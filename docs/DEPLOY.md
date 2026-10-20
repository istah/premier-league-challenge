# Deploy to Azure Container Apps

The container runs the offline app (`uvicorn plc.api:app` on port 8080). No secrets are baked into the image; `.env` is excluded by `.dockerignore`.

## Local container (tested)
`docker build` and `docker run -p 8080:8080` were run on a local Docker 29.1: the image built, `GET /` returned 200 and `POST /match` returned a match. The Azure commands below are **untested**; they were not run against a subscription.

```bash
docker build -t plc .
docker run --rm -p 8080:8080 plc
```

## Azure Container Apps (untested)
Names are placeholders. Check flags against `az containerapp --help`.

```bash
RG=plc-rg; LOC=westeurope; ENV=plc-env; APP=plc-coach-room
az group create -n $RG -l $LOC
az containerapp env create -n $ENV -g $RG -l $LOC

# Build in Azure from the repo root and deploy with public ingress on 8080.
az containerapp up -n $APP -g $RG --environment $ENV --source . --ingress external --target-port 8080
```

Optional Foundry settings (omit them and the app runs offline on the heuristic). Store them as secrets, not in the image:

```bash
az containerapp secret set -n $APP -g $RG --secrets foundry-endpoint="<project endpoint>"
az containerapp update -n $APP -g $RG --set-env-vars \
  FOUNDRY_PROJECT_ENDPOINT=secretref:foundry-endpoint FOUNDRY_MODEL=<deployment>
```

`FOUNDRY_RESOURCE_ENDPOINT`, `DECISION_DEPLOYMENT`, `EVENTHUB_NAMESPACE` and `EVENTHUB_NAME` work the same way. Foundry and Event Hubs paths are unverified live, and the app needs an identity with access (for example a managed identity) if you enable them.

## Notes
- State is in memory: one replica (`--min-replicas 1 --max-replicas 1`), and matches are lost on restart.
- Delete when done: `az group delete -n $RG`.
