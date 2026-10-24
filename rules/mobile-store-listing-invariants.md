# Mobile Store Listing, Feature Claims & ASO Invariants

When drafting, reviewing, or modifying store listings, paywall UI strings, screenshot generators, and product documentation for mobile apps:

## 1. Single Source of Truth: Code Over Marketing
- **Engine Limit Supremacy**: Runtime code constants are the authoritative source of truth. In-app strings, screenshot generators, and store listings must strictly synchronize with these limits.
- **No False Concurrency Claims**: Never claim "unlimited downloads" or "unlimited operations" when queue concurrency or slot ceilings exist in code. Always state exact supported limits.

## 2. Feature Claim Verification Invariant
- **Verify Architecture Before Claiming**: Check feature claims against actual platform implementations before publishing:
  - Do not claim "Background Playback" if the app only implements Picture-in-Picture (PiP) without an active foreground playback service or media session.
  - Do not claim "packet classification" if filtering runs at the HTTP/HTTPS request or URL layer inside WebView / network stack.
  - Verify cipher modes and hardware backing in code before including in promotional text.

## 3. Pricing & Currency Localization
- **Zero Hardcoded Currency Values**: Never embed specific dollar amounts (e.g. `$1.00/mo`, `$3.00 Lifetime`) in store descriptions.
- **Structure Over Numbers**: Clearly describe billing cadence and tier models (e.g. "free core", "monthly subscription or one-time lifetime unlock") and let the app store handle regional price formatting and localized currencies.

## 4. Policy Compliance & Legal Copy
- **Platform Exclusions**: Clearly state platform limitations (e.g. "does not download from YouTube or Google-owned platforms").
- **Never Cite Store Policies**: Do NOT include phrases such as "in strict compliance with Google Play Store Terms of Service...". Citing store policies in listing copy risks policy rejection for claiming false endorsement.

## 5. ASO & Conversion Copywriting Principles
- **Action-First Opening**: The first 1–2 lines (visible before "read more") must lead with direct user verbs (e.g. browse, detect, save). Avoid opening with low-level backend architecture.
- **Mandatory First-Session Walkthrough**: Always provide a clear 3-step usage instruction to prevent immediate uninstalls caused by missing onboarding context.
- **Search Keywords Over Internal Jargon**:
  - Purge low-value internal implementation terms: file names (`.so`), memory/page alignment notes, database frameworks, low-level APIs, and licensing notes.
  - Prioritize user search terms: high-intent keywords describing what the user actually wants.
- **Eliminate Puffery**: Avoid exaggerated claims ("military-grade", "lightning-fast", "saturate your connection"). Use precise, transparent engineering statements.
- **Highlight Real Differentiators**: Emphasize genuine unique selling propositions, such as "100% ad-free on every tier with zero tracking SDKs".
