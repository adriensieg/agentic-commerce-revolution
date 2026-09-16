# How a Card Payment Moves Through React, Python, and Stripe

Server-Side PaymentIntent, Client-Side Card Collection, Webhook-Verified Fulfillment

```mermaid
%%{init: { 'theme': 'default', 'config': { 'wrap': true }}}%%
sequenceDiagram
    actor Customer
    participant React (Frontend)
    participant Python (Backend)
    participant Stripe

    autonumber
    Customer->>React (Frontend): Click Checkout
    React (Frontend)->>Python (Backend): Send cart_id
    Python (Backend)->>Stripe: Create PaymentIntent (sk_live_...)
    Stripe-->>React (Frontend): client_secret
    Customer->>Stripe: Enter card in Stripe iframe (pk_live_...)
    React (Frontend)->>Stripe: confirmCardPayment(client_secret)
    Stripe-->>React (Frontend): succeeded (UI only)
    Stripe->>Python (Backend): Webhook (verify with whsec_...)
    Python (Backend)->>Python (Backend): Mark PAID -> deliver goods
```

- Create **<mark>PaymentIntent</mark>** (`sk_live_...`): Our backend tells Stripe "I want to collect $20 from a customer — set up a payment slot for it." A `PaymentIntent` is Stripe's record of one attempted payment: the amount, the currency, and its status (pending → succeeded). Our backend creates it before the customer pays so the amount is **locked server-side** and can't be tampered with. The `sk_live_...` is **our backend's password to Stripe**. It **proves the request** is really from you.

- The **<mark>client_secret</mark>**: When Stripe creates the `PaymentIntent`, it returns a `client_secret` — a one-time password tied to that specific $20 payment. Think of it as a **claim ticket**. Our backend can't safely hand the browser the secret key (that would give the browser full account power). So instead Stripe issues a **narrow**, **single-use ticket** that says: "the holder of this ticket is allowed to complete this one $20 payment — and nothing else." The browser needs some permission to finish the payment. The client_secret is exactly that permission, **scoped to one transaction**.

- **<mark>Stripe iframe (pk_live_...)</mark>**: The `pk_live_...` (**publishable key**) just tells Stripe **which merchant account the card fields belong to**. It's public and powerless on its own — it can't move money. The key is only there so Stripe knows it's your account.

- "confirmCardPayment(client_secret)". This is the moment the browser says to Stripe: "here's the ticket for the $20 payment — go charge the card I just collected." It hands back the client_secret (the ticket) so Stripe can match the card the customer typed to the exact $20 payment your backend set up earlier. Stripe then contacts the banks and charges it. Plain version: "Browser tells Stripe: use this ticket, charge the card now."

### Step 0 — Merchant Onboarding & Key Registration
- The merchant registers with Stripe once.
- Stripe creates a **merchant account** (where funds will be held) and issues the **three keys**.
- **Secret** and **webhook keys** are stored in **server environment variables**, never sent to the browser.
- The **publishable key** is compiled into the frontend.
- The merchant also registers the **URL** where **Stripe should later send webhooks**.

    - **<mark>Publishable Key</mark>** (`pk_live_`...) — **Public identifier**. **Lives in the browser**. Tells Stripe "which merchant account this frontend belongs to." Can only create tokens and mount UI. Useless to an attacker because it cannot move money or read data.
    - **<mark>Secret Key</mark>** (`sk_live_`...) — **Private credential**. Lives only on the backend. Proves to Stripe that a server request genuinely comes from the account owner. Authorizes money-moving actions (charge, capture, refund). If leaked, an attacker controls the account.
    - **<mark>Webhook Secret</mark>** (`whsec_`...) — **Shared signing key**. Lives only on the backend. Used to verify that an incoming webhook was actually sent by Stripe and not forged. It does not encrypt; it authenticates the message origin. The browser gets a key that can only identify; the server gets keys that can authorize and verify.

### Step 1 — Checkout Initialization

The customer clicks checkout. React asks the backend to start a payment, sending only a cart identifier — not a price. The backend looks up the real price in its own database, then calls Stripe using the secret key to create a PaymentIntent (a Stripe object representing "an attempt to collect a specific amount"). Stripe returns a client_secret.

Purpose: the amount is calculated server-side so the customer cannot tamper with it. The secret key authenticates the merchant to Stripe. The client_secret is a single-use token authorizing the browser to complete only this one payment.

### Step 2 — UI Rendering & Card Collection

- React loads **Stripe.js** using the **publishable key** and mounts an **iframe served by Stripe**.
- The card fields live inside this iframe. Because the iframe is a different origin, the merchant's own JavaScript cannot read what the customer types.

Purpose: **raw card numbers never enter merchant code or servers**. This keeps the merchant out of the strictest PCI-DSS compliance scope. Stripe, not the merchant, is the party that touches the card data.

### Step 3 — Tokenization & Authorization

- The customer clicks Pay.
- React calls confirmCardPayment with the client_secret.
- Stripe reads the card data from its own iframe, converts the raw card number into a token (a PaymentMethod ID like pm_...), and stores the real number in its vault. Stripe then routes an authorization request through the card networks to the customer's issuing bank. The bank checks funds, runs fraud/3-D Secure, and places a hold. Approval flows back to Stripe, which reports succeeded to the browser.

Purpose: tokenization replaces the sensitive number with a safe reference. Authorization confirms the bank will release the funds and reserves them, but has not yet transferred them.

### Step 4 — Optimistic UI

React shows "Processing your order." This is only a visual update.

Purpose: give the user feedback. This browser response is not trusted for delivering goods, because browser code can be modified by the user to fake a success.

### Step 5 — Asynchronous Webhook (Source of Truth)

Stripe independently sends a server-to-server POST to the backend's registered URL, reporting payment_intent.succeeded. The backend recomputes an HMAC signature over the raw request body using the webhook secret and compares it to the signature Stripe attached. If they match, the event is genuine: the backend marks the order paid and provisions the service. If they don't match, the event is rejected as forged.

Purpose: this is the authoritative confirmation that money actually moved. It comes directly from Stripe (not through the manipulable browser) and is cryptographically verified. Fulfillment happens here, not in Step 4.

### Step 6 — Settlement

Later, in batches, Stripe submits the authorized transactions for actual fund movement. The issuing bank transfers money through the card networks to the acquiring bank (the merchant's bank side). Funds land in the Stripe balance, Stripe deducts fees, and pays out the net amount to the merchant's bank on a schedule.

Purpose: authorization (Step 3) only reserved the funds; settlement is when the money is truly captured and moved. This is asynchronous and can take days.

### Step 7 — Confirmed Fulfillment

React asks the backend for the final order status (by polling or a pushed update). The backend reads the database — already marked PAID in Step 5 — and returns confirmation. React displays "Order Complete & Access Granted."

Purpose: the frontend reflects the state the backend has already authoritatively confirmed, closing the loop between the trusted server state and the user's screen.

The Actors (Gateway / Processor / PSP)

With Stripe these are one vendor wearing three hats. Gateway: the iframe that captures and encrypts card data (Step 2–3). Processor: Stripe routing the transaction through card networks and banks (Step 3, 6). PSP: Stripe as the company bundling both and providing the merchant account that holds funds (Step 0, 6). You integrate once; Stripe fulfills all three roles internally.

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer Browser
    participant React as React App Frontend
    participant Python as Python Backend FastAPI
    participant DB as Merchant Database
    participant PSP as Stripe PSP
    participant Networks as Card Networks Visa/MC
    participant IssuingBank as Issuing Bank Customer Bank
    participant AcquiringBank as Acquiring Bank Merchant Bank

    Note over Python,PSP: STEP 0 - Merchant Onboarding and Key Registration (one-time)
    Note over PSP: Merchant signs up with Stripe. Stripe provisions a Merchant Account and issues 3 keys plus 1 webhook secret
    PSP-->>Python: Issue Secret Key sk_live - full API access
    PSP-->>React: Issue Publishable Key pk_live - public account identifier
    PSP-->>Python: Issue Webhook Secret whsec - verifies webhook authenticity
    Python->>Python: Store secret key and webhook secret in server environment
    React->>React: Embed publishable key in frontend bundle
    Python->>PSP: Register webhook endpoint URL

    Note over Customer,PSP: STEP 1 - Checkout Initialization
    Customer->>React: Click Proceed to Checkout
    React->>Python: POST create-payment-intent with cart_id
    Note over Python: Compute amount server-side from cart_id. Never trust amount sent by browser
    Python->>DB: Look up cart items and prices
    DB-->>Python: Return authoritative cart total
    Python->>PSP: Create PaymentIntent for 2000 cents USD using secret key
    Note over PSP: Secret key authenticates and authorizes the API request
    PSP-->>Python: Return PaymentIntent ID and client secret
    Python-->>React: Return client secret
    Note over React: Client secret is an ephemeral token authorizing this payment only

    Note over Customer,PSP: STEP 2 - UI Rendering and Card Collection
    React->>PSP: Load Stripe.js SDK with publishable key
    PSP-->>React: Return SDK and mount secure card component
    Note over React,PSP: Secure card fields are served by Stripe in a cross-origin iframe
    PSP-->>Customer: Render secure card input fields
    Customer->>PSP: Type PAN, expiry, and CVV directly into Stripe iframe
    Note over React,Python: Raw card data never touches React application code or Python server
    Note over React,Python: This architecture minimizes the merchant systems handling of sensitive card data

    Note over Customer,IssuingBank: STEP 3 - Tokenization and Authorization
    Customer->>React: Click Pay
    React->>PSP: Confirm card payment using client secret and card element
    Note over PSP: Tokenize card data into a PaymentMethod
    PSP->>Networks: Route authorization request
    Networks->>IssuingBank: Forward authorization request
    Note over IssuingBank: Check funds, fraud controls, and 3-D Secure
    IssuingBank->>IssuingBank: Place authorization hold on payment amount
    IssuingBank-->>Networks: Approve or decline with authorization result
    Networks-->>PSP: Relay authorization result
    PSP-->>React: Return PaymentIntent status
    Note over React: Status may be succeeded, requires_action, processing, or another state

    Note over React,Customer: STEP 4 - Optimistic UI
    React->>Customer: Show Processing your order
    Note over React: Browser response is not trusted for fulfillment
    Note over React: Never grant goods or permanent access based only on this response

    Note over PSP,DB: STEP 5 - Asynchronous Webhook and Source of Truth
    PSP->>Python: POST stripe webhook event
    Note over Python: Read raw request body and Stripe-Signature header
    Note over Python: Verify webhook signature using webhook secret
    alt Signature valid
        Python->>Python: Parse and validate webhook event
        Python->>DB: Mark order 123 as PAID
        DB-->>Python: Update successful
        Python->>Python: Provision digital service and fulfill order
        Python-->>PSP: HTTP 200 acknowledgment
    else Signature invalid
        Python-->>PSP: HTTP 400 Bad Request
        Note over Python: Reject forged or tampered webhook
    end

    Note over PSP,AcquiringBank: STEP 6 - Settlement
    PSP->>Networks: Submit captured transactions for settlement
    Networks->>IssuingBank: Request actual funds transfer
    IssuingBank->>AcquiringBank: Transfer funds through card networks
    AcquiringBank->>PSP: Funds arrive in Stripe balance
    Note over PSP: Stripe deducts applicable processing fees
    PSP->>AcquiringBank: Payout net funds to merchant bank on schedule

    Note over Customer,DB: STEP 7 - Confirmed Fulfillment
    React->>Python: GET order status
    Python->>DB: Read order status
    DB-->>Python: Return status PAID
    Python-->>React: Return PAID and access granted
    React->>Customer: Display Order Complete and Access Granted
```
```
