Trust Layer for MCP — Project Starter
The neutral verification authority for MCP servers. Server Cards say what a server claims; we prove whether the claim is true.
The one-line bet
The MCP spec is building the envelope (machine-readable Server Cards via .well-known). It is not building the trust (proof the card is honest, the tools behave, and nothing drifts). That gap is structurally an outsider's job — a trust authority can't live inside the thing it verifies. That's what we build.
Why this, and not the obvious thing
The intuitive project — "a standard way to describe an agent/MCP server" — is already being absorbed by the spec:
SEP-1649 (Server Cards) — /.well-known/mcp/server-card.json: capabilities, tools, transports, auth, protocol version, discoverable before connecting. Authored partly by the lead maintainer. Draft, slated for the next release.
SEP-1960 — parallel discovery endpoint for endpoint enumeration + auth requirements.
Both have broad community support and live client implementations.
Conclusion: do not build the descriptor. The committee owns it and ships it.
What the spec is NOT doing (the durable gap):
Server Cards are self-declared. Nothing verifies the claim.
No conformance testing exists yet (the roadmap only "commits to" test suites — no Working Group staffed on it).
Rug-pull / drift — a server can change its tools after a client approves the card. Unowned.
Blast radius — what a tool reads vs writes vs does irreversibly. Still informal, lives in READMEs.
Why it survives contact with the roadmap
Neutrality is the moat. TLS doesn't contain the Certificate Authority — the CA sits beside the protocol. Docker doesn't sign its own images. You never let the server vouch for itself. Even when MCP ships conformance tests, the attestation (the party that runs them and issues an unforgeable badge) is an outsider role by design. This is the one seat the committee and hyperscalers can't take, because the value comes from not being them.
Crawlable substrate didn't exist before. Verification-at-scale was impossible while server surfaces lived in prose READMEs. Server Cards hand you a machine-readable surface across thousands of servers. The spec is, unintentionally, building your raw material.
Timing opening. Conformance is not a staffed priority area. SEPs outside priority areas move slowly — which means an independent party can move faster than the committee here. Engage the contributor Discord to build beside the eventual conformance WG, not against it.
What NOT to build
❌ A server descriptor / card format — SEP-1649/1960 own it.
❌ A token-bloat / tool-selection fixer — Anthropic (Tool Search), Cloudflare, and gateways already shipped these, each inside their own ecosystem.
❌ Transport / scaling / enterprise auth — official 2026 roadmap owns it.
❌ A full "cathedral" (Spec → Validator → Evaluator → Registry → Orchestrator) up front. Build one load-bearing brick.
The wedge (MVP) — the conformance checker
A tool a single developer runs against their own server, alone, with zero network, and gets value in the first minute.
It reads the server's card, then actually exercises the server and reports where card and reality diverge:
A tool present in behavior but missing from the card (or vice versa).
A schema that lies about its inputs/outputs.
A declared capability the handshake doesn't deliver.
A side effect the card never disclosed.
This is the SSL-cert / Docker-sign analogy, finally grounded in a real artifact.
MVP success test: a developer who just wrote an MCP server points the tool at it and, within 60 seconds, learns something true about their server they couldn't easily see before — entirely for their own benefit, no badge or network required.
Build sequence (smallest useful thing first)
Conformance checker — card vs reality diff. Standalone, selfish value. (Start here.)
Attestation / badge — signed, unforgeable results the dev can publish. The badge means something because an independent party ran it.
Trust dimensions the card ignores — blast radius (read/write/irreversible) and drift detection (did this week's behavior match last week's card?). Rug-pull detection is the real differentiator and nobody owns it.
Registry / search — last, not first. It's the network-effect payoff, earned only after the badge is credible and you're sitting on crawled, verified card data.
Validate before writing real code
The single assumption the whole project rests on:
[ ] Is the gap between a declared Server Card and real server behavior actually wide enough to be worth checking? Pull the SEP-1649 card schema + a few real published cards. List what a card asserts vs. what it leaves unverifiable. If cards are trivially accurate, there's nothing to verify — and the project is dead. Confirm this first.
Secondary checks:
[ ] How many real servers publish a card today? (Crawlable population size.)
[ ] Is anyone in the contributor Discord already drafting a conformance SEP? (Build beside, not against.)
[ ] What's the cheapest way to "exercise" a tool safely without triggering real side effects? (Sandboxing / dry-run semantics.)
Positioning one-liner (for later)
Not "Swagger for agents." The Certificate Authority for MCP servers — the neutral party that proves a server is what its card says it is, and stays that way.
Reference context (as of mid-2026)
MCP governed by the Agentic AI Foundation (Linux Foundation); donated by Anthropic Dec 2025.
Next spec release candidate dated 2026-07-28; headline change is statelessness. Discovery (server/discover, .well-known) is being built into core.
SEPs aligned to priority areas (transport, agent comms, governance, enterprise) move fastest; others face a higher bar — conformance/trust is not currently a priority area.
Tool-bloat crisis (up to ~72% of context lost to tool defs; selection accuracy dropping ~3x) is real but already being addressed ecosystem-by-ecosystem — explicitly out of scope for us.
