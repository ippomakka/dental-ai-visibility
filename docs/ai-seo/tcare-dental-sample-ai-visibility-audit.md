# AI Visibility Audit: TCare Dental Centre

**Website:** https://tcaredental.com.au/  
**Industry:** Dental / Orthodontics / Cosmetic Dentistry  
**Locations:** Campsie + Villawood, NSW, Australia  
**Audit Type:** Sample AI Recommendation / GEO Audit  
**Prepared for:** Dental clinics wanting to appear in ChatGPT, Perplexity, Gemini, Copilot and AI-powered search

---

## Executive Summary

When patients ask AI tools questions like:

- “Who is the best dentist in Campsie?”
- “Where can I get Invisalign near Villawood?”
- “Best dental implants clinic near me”
- “Recommend a cosmetic dentist in Sydney’s southwest”

AI systems look for businesses they can **find, understand, trust and verify**.

TCare Dental Centre already has several strong foundations: clear dental services, two visible clinic locations, dentist/team pages, implant and Invisalign content, a working sitemap, and existing schema markup.

However, the site is not yet fully structured for AI recommendation systems. Key issues include incomplete local business schema, no visible homepage H1, no AI-readable business profile, no `llms.txt`, weak `sameAs` entity linking, limited location-specific treatment pages, and no obvious structured FAQ/review data.

**Bottom line:** TCare Dental is likely understandable to search engines at a basic level, but it is not yet optimized to be confidently recommended by AI systems for high-intent local dental prompts.

---

## Overall AI Recommendation Score

**Estimated Score: 52 / 100**

| Category | Score | Interpretation |
|---|---:|---|
| Crawlability & Indexability | 80/100 | Robots.txt and sitemap are accessible. No AI crawlers explicitly blocked. |
| Entity Clarity | 62/100 | Business, locations and services are visible, but not consistently structured. |
| Local AI Readiness | 55/100 | Campsie and Villawood are visible, but separate local entities are not fully defined. |
| Schema / Structured Data | 45/100 | Schema exists, but is incomplete, duplicated and missing key local fields. |
| AI-Readable Content | 35/100 | No `llms.txt`, markdown profile, service JSON, or AI-focused business summary detected. |
| Treatment Prompt Coverage | 58/100 | Implant and Invisalign pages exist, but location/treatment targeting could be stronger. |
| Trust & Review Signals | 45/100 | Dentist/team info exists, but reviews, credentials and proof are not fully machine-readable. |
| Competitor / Prompt Visibility | Not yet scored | Requires live prompt testing across AI/search platforms. |

---

## What TCare Dental Is Doing Well

### 1. Clear Core Services

The website clearly references high-value dental services including:

- Dental implants
- Full-arch / All-on-4 style implants
- Invisalign® clear aligners
- Braces
- Porcelain veneers
- Cosmetic dentistry
- General dentistry
- Root canal treatment
- Wisdom teeth removal
- Gum disease treatment
- Children’s dentistry

This gives AI systems a reasonable starting point for understanding what the clinic offers.

### 2. Two Physical Locations Are Visible

The site lists two clinic locations:

**TCare Dental Centre Villawood**  
27 Villawood Pl, Villawood NSW 2163  
Phone: (02) 8766 6698

**TCare Dental Centre Campsie**  
321 Beamish Street, Campsie NSW 2194  
Phone: (02) 8766 6699

This is valuable for local dental prompts. However, these locations should be made more machine-readable through dedicated location schema and local landing pages.

### 3. Sitemap Exists

The XML sitemap is live and references approximately 20 pages, including homepage, About, dentists/team, All-on-4 implants, clear aligner, payment plans/pricing, children’s dentistry, root canal treatment, wisdom teeth removal, dental crowns/bridges, and gum disease treatment.

This is good for discoverability, but the number of indexed pages appears light for a multi-location dental clinic with multiple high-value treatments.

### 4. Robots.txt Allows Crawling

The robots.txt file is simple and open:

```txt
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

Sitemap: https://tcaredental.com.au/sitemap_index.xml
```

No major AI/search crawlers appear to be explicitly blocked.

### 5. Schema Markup Exists

The site includes JSON-LD schema with types including:

- `Dentist`
- `Organization`
- `WebSite`
- `WebPage`

This is a positive starting point, but the schema needs cleanup and expansion.

---

## Key AI Visibility Gaps

### Gap 1: Homepage Has No Visible H1

Detected homepage heading structure:

- H1: none detected
- H2 examples: “Dentistry With Heart”, “Your Unique Smile, Our Commitment”
- H3 examples: “Dental Implants”, “Invisalign® Clear Aligner”, dentist names

Brand-led copy like “Dentistry With Heart” is warm for humans, but vague for machines.

**Why this matters:** AI systems benefit from a clear page-level statement of who the business is, where it operates, and what it offers.

**Recommended H1:**

> Dentist in Campsie & Villawood for Implants, Invisalign and Cosmetic Dental Care

Alternative:

> TCare Dental Centre — General, Cosmetic and Implant Dentistry in Campsie & Villawood

### Gap 2: Schema Is Present but Incomplete

The site has schema, but it appears incomplete for a dental/local business.

Detected issues:

- Organization/Dentist schema exists, but lacks full location data.
- `sameAs` array appears empty.
- Two different schema blocks reference similar organization data.
- One schema block uses `legalName: cb_james_admin`, which appears incorrect or accidental.
- One logo URL appears as `http://` instead of `https://`.
- No clear separate entities for Campsie and Villawood locations.
- No detected `FAQPage` schema.
- No detected `Service`/`OfferCatalog` structure for treatments.
- No detected structured dentist/provider relationships.

**Why this matters:** AI systems need consistent entity data. Conflicting or incomplete schema can reduce confidence.

### Gap 3: Two Locations Are Not Structured as Separate Local Entities

TCare Dental has two locations, but AI systems should be able to understand each one as a distinct local dental clinic.

Each location should have its own schema and landing page containing:

- clinic name
- address
- phone number
- opening hours
- geo coordinates
- booking URL
- services available
- dentists practicing there
- surrounding suburbs served
- Google Business Profile link
- review/profile links
- parking/accessibility notes if available

**Recommended location pages:**

- `/dentist-campsie/`
- `/dentist-villawood/`

### Gap 4: No AI-Readable Business Profile Detected

No `llms.txt` file was found at:

```txt
https://tcaredental.com.au/llms.txt
```

The site also does not appear to expose dedicated AI-readable files such as:

- `/business-profile.md`
- `/services.json`
- `/locations.json`
- `/dentists.json`
- `/faqs.md`
- `/schema.json`

**Why this matters:** AI-readable files are not a magic ranking factor, but they can help search agents and crawlers extract clean facts about the business.

**Recommended deliverable:** Create an AI Business Profile Pack containing `llms.txt`, `business-profile.md`, `services.json`, `locations.json`, `dentists.json`, `faq.md`, and improved JSON-LD schema.

### Gap 5: Treatment + Location Pages Are Underdeveloped

The site has treatment pages, but it could better map treatment intent to local patient prompts.

AI prompts may include:

- “Invisalign dentist in Campsie”
- “Dental implants near Villawood”
- “Cosmetic dentist Campsie”
- “Emergency dentist Villawood”
- “Best dentist near Belmore”

**Recommended page opportunities:**

- Invisalign in Campsie
- Invisalign in Villawood
- Dental Implants in Campsie
- Dental Implants in Villawood
- Cosmetic Dentist in Campsie
- Cosmetic Dentist in Villawood
- Emergency Dentist Campsie
- Emergency Dentist Villawood
- Family Dentist Campsie
- Family Dentist Villawood
- Orthodontist Campsie
- Orthodontist Villawood

These should be genuinely useful pages, not thin doorway pages.

### Gap 6: FAQ Content Should Be More Structured

AI systems often use FAQ-style content to answer patient questions.

Recommended FAQ examples:

#### Invisalign / Clear Aligners

- How much does Invisalign cost in Australia?
- How long does Invisalign treatment take?
- Is Invisalign suitable for adults?
- Is Invisalign better than braces?
- Can I get Invisalign at TCare Dental Campsie or Villawood?
- Do you offer payment plans for Invisalign?

#### Dental Implants

- How much do dental implants cost in Sydney?
- What is the difference between single implants and full-arch implants?
- Am I suitable for All-on-4 style implants?
- How long do dental implants last?
- Do you offer payment plans for implants?
- Which TCare Dental clinic provides implant consultations?

#### General Dentistry

- Do you accept new patients?
- Do you treat children?
- Are appointments available on Saturdays?
- What suburbs do you serve?
- Do you offer emergency dental appointments?

These FAQs should be included on relevant pages and marked up with valid `FAQPage` schema where appropriate.

### Gap 7: Trust Signals Need Stronger Machine-Readable Presentation

The site lists dentists and some AHPRA information, which is useful. But trust signals should be easier for AI systems to extract.

Recommended trust elements:

- dentist bios with qualifications
- AHPRA numbers
- years of experience
- treatment focus areas
- before/after case examples
- review snippets
- patient testimonials
- payment plan details
- technology used
- safety/treatment risk disclosures
- professional memberships

For dental/healthcare, trust and credentials are especially important because AI systems are cautious with medical recommendations.

---

## Suggested AI Buyer Prompt Test Matrix

### General Dentist Prompts

| Prompt | Why It Matters |
|---|---|
| Best dentist in Campsie | High-intent local discovery |
| Best dentist in Villawood | High-intent local discovery |
| Recommend a dental clinic near Campsie | Natural AI assistant prompt |
| Top-rated family dentist near Villawood | Review/trust intent |
| Dentist open Saturday near Campsie | Availability-based local intent |

### Orthodontic / Invisalign Prompts

| Prompt | Why It Matters |
|---|---|
| Best Invisalign dentist in Campsie | High-value treatment intent |
| Orthodontist near Villawood for clear aligners | Treatment + location intent |
| Where can I get Invisalign near Campsie? | Natural recommendation prompt |
| Best clear aligner dentist in Sydney’s southwest | Regional discovery prompt |

### Implant Prompts

| Prompt | Why It Matters |
|---|---|
| Best dental implants clinic in Campsie | High-value treatment intent |
| All-on-4 dental implants near Villawood | High-ticket procedure intent |
| Best dentist for full mouth implants in Sydney | Regional high-value prompt |
| Affordable dental implants near Campsie | Cost/payment-plan intent |

### Cosmetic Dentistry Prompts

| Prompt | Why It Matters |
|---|---|
| Best cosmetic dentist in Campsie | High-intent cosmetic prompt |
| Porcelain veneers dentist near Villawood | Specific treatment prompt |
| Smile makeover dentist in Sydney southwest | Regional cosmetic prompt |

For each prompt, the live audit should record:

- Does TCare Dental appear?
- Which competitors appear?
- What sources does the AI cite?
- What reasons does the AI give?
- Is TCare described accurately?
- What source/website gap caused competitors to appear instead?

---

## Recommended 30-Day Fix Plan

### Week 1: Entity + Schema Cleanup

1. Add a clear homepage H1.
2. Rewrite homepage intro for machine clarity.
3. Remove incorrect schema fields such as `legalName: cb_james_admin`.
4. Consolidate duplicate Organization schema.
5. Add full LocalBusiness/Dentist schema for each location.
6. Add `sameAs` links to trusted external profiles.
7. Use HTTPS URLs for logos and images.

### Week 2: Location AI Readiness

1. Create or strengthen Campsie location page.
2. Create or strengthen Villawood location page.
3. Add address, phone, opening hours, maps, parking/access notes.
4. Add suburbs served.
5. Add location-specific FAQs.
6. Add location-specific schema.

### Week 3: Treatment Prompt Coverage

1. Create/upgrade Invisalign Campsie/Villawood content.
2. Create/upgrade dental implant Campsie/Villawood content.
3. Add FAQ sections to implant and Invisalign pages.
4. Add treatment/service schema.
5. Add internal links from homepage/footer to high-value treatment pages.

### Week 4: AI Business Profile + Trust Layer

1. Publish `llms.txt`.
2. Publish AI-readable business profile.
3. Publish structured services and locations JSON.
4. Improve dentist/team bios with credentials and treatment areas.
5. Add review/testimonial sections where compliant.
6. Run first AI prompt visibility benchmark.
7. Produce before/after AI visibility report.

---

## Example AI-Readable Business Summary

> TCare Dental Centre is a dental clinic group serving Campsie, Villawood and surrounding suburbs in NSW, Australia. The clinic provides general dentistry, cosmetic dentistry, dental implants, full-arch implant treatment, Invisalign clear aligners, braces, veneers, children’s dentistry, wisdom teeth removal, root canal treatment, gum disease treatment and dental payment plan options. TCare Dental operates clinics at 321 Beamish Street, Campsie NSW 2194 and 27 Villawood Pl, Villawood NSW 2163. The practice team includes registered dental practitioners and offers consultations for patients seeking general dental care, orthodontic treatment, smile makeovers and implant dentistry.

---

## Suggested Paid Implementation Package

### AI Dental Visibility Fix Pack

**One-time setup:** AUD $1,500-$3,500 depending site access and scope.

Includes:

- homepage AI clarity rewrite
- schema cleanup and expansion
- two location entity profiles
- `llms.txt`
- AI-readable business profile
- services/locations JSON files
- FAQ sections for key treatment pages
- treatment/location page recommendations
- sameAs/citation map
- 10-prompt AI visibility baseline
- 30-day action plan

### Ongoing AI Recommendation Growth

**Monthly retainer:** AUD $1,500-$4,000/month.

Includes:

- monthly AI prompt tracking
- competitor visibility monitoring
- treatment/location content creation
- GBP/profile optimization recommendations
- citation/review strategy
- schema updates
- monthly AI visibility report

---

## Final Takeaway

TCare Dental already has a solid website foundation, visible service pages and two clear locations. The biggest opportunity is not rebuilding the site; it is adding the missing AI visibility layer.

The clinic needs to become easier for AI systems to:

1. identify as a dental provider,
2. understand by location,
3. match to treatment-specific patient prompts,
4. verify through trusted external profiles,
5. extract clean facts from structured data,
6. confidently recommend over nearby competitors.

**Recommended next step:** run live AI prompt tests against TCare Dental and 5-10 local competitors, then convert this technical audit into a patient-intent AI visibility report.
