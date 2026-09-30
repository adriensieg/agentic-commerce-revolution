
```mermaid
sequenceDiagram
    autonumber

    actor User as "User (Web Browser)"
    participant GPay as "Google Pay API"
    participant Stripe as "PSP (Stripe)"

    %% Note: Other components are idle during wallet provisioning

    Note over User,GPay: Phase 1: Card Provisioning & Tokenization

    User->>GPay: Inputs Raw Credit Card Details (PAN)
    GPay->>GPay: Contacts Card Network (Visa/Mastercard) & Issuing Bank
    GPay->>GPay: Replaces PAN with unique Digital Account Number (DPAN)
    GPay->>GPay: Discards raw PAN; stores DPAN securely in Google Wallet

    Note over User,GPay: Card is now fully tokenized and ready for secure transactions
```

```
