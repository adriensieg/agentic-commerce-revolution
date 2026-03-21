# Agentic AI Takes Over Commerce

What if **buying anything** was as **simple** as **asking**? Why **juggle multiple apps** like it’s **2015**, when **your favorite assistant** can do it all in **one conversation**? What if you could **place your order** directly with ChatGPT using the Agentic Commerce Protocol?

- 🚗 Book the cheapest Uber or Lyft **ride** right inside **ChatGPT** - https://www.youtube.com/shorts/5ZI7IgvJHV8
- 💐 Send **flowers** instantly from your local nearby store inside **Mistral AI Le Chat** - https://youtu.be/671YMGWVHL0
- 🍔 Order your favorite nearby **burgers** with **Anthropic Claude** - https://www.youtube.com/shorts/Cy-N7jy_BsQ

**No more apps**. All from the AI assistant you already use: **ChatGPT**, **Claude** or **Le Chat**

**McDonald's** has an app. **Burger Kings** has an app. **Wendy's** has an app. **KFC** has an app. **ChatGPT OpenAI has a conversation**. Guess which one wins. *China already knows* — **ask WeChat**. The next time you want a burger, **you won't open an app**. **You'll open a conversation**.

#### Try it out here - https://hackaton.devailab.work/mcp

How to set it up into your favorite **existing** AI Assistant - such as **ChatGPT**, **Claude** or **Mistral AI**? Here is the **full tutorial**: https://www.youtube.com/watch?v=qwtwGqpXluE&feature=youtu.be

- [The Vision]()
- [The Core Problems we are solving]()
    - [Break 1 — ChatGPT is authenticated, but the user is not]()
    - [Break 2 — Our MCP server cannot act on external APIs without user-specific authorization]()
    - [Break 3 — Financial transactions require explicit user confirmation]()
 - [The solution]()
 - [What has it been developed for this hackaton?]()
 - [The Limits of Today, The Blueprint for Tomorrow]()

# The Vision

Meet **Agentic Commerce Protocol** — the **end of apps**, **tabs**, and **checkout flows**. **Just intent**.

Tell your favorite AI assistant **what you want**, and **it acts**. It **finds** products, **compares** options, **negotiates** prices, and **completes** the purchase — instantly. **No redirects**. **No forms**. **No friction**.

**Retailers**: no more **costly kiosks** or **mobile apps** —just **expose** your **menu**, **catalog**, or **products** via an **MCP server** and let AI assistants handle the rest.

**No app to download**.**No screen to tap**. **No line to wait in**.

Just you, a chat window, and your order — placed in plain language, confirmed in seconds.

This is the future for small commerce. Zero hardware. Zero maintenance. Zero friction.

The next generation of ordering won't look like a touch screen. It'll look like a text message.

Small businesses don't need a $10,000 kiosk. They need a phone number and an AI that listens.

The revolution won't be digitized. It'll be conversational.

Powered by a secure, **OAuth-protected MCP server**, our platform turns any **AI assistant** into a **fully autonomous buyer**. It can **discover products**, **execute transactions**, and **handle payments** end-to-end through a **trusted**, **standardized protocol**.

This is **NOT** another marketplace. It’s a **new interface for commerce**. 

- With Agentic Commerce, intent becomes action.
- Search becomes obsolete. Browsing becomes optional.
- Transactions become invisible.
- We’re not improving e-commerce — we’re replacing it.

Just tell ChatGPT what you want — and it orders, negotiates, and pays for you. We implement a secure, OAuth-protected MCP server that enables Mistral AI Le Chat to discover products, execute commerce tools, and complete end-to-end Agentic Commerce transactions through a standardized and trusted protocol.

We implemented a secure, **OAuth-protected MCP server** that enables **Mistral AI Le Chat** to **discover products**, **execute commerce tools**, and **complete end-to-end Agentic Commerce transactions** through a **standardized** and **trusted protocol**.

# The Core Problem We're Solving 
The main security question is then how do we enable **AI assistants** (such as *Open AI ChatGPT*, *Mistral AI Le Chat* or *Anthropic Claude*) to execute end‑to‑end actions **on behalf of users** — in **real time** and **transparently** — while **preserving identity**, **consent**, and **trust** across **multiple providers**?

Who **owns the transaction** when ChatGPT (or others) becomes the **interface** and **every app becomes a backend** — and how do we monetize that securely?

This is **not** a **UX convenience story** - it's a **multi-party authorization problem**: connecting these 3 systems into a single seamless user action — "repair my Washing machine" — requires solving an **identity chain** that does not exist out of the box. The chain breaks in 3 specific places:

- Break 1 — **ChatGPT is authenticated** - via DCR and OAuth 2.1 Authorization Code Flow with PKCE - but **the user is not**.
- Break 2 — Our MCP server has **no standing** with **other 3rd party applications** - such as ServiceNow and 3rd party APIs.
- Break 3 — A **financial transaction** requires explicit **user confirmation**

# The Core Problem We're Solving

A user saying "repair my washing machine" inside ChatGPT triggers a **3-party authorization chain**: 

1. ChatGPT must prove its **application identity** to our MCP server (Boundary 1, solved via PKCE + Auth0-issued JWT),
2. ...our MCP server must **resolve which human issued the command** and retrieve that **human's pre-authorized 3rd parties' API credentials** (identity gap, solved via RFC 8693 Token Exchange + Auth0 Token Vault),
3. ...and before the actual mainteance intervention is booked, the **user must explicitly confirm the financial transaction** on a separate channel without leaving ChatGPT (confirmation gap, solved via CIBA).

- **ChatGPT** can talk to **external services** through **MCP**.
- **Uber** exposes **ride-booking** through an **OAuth-protected API**.
- **Auth0** can **broker identity** and **credentials**.

We need a mechanism that **bridges the ChatGPT session identity** to the **3rd parties account identity** without asking the user to **re-authenticate every time**. 

~~This is exactly what **Identity Federation** and specifically **Token Exchange** (RFC 8693) solves. This is where **Identity Jag** (**Id-Jag**) or equivalent **cross-app identity** patterns come in.~~

Each of these is a distinct protocol problem. None is automatically inherited from solving the others. **Auth0 is the architectural component that spans all three** — 
- as **authorization server**,
- **identity broker**,
- **credential vault**,
- and **confirmation orchestrator**

... making it the single most critical dependency in the entire stack.

| # | Problem | Protocol gap | Consequence if unsolved |
|---|---|---|---|
| 1 | ChatGPT is authenticated but the human user is not identified | OAuth 2.1 without OIDC carries no user identity | MCP server cannot map the request to a specific Uber account |
| 2 | MCP server has no Uber credentials for the user | 3rd parties tokens are user-scoped, issued separately, must be stored and refreshed | Maintenace cannot be booked regardless of Boundary 1 being correctly configured |
| 3 | Financial transaction requires explicit out-of-band user confirmation | Neither OAuth nor MCP provide a transaction confirmation primitive | Real money moves without verified user intent — compliance and fraud risk |

#### Break 1 — ChatGPT is authenticated, but the user is not
When ChatGPT connects to our MCP server, **OAuth 2.1 authenticates the ChatGPT application** — **not the human behind it**. 

The access token your MCP server receives proves that **OpenAI's client is authorized to call our tools**. It carries **zero information** about which specific human issued the command.
OpenAI's MCP integration uses OAuth 2.1 **without OpenID Connect**. No `ID token` is issued. No sub `claim`. No `user profile`. **The human is invisible at the protocol level**.
Your MCP server receives a **legitimate**, **cryptographically valid token** — and has **no idea whose Uber account to charge**.

### Break 2 — Our MCP server cannot act on external APIs without user-specific authorization

Even if a user's identity is resolved, our MCP server cannot perform actions on an external service on the user's behalf without a user-specific access token — one explicitly issued after the user has gone through that service’s consent flow and granted permission for your application to act on their account.

These tokens are not automatically available. They must be obtained per user, stored securely, refreshed before expiration, and retrieved at the moment of request.

If the token is missing, expired, or handled incorrectly, the action cannot be completed, no matter how well internal identity or authentication boundaries are configured.
Tokens issued by different authorization servers are scoped to different resources and govern distinct trust relationships. They are not interchangeable.

### Break 3 — Financial transactions require explicit user confirmation

Low-risk queries like reading estimates or checking availability can often be done without user interaction. Performing actions that trigger real financial transactions, however, is fundamentally different. Background authorization is insufficient and may be legally non-compliant in certain jurisdictions.

The user must explicitly confirm each transaction, through a separate, auditable, and non-repudiable channel. This confirmation should occur without breaking the conversational flow or requiring the user to leave the interface.

# What has it been developed for this hackaton?

### Commerce Protocol
We implement an AI agent that enables users to discover products, negotiate, order, and pay within a standardized and seamless commerce flow.

### Secure Server Exposure
Le Chat connects to our OAuth-protected MCP server using **discovery Dynamic Client Registration (DCR)**, and a **PKCE Authorization Code flow** with **Auth0**. It obtains a **signed JWT access token**, verified via **JWKS** before **granting MCP-based MCP tool execution** with automatic token refresh.

### Capabilities
Secure **product discovery**, **contextual ordering**, **real-time negotiation**, **payment initiation** via CIBA, and persistent user context — enabling end-to-end trusted Agentic Commerce.

# The Limits of Today, The Blueprint for Tomorrow

#### OpenAI (or any AI assistant) does not expose user identity through the MCP layer.
**RFC 8693 Token Exchange** works only if Auth0 can resolve the incoming ChatGPT token to a known user. 
Currently, **OpenAI does not pass verifiable user identity claims through the MCP connection**. 
We can work around this — but it requires either **OpenAI adding OIDC support**, or **a separate user-linking** step during onboarding that correlates the **ChatGPT session** to our **internal user record**. Doable, but not clean.

- The **OAuth flow** authenticates **OpenAI chatgpt** (**the client**) to our **MCP service** (**the resource provider**). 
- It does **NOT** **authenticate** or **identify the individual human** (OpenAI chatgpt's user) to us.
- We **won’t receive any user identity info** unless OpenAI chatgpt explictly passes it.
- OAuth by itself **does not identify a user**; it just **delegates authorization**.

In traditional web apps, we often combine **OAuth + OpenID Connect (OIDC)** to both **authenticate** and **authorize users**.
In the OpenAI chatgpt SDK integration, **only OAuth 2.1 is used** — **not OIDC.** So there’s **no user identity payload** (**no ID token**, **no claims** about the user).

#### Most of 3rd parties API access requires business approval.
External 3rd parties API are **not publicly open**. 
Vendors must **explicitly grant our application access to perform actions on behalf of users**. This is a commercial and legal dependency — not a technical one. Without it, Boundary 2 cannot go to production regardless of how well everything else is built.

### Capabilities

```
agentic-commerce/
├── app.py
└── mcp_auth/
    ├── __init__.py
    ├── config.py
    ├── token.py
    ├── middleware.py
    └── routes.py
```

```
agentic-commerce/
├── app.py
└── mcp_auth/
    ├── __init__.py
    ├── data.py
    ├── filters.py
    ├── handlers.py
    ├── models.py
    ├── server.py
    └── widgets.py
```


