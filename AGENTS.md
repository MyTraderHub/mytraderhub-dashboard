# AGENTS.md

Guidance for AI agents working in this repository.

## Project status

**mytraderhub-dashboard** is a greenfield stub. As of the initial commit, the repo contains only `README.md` describing a future stock market dashboard for MyTraderHub. There is no application source, dependency manifest, test suite, or service configuration yet.

## Cursor Cloud specific instructions

### Services

No services are defined. There is nothing to lint, test, build, or run until application code and tooling are added (for example `package.json`, `docker-compose.yml`, or equivalent).

### VM tooling

The Cloud Agent VM provides:

- **Node.js** v22.x and **npm** (suitable for a future React/Next.js/Vite frontend)
- **Python** 3.12 (suitable for a future Python API or scripts)
- **git**

Docker is not required for the current repo contents.

### When application code is added

1. Read the project's README and any new setup docs first.
2. Install dependencies using the lockfile's package manager (`package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, etc.).
3. Start the dev server with the documented command (commonly `npm run dev` or `docker compose up`).
4. Document any non-obvious env vars, ports, or external APIs (market data, auth) in this section for future agents.

### Update script

The VM startup update script is a no-op until a dependency manifest exists. Once `package.json` (or similar) is committed, the update script should install dependencies on each agent session.
