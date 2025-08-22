

## ✅ Feature / Function Breakdown with Priority

- **Presentation (5)** → Demo script, Loom video, live rehearsal. Critical path: must be rehearsed and polished before 8/25.
    
- **Hosting (5)** → Public endpoint by 8/18. Without this, DemoDay isn’t viable.
    
- **Hosting (3)** → Boffo Games website integration. “Very nice to have” but not core. Can be deferred if tight.
    
- **Visual Appeal (4)** → Spacebar visuals (custom Thud icon already in place). Adds polish for DemoDay.
    
- **Functionality (5)** → Staying on topic. Reliability required (no random fallback).
    
- **Functionality (4)** → Staying in character. Prompt tuning needed (avoid generic summaries).
    
- **Functionality (4)** → Progressive hints. Good UX, fits DemoDay narrative.
    
- **Functionality (2)** → Multiple characters. Nice-to-have only; skip if it risks core.
    
- **Functionality (1)** → Audio. Optional stretch.
    
- **Functionality (3)** → More hint data. Expands coverage, useful if time.
    
- **NFR (3)** → Reasonable latency. Already acceptable (~4.5s multi-query); improve if possible.
    
- **NFR (4)** → Observability. LangSmith already integrated; mostly for debugging.
    

---

## 📅 Timeline Alignment

- **Today (8/17):** Prioritize hosting prep & character prompt tuning. Build task detail list.
    
- **8/18 (Hosting):** Public endpoint live = Certification-level requirement.
    
- **8/19–20 (Functionality):** Lock down staying on-topic/in-character, add progressive hints.
    
- **8/21 (Code Freeze):** Drop optional features (multi-character, audio).
    
- **8/22 (Polish):** Visual appeal, branding, doc updates.
    
- **8/24 (Video):** Record professional demo with stable features.
    
- **8/25 (Rehearsal):** Full run-through, buffer for glitches.
    

---

That gives you:

- **Must have (5s)** done by Mon–Wed.
    
- **Personal satisfaction (4s)** polished by Thu–Fri.
    
- **Nice/optional (≤3s)** only if you still have cycles.


## 📅 **DemoDay Work Plan**

**Sunday 8/17 (10h)**

- Planning + setup
    
    - Finalize task breakdown for hosting, character polish, UI, and demo flow.
        
    - Prioritize any blockers (dependencies, environment, DNS).
        
    - Light prompt tuning session to start refining Thud’s voice.
        

**Monday 8/18 (6h) → Public Hosting Done**

- VPS setup (Linode/Hetzner) + Cloudflare DNS.
    
- Install stack (Python, Node, FastAPI, Next.js).
    
- Deploy MVP app with SSL (Let’s Encrypt).
    
- Verify external access: `thud.boffo.games` reachable.
    

**Tuesday 8/19 (10h)**

- Backend polish: ensure deterministic hint responses (no random fallback).
    
- Implement small features: progressive hint memory, error messages, logging polish.
    
- Draft stretch features if time (mock Fleebix fallback).
    

**Wednesday 8/20 (10h) → Functionality Complete**

- Lock in all core functionality.
    
- Test hint coverage and escalation.
    
- Validate hosting reliability (simulate grader conditions).
    
- Finalize character prompt tuning (eliminate generic summaries).
    

**Thursday 8/21 (10h) → Code Freeze**

- Freeze feature work.
    
- Focus on **bug fixes + stability** only.
    
- Expand test coverage.
    
- Tag repo release for DemoDay.
    

**Friday 8/22 (10h)**

- Polish UI: session persistence, loading states, timestamps, optional styling.
    
- Improve documentation: update README, add MERGE.md, deployment notes.
    
- Run clean machine test again.
    

**Saturday 8/23 (0h)**

- Rest/reset buffer day.
    

**Sunday 8/24 (10h) → Video Complete**

- Script demo (3–5 mins).
    
- Record Loom demo (multiple takes if needed).
    
- Edit + confirm link stable.
    

**Monday 8/25 (8h) → Rehearsal Complete**

- Dry run full presentation: intro, live demo flow, Q&A prep.
    
- Backup plan in case of network/demo failure.
    
- Share repo + demo links with peers for feedback.
    

**Tuesday 8/26 → Presentation 6PM**

- Light touch-ups only.
    
- Focus on presentation delivery.
    
- Go live at 6PM sharp with tested flow.