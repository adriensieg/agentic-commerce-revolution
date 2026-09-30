


#### Core Pillars: Who Does What?

- <mark>**AI Chatbot Platform**</mark>: The orchestrator. It **talks to the user**, **connects to merchants** via MCP, **manages the shopping cart**, and **displays the Google Pay button**.
- <mark>**The Merchants**</mark>: Independent sellers who expose their catalogs and **checkout systems** using MCP and the UCP (Universal Commerce Protocol) standard.
- <mark>**The Payment Infrastructure**</mark> (**Google Pay** + **PSP**): Google Pay securely hands over the **user's encrypted card token** to our chatbot, and our chatbot sends it to the **PSP** (like Stripe) to **capture the actual money**.

#### Requirements for Integration
- <mark>**Google Pay & Wallet Console Account**</mark>: We must create or reuse **a merchant account** in the **Google Pay & Wallet Console**.
- <mark>**Payment Service Provider (PSP)**</mark>: Use a **PSP integrated with Google Pay**, or set up a direct integration requiring PCI DSS compliance and encryption configuration.
- <mark>**UCP Well-Known Profile**</mark>: Publish a **UCP profile** declaring **your endpoints**, **public keys**, and the **Google Pay payment handler** (`com.google.pay`).
- <mark>**REST Endpoints**</mark>: Implement core backend **REST endpoints** for **session creation**, **updates**, and **completion to manage checkout sessions** with AI agents.

<mark>**Google Pay Wallet**</mark> **does not process money**, so we must use a **</mark>Payment Service Provider**</mark> (PSP) like **Stripe**. 
- **Google Pay** is a secure **digital wallet** that **stores tokens of real credit cards**;
- A **PSP** is the actual **financial engine** that communicates with **banks** to securely move money from **the buyer's card to the merchant's bank account**. Since Stripe is a PSP that handles all heavy encryption, using them ensures you do not have to manage PCI DSS compliance.

### The Step-by-Step Flow

#### Phase 1: Merchant Onboarding (Behind the Scenes)
Before any user types a message, merchants must list their products in your chatbot.
- **Step 1**: The merchant builds an MCP Server that exposes their product catalog and inventory.
- **Step 2**: The merchant configures their system to adhere to UCP endpoints (Standardized APIs for creating a cart, calculating shipping/taxes, and submitting an order).
- **Step 3**: The merchant registers their UCP-compliant endpoints with your chatbot platform.
- **Step 4**: The merchant connects their own PSP account (e.g., Stripe) to their system so they can eventually receive payouts.

#### Phase 2: The User Experience (Frontend & AI Logic)
This is what happens live inside our web application.

- **Step 5**: Search & Browse
  - **User Perspective**: The user types: "I need a waterproof running jacket size M under $100."
  - **AI Chatbot Perspective**: The AI recognizes the intent, calls the connected merchant MCP servers, searches their catalogs, and displays 3 matching options directly in the chat UI.
- **Step 6**: Cart Creation
    - **User Perspective**: The user clicks "Add to cart" or tells the bot "Let's buy the blue one."
    - **AI Chatbot Perspective**: The AI uses the merchant's UCP endpoints to initiate a checkout session. The merchant's backend responds with the exact total, item details, and available shipping methods.

- **Step 7**: <mark>**The Checkout & Payment Trigger**</mark>
    - **User Perspective**: The user sees a summary of the order and clicks a "Google Pay" button embedded in your chatbot UI.
    - **AI Chatbot Perspective**: Your web app triggers the standard Google Pay API JavaScript SDK. A secure Google pop-up appears over your chatbot.
      
- **Step 8**: <mark>**Tokenization**</mark> (Skipping PCI Compliance)
    - **User Perspective**: The user authenticates with biometric data (like FaceID/Fingerprint) or chooses a saved card, and confirms the payment.
    - **AI Chatbot Perspective**: Google Pay does not give your chatbot or the merchant the actual credit card number. Instead, Google returns a heavily encrypted, one-time-use Payment Token. Because your code never touches raw credit card numbers, you are completely free from PCI DSS compliance stress.
      
- **Step 9**: <mark>**Processing the Money (The PSP's Job)
    - **AI Chatbot Perspective**: Your chatbot captures this Google Pay encrypted token and passes it securely to the merchant's backend via the UCP "complete session" endpoint.
    - **Merchant Perspective**: The merchant's backend takes that token and hands it over to their PSP (Stripe). Stripe decrypts the token, talks to the customer's bank, pulls the money, deposits it into the merchant's bank account, and sends back a success confirmation.
      
- **Step 10**: <mark>**Order Confirmation
    - **AI Chatbot Perspective**: Upon receiving the success signal from the merchant, the AI tells the user: "Success! Your order #12345 has been placed, and a confirmation email is on the way."

```mermaid
sequenceDiagram
    autonumber
    actor User as "User (Web Browser)"
    participant BotUI as "Your Chatbot UI / Frontend"
    participant Gemini as "Gemini AI Orchestrator"
    participant MerchMCP as "Merchant MCP Server"
    participant MerchUCP as "Merchant UCP Backend"
    participant GPay as "Google Pay API"
    participant Stripe as "PSP (Stripe)"

    %% PHASE 1: MERCHANDISER ONBOARDING
    Note over MerchMCP, Stripe: Phase 1: Merchant Onboarding (Prep Work)
    MerchUCP->>Stripe: Link merchant bank account to Stripe
    MerchMCP->>Gemini: Register MCP Tools (Expose Product Catalog APIs)
    MerchUCP->>BotUI: Publish UCP Well-Known Profile (Endpoints & Public Keys)

    %% PHASE 2: BROWSING & SEARCH
    Note over User, MerchMCP: Phase 2: User Browsing & Product Search
    User->>BotUI: Types: "Find a waterproof running jacket size M under $100"
    BotUI->>Gemini: Forward user prompt
    Gemini->>MerchMCP: Execute Tool Call: search_catalog(query, size, price)
    MerchMCP-->>Gemini: Return matching products list
    Gemini-->>BotUI: Render products nicely in Chat UI
    BotUI-->>User: Displays product choices with "Buy Now" button

    %% PHASE 3: CHECKOUT INITIALIZATION
    Note over User, MerchUCP: Phase 3: Cart & Checkout Session Creation
    User->>BotUI: Clicks "Google Pay / Buy Now"
    BotUI->>MerchUCP: HTTP POST: Create UCP Checkout Session
    MerchUCP-->>BotUI: Returns Session ID, exact total, taxes, and allowed payment methods (com.google.pay)

    %% PHASE 4: GOOGLE PAY TOKENIZATION
    Note over User, GPay: Phase 4: Secure Payment Authentication (No PCI Stress)
    BotUI->>GPay: Call Google Pay SDK with Merchant Stripe Credentials
    GPay-->>User: Present secure Google overlay popup (FaceID / Fingerprint authorization)
    User->>GPay: Approves transaction
    GPay->>GPay: Encrypts card details internally
    GPay-->>BotUI: Returns Single-use Encrypted Payment Token

    %% PHASE 5: TRANSACTION COMPLETION
    Note over BotUI, Stripe: Phase 5: Processing the Money & Completing Order
    BotUI->>MerchUCP: HTTP POST: Complete UCP Session (Sends Google Pay Token + Session ID)
    MerchUCP->>Stripe: Forward Encrypted Payment Token to charge customer
    Stripe->>Stripe: Decrypts token & processes funds bank-to-bank
    Stripe-->>MerchUCP: Payment Success Confirmation
    MerchUCP->>MerchUCP: Create order record in ERP / Inventory system
    MerchUCP-->>BotUI: HTTP 200 OK (Order Confirmation Details)
    BotUI->>Gemini: Notify AI of successful purchase
    Gemini-->>BotUI: Formulate friendly success message
    BotUI-->>User: Displays message: "Success! Order #12345 has been placed."
```





How credit cards are secured in Google Pay and how Stripe processes that token without anyone seeing the raw card details

### Step 1: How a Card Gets into Google Pay (Network Tokenization)

When a user adds a credit card to Google Pay, the **raw card number** (**PAN - Primary Account Number**) is destroyed almost immediately and replaced using a process called <mark>**Network Tokenization**</mark>.

- <mark>**The Handshake**</mark>: The user types their **16-digit card number (PAN)** into the Google Pay app. Google Pay securely transmits this data directly to the **Card Network** (Visa, Mastercard, Amex).
- <mark>**The Substitution**</mark>: The **Card Network** asks the **Issuing Bank** (the bank that gave the user the card) for a **substitute number**. This substitute is called a **DPAN (Digital Primary Account Number)** or a <mark>**Network Token**</mark>.
- <mark>**The Storage**</mark>: The raw card number is discarded by Google. Only the **DPAN** is stored securely in Google's encrypted servers. This DPAN is entirely useless outside of the Google Pay ecosystem; if a hacker steals it, they cannot use it to buy things on Amazon or swipe it at a physical grocery store.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant GPay as Google Pay

    Note over User,GPay: Phase 1 - Card Provisioning and Tokenization
    User->>GPay: Enter raw credit card details (PAN)
    GPay->>GPay: Contact card network and issuing bank
    GPay->>GPay: Replace PAN with Digital Account Number (DPAN)
    GPay->>GPay: Store DPAN securely in Google Wallet
    Note over User,GPay: Card is tokenized and ready for secure transactions
```

### Part 2: How Stripe Recognizes the Google Pay Token

How Stripe does understand a token generated by Google? 
This works because of a **pre-established cryptographic framework** and a **joint configuration** called <mark>**Gateway Tokenization**</mark>.
Before a transaction ever happens, **the merchant configures their frontend Google Pay SDK** with a specific parameter: `gateway: 'stripe'`.

The Cryptographic Chain of Custody:

```mermaid
sequenceDiagram
    autonumber
    participant BotUI as "Chatbot UI (Your Frontend)"
    participant GPay as "Google Pay Servers"
    participant Merch as "Merchant Backend"
    participant Stripe as "Stripe (PSP)"
    participant Network as "Visa/Mastercard Network"

    BotUI->>GPay: Request Token (Configured for Gateway: Stripe)
    GPay->>GPay: Encrypts DPAN using Stripe's Public Key
    GPay-->>BotUI: Returns Google Pay Token (Encrypted Blob)
    BotUI->>Merch: Sends Token via UCP
    Merch->>Stripe: Forwards Encrypted Token
    Stripe->>Stripe: Decrypts Blob using Stripe's Private Key
    Stripe->>Network: Submits Decrypted DPAN + Cryptogram
```

1. <mark>**The Shared Keys**</mark>: Stripe and Google Pay have an ongoing platform agreement. Google Pay holds Stripe’s Public Cryptographic Keys in its master system.
2. <mark>**The Target Lock**</mark>: When our Chatbot UI calls the Google Pay API, it explicitly says: "Hey Google, I am requesting a token for a merchant who uses Stripe."
3. <mark>**The Encryption**</mark>: Google Pay takes the **stored secure card details (DPAN)** and packs it inside an **encrypted payload** (a **JSON cryptographic blob**) using **Stripe’s public key**.
4. <mark>**The Blind Hand-off**</mark>: Google Pay hands this **encrypted blob to our Chatbot UI**. Our frontend, our backend, and the merchant's MCP server can all look at this payload, but it looks like **unreadable gibberish**. This is why you don't need PCI compliance; you lack the mathematical key required to read it.
5. <mark>**The Decryption**</mark>: The merchant backend passes this unreadable blob to Stripe via the Stripe API. Because the blob was encrypted with Stripe's public key, only Stripe's matching Private Key can unlock it.
6. <mark>**The Charge**</mark>: Stripe **decrypts the blob**, **extracts the DPAN** along with a **one-time cryptographic signature** (**cryptogram**), and **forwards** it directly to the **Visa/Mastercard networks** to legally pull the funds from the user's bank.

#### Summary of Concepts
- <mark>**Network Token (DPAN)**</mark>: A permanent fake card number issued by the card network that replaces the real card inside Google's wallet.
- <mark>**Gateway Token (The Blob)**</mark>: A single-use, highly encrypted package containing the DPAN, wrapped by Google using Stripe's public key so that only Stripe can read it.
- <mark>**Asymmetric Encryption**</mark>: The mathematical concept (Public/Private key pairs) that ensures sensitive data can pass through unsafe intermediaries (our chatbot, the UCP backend) without being compromised.


