

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer (Browser)
    participant React as React App (Frontend)
    participant Python as Python Backend (FastAPI)
    participant DB as Merchant Database
    participant PSP as Stripe (PSP = Gateway + Processor)
    participant Networks as Card Networks (Visa/MC)
    participant IssuingBank as Issuing Bank (Customer's Bank)
    participant AcquiringBank as Acquiring Bank (Merchant's Bank)

    Note over Python,PSP: STEP 0 — Merchant Onboarding & Key Registration (one-time)
    Note over PSP: Merchant signs up with Stripe → Stripe provisions a Merchant Account<br/>and issues 3 keys + 1 webhook secret
    PSP-->>Python: Issue Secret Key (sk_live_...) — full API access
    PSP-->>React: Issue Publishable Key (pk_live_...) — public, identifies account only
    PSP-->>Python: Issue Webhook Secret (whsec_...) — verifies webhook authenticity
    Python->>Python: Store sk_live_... & whsec_... in server .env (never exposed to browser)
    React->>React: Embed pk_live_... in frontend bundle (safe to expose)
    Python->>PSP: Register webhook endpoint URL (https://api.merchant.com/stripe-webhook)

    Note over Customer,PSP: STEP 1 — Checkout Initialization
    Customer->>React: Click "Proceed to Checkout"
    React->>Python: POST /api/create-payment-intent { cart_id: 123 }
    Note over Python: Compute amount server-side from cart_id<br/>(NEVER trust an amount sent by the browser)
    Python->>DB: Look up cart items, prices → total = 2000 (¢) = $20.00
    DB-->>Python: Return authoritative cart total
    Python->>PSP: POST /v1/payment_intents { amount: 2000, currency: "usd" }<br/>Authorization: Bearer sk_live_...
    Note over PSP: sk_live_... authenticates & authorizes this request<br/>as belonging to the merchant's account
    PSP-->>Python: 200 OK { id: "pi_3M...", client_secret: "pi_3M_secret_xyz" }
    Python-->>React: 200 OK { client_secret: "pi_3M_secret_xyz" }
    Note over React: client_secret = ephemeral, single-use token<br/>authorizing THIS payment only

    Note over Customer,PSP: STEP 2 — UI Rendering & Card Collection (PCI isolation)
    React->>PSP: loadStripe(pk_live_...) → load Stripe.js SDK
    PSP-->>React: Return SDK; React mounts <Elements> → injects Stripe iframe
    Note over React,PSP: The iframe is served by Stripe, NOT by the merchant.<br/>Merchant JS cannot read its contents (cross-origin).
    PSP-->>Customer: Render secure card input fields inside iframe
    Customer->>PSP: Type PAN, Expiry, CVV directly into Stripe's iframe
    Note over React,Python: Raw PAN/CVV never touch React code or Python server → keeps merchant OUT of PCI-DSS scope

    Note over Customer,IssuingBank: STEP 3 — Tokenization & Authorization
    Customer->>React: Click "Pay $20.00"
    React->>PSP: stripe.confirmCardPayment(client_secret, { card: iframeElement })
    Note over PSP: Tokenize raw card → PaymentMethod (pm_1N...)<br/>Raw PAN is vaulted at Stripe; only token leaves the vault
    PSP->>Networks: Route authorization request (amount + token)
    Networks->>IssuingBank: Forward auth request to customer's bank
    Note over IssuingBank: Check funds, run fraud/3-D Secure,<br/>place a hold on $20.00
    IssuingBank-->>Networks: Approve (auth code) / Decline
    Networks-->>PSP: Relay approval + auth code
    PSP-->>React: Return PaymentIntent status: "succeeded" (or "requires_action" for 3DS)

    Note over React,Customer: STEP 4 — Optimistic UI (NOT trusted for fulfillment)
    React->>Customer: Show "Processing your order..."
    Note over React: A response to the browser can be spoofed by a user.<br/>NEVER grant goods based on this alone.

    Note over PSP,DB: STEP 5 — Asynchronous Webhook (source of truth)
    PSP->>Python: POST /stripe-webhook { type: "payment_intent.succeeded", data: {...} }
    Note over Python: Recompute HMAC-SHA256 over raw body using whsec_...<br/>Compare to Stripe-Signature header
    alt Signature valid
        Python->>DB: UPDATE order #123 SET status = 'PAID'
        DB-->>Python: OK
        Python->>Python: Provision digital service / fulfill order
        Python-->>PSP: 200 OK (acknowledge receipt)
    else Signature invalid / mismatch
        Python-->>PSP: 400 Bad Request (reject forged/tampered event)
    end

    Note over PSP,AcquiringBank: STEP 6 — Settlement (hours–days later, batch)
    PSP->>Networks: Submit captured transactions for settlement (batch)
    Networks->>IssuingBank: Request actual funds transfer
    IssuingBank->>AcquiringBank: Move funds via card networks
    AcquiringBank->>PSP: Funds land in Stripe balance (merchant account)
    Note over PSP: Stripe deducts fees (e.g. 2.9% + 30¢),<br/>then payouts net amount to merchant bank on schedule

    Note over Customer,DB: STEP 7 — Confirmed Fulfillment
    React->>Python: GET /api/order/123/status (poll) or via WebSocket push
    Python->>DB: Read order status
    DB-->>Python: status = 'PAID'
    Python-->>React: { status: "PAID", access: "granted" }
    React->>Customer: Display "Order Complete & Access Granted"
```
