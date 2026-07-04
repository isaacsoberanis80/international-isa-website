# Ad Campaign Automation — What You Need Before This Can Go Live

Part 2 of the build spec (Meta + Google Ads API integration) is scaffolded
(`Campaigns` dashboard page, `AdCampaign` database table) but **not
connected to either platform yet.** Here's exactly what needs to exist on
your end before that connection can be built — researched 2026-07-03, but
verify current requirements at the links below since ad platform policies
change often.

## Meta Marketing API

**Realistic timeline: expect 1-3 weeks**, not a same-day setup.

1. **Meta Business Manager account** — business.facebook.com. Needs to
   already exist and be verified (see next step) before an ad account is
   usable via API.
2. **Business Verification** — Meta requires real legal documents: a
   business license or articles of incorporation, tax ID, and a physical
   business address (a PO box will get rejected). The name on the
   documents must exactly match what's entered in Business Manager, or it
   gets bounced back.
3. **A Meta developer app** — developers.facebook.com, create an app,
   request the Marketing API product.
4. **App Review** — Meta reviews any app that isn't just using an
   already-approved third-party tool. As of the most recent policy
   update, the practical bar is roughly 500 API calls in the past 15 days
   with under 15% error rate to reach standard access — meaning a brand
   new app usually needs to run in a lower/test tier first before
   qualifying, not get full access on day one. Typical review turnaround
   is 5-7 business days, longer for anything flagged for extra scrutiny.
5. **Ad Account ID + access token** — once approved, generate a
   long-lived access token scoped to the ad account.

Source: [Meta for Developers — App Review](https://developers.facebook.com/documentation/resp-plat-initiatives/individual-processes/app-review), [Ads Management Access update](https://developers.meta.com/blog/updates-to-ads-management-standard-access-feature/)

## Google Ads API

**Realistic timeline: faster than Meta, but still not instant** — Basic
access is a review, not an automatic approval.

1. **Google Ads Manager account (MCC)** — a manager account, not a
   regular advertiser account, is required to request a developer token.
2. **Developer token application** — inside the Google Ads UI, go to
   **Tools & Settings → API Center**, fill out the access-request form.
   Make sure the account's API contact email is real and monitored —
   Google's review team may email follow-up questions.
3. **A working business website** — part of the review checks that the
   company website URL is live and legitimate.
4. **Google Cloud project + OAuth credentials** — needed alongside the
   developer token to actually authenticate API calls.
5. **Basic Access** (the tier to request first) allows up to 15,000
   API operations/day against both test and production accounts — enough
   for this use case; no need to request Standard/higher access initially.

Source: [Google Ads API — Developer Token](https://developers.google.com/google-ads/api/docs/api-policy/developer-token), [Access Levels](https://developers.google.com/google-ads/api/docs/api-policy/access-levels)

## What to do with this once you have it

Once both are approved, give Claude Code:
- Meta: the ad account ID + a long-lived access token
- Google: the developer token, OAuth client ID/secret, and the 10-digit
  customer ID for the Ads account to target

From there, the `AdCampaign` table and `/dashboard/campaigns` page already
exist to receive real performance data (impressions, clicks, cost-per-lead)
— the remaining work is writing the API client calls themselves, which is
a much smaller task than the account setup above.

## In the meantime

The Campaigns page works today as a **manual tracker** — log campaigns you
run directly through Meta/Google's own ad managers, and record the
performance numbers here by hand until the API connection exists.
