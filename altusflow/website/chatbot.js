/**
 * AltusFlow.ai — Native AI Chat Assistant
 * Intent-based helper with deep product knowledge.
 */
(function () {
  'use strict';

  const QUICK_ACTIONS = [
    { label: 'What does AltusFlow do?', intent: 'overview' },
    { label: 'AI-powered websites', intent: 'websites' },
    { label: 'Meta ads & funnels', intent: 'ads' },
    { label: 'Lead sourcing', intent: 'lead_sourcing_specialist' },
    { label: 'Ideal client profile', intent: 'icp' },
    { label: 'Book a strategy call', intent: 'contact' },
  ];

  const RESPONSES = {
    overview: `**AltusFlow.ai** builds fully automated growth engines for high-value businesses.

We solve the "leaky bucket" problem — where you spend on traffic but lose deals because your website can't sell 24/7.

Our **3-vertical ecosystem** works as one integrated pipeline:

1. **Premium AI-Powered Websites** — conversion engines with a native 24/7 chat assistant
2. **Meta Ads & Sales Funnels** — targeted campaigns that turn cold clicks into booked calls
3. **Intent-Based Lead Sourcing** — AI that finds buyers on LinkedIn & social and drafts personalized outreach

Which area would you like to dive into?`,

    websites: `**The Conversion Engine** — Premium AI-Powered Websites

Every AltusFlow website is built for speed, clarity, and conversion — and ships with a **custom-trained AI chat assistant** baked in (not a bolt-on widget).

**What it does for you:**
• Answers customer questions in ~3 seconds, 24/7
• Qualifies leads with smart follow-up questions
• Books meetings directly into your calendar
• Handles objections while your team sleeps

**Why "native" matters:** The chatbot knows your offers, pricing tiers, and FAQs because it's trained on *your* business — not generic scripts.

**Best for you if:** Your site is a passive brochure, you miss after-hours inquiries, or your sales team wastes time on unqualified leads.

Want to see how it connects to ads and outbound? Just ask!`,

    ads: `**The Inbound Magnet** — Meta Ads & Sales Funnels

Stop burning budget on generic ads that drive clicks but not calls.

**What we build:**
• Targeted Meta (Facebook & Instagram) campaigns for your ideal buyer
• Psychological sales funnels designed for one outcome: **high-value booked calls**
• Landing pages wired into your native AI chatbot for instant qualification
• Retargeting sequences that bring warm prospects back

**How it connects:** Traffic from ads lands on your AltusFlow website where the AI assistant qualifies and books — no lead falls through the cracks.

**Best for you if:** You're spending on ads but cost-per-booked-call is too high, or leads go cold before your team responds.

Ask me about outbound sourcing or the full integrated pipeline!`,

    outbound: `**The Outbound Hunter** — Intent-Based Lead Sourcing

While your website and ads capture inbound demand, our outbound engine finds buyers who are **actively signaling intent** right now.

**How it works:**
• Custom AI scans LinkedIn, X/Twitter, and relevant social networks
• Identifies people posting about problems your business solves
• Drafts hyper-personalized outreach pitches for your executive review
• You approve and send — no spray-and-pray spam

**How it connects:** Buying signals from your chatbot and funnel data feed back into outbound targeting. Warm traffic loops back to funnels that already know how to close.

**Best for you if:** Your sales team wastes hours on manual research, or you want predictable outbound without hiring a full SDR team.

Ready to map this to your business? I can help you get started.`,

    process: `**How AltusFlow works — from leaky bucket to growth engine:**

**Step 1 — Diagnose**
We audit where revenue is leaking: slow follow-ups, passive website, weak ads, or manual outbound.

**Step 2 — Build the Conversion Engine**
We launch your premium website with native AI chat — your 24/7 sales floor.

**Step 3 — Turn on the Inbound Magnet**
Targeted Meta campaigns + psychological funnels drive qualified traffic into that engine.

**Step 4 — Deploy the Outbound Hunter**
AI finds high-intent buyers on social and drafts outreach for your review.

**Step 5 — Integrate & Automate**
All three systems share data in the background. Traffic, conversion, and outbound work as one pipeline — 24/7.

**Timeline:** Most clients see their conversion engine live within weeks; full ecosystem rollout depends on scope.

Want a personalized gap analysis? I can take you to our contact form.`,

    integration: `**The unfair advantage: one integrated pipeline**

Most agencies sell disconnected tools. AltusFlow clients get **autonomous systems that talk to each other:**

• **Ads → Website:** Campaign traffic lands on conversion-optimized pages with instant AI qualification
• **Chatbot → Outbound:** Buying signals and objection patterns inform who to target outbound
• **Outbound → Funnels:** Warm prospects hit funnels that already know their pain points
• **Everything → Optimization:** Data loops back to improve ad spend, chat scripts, and outreach

The result: you're not managing three vendors — you're running one growth engine that works while you sleep.

Which vertical should we prioritize for your business?`,

    problem: `**The Leaky Bucket** — sound familiar?

You spend thousands on traffic every month. The pipeline fills up… then nothing happens.

**Common leaks:**
• Website is a passive brochure — can't answer questions at 7 PM Saturday
• Sales follows up 3 days later; lead already booked a competitor
• Ads drive clicks but landing pages don't convert
• SDRs spend hours researching instead of closing

**The fix:** Turn your website into an active, 24/7 automated sales pipeline. AltusFlow combines premium design + native AI chat + automated traffic + intent-based outbound so nothing leaks.

What's your biggest bottleneck right now — website, ads, or outbound research?`,

    pricing: `**Investment & scope**

AltusFlow builds custom growth engines — not one-size-fits-all packages — so pricing depends on:

• Current website state and chatbot complexity
• Meta ad budget and funnel depth
• Outbound volume and target markets
• How many of the 3 verticals you need live

**What I can tell you:** Clients invest in an integrated system because replacing 3–4 disconnected tools + agency retainers often costs more long-term — with worse results.

**Best next step:** Fill out our **"Identify Your Revenue Gaps"** form and we'll map exactly what you need and what ROI to expect — no generic quote sheet.

<a href="#contact" class="chat-cta-link">→ Analyze My Systems</a>`,

    contact: `**Let's map your revenue gaps.**

The fastest way to get a personalized plan is our short intake form. We'll review:

• Your current website & whether you're missing 24/7 chat
• Ad performance and funnel conversion rates
• How much time your team spends on manual research

**Takes 2 minutes.** Our team will follow up with a tailored systems analysis.

<a href="#contact" class="chat-cta-link">→ Go to Contact Form</a>

Or tell me your biggest challenge here — website, ads, or outbound — and I'll point you in the right direction.`,

    who: `**Who AltusFlow is built for:**

High-value businesses where **one booked call = significant revenue** — and losing a lead hurts.

**Great fit:**
• B2B services, agencies, consultants, SaaS
• Companies spending $3k+/mo on marketing with weak conversion
• Teams that can't respond to leads 24/7
• Sales leaders tired of SDRs doing manual LinkedIn research

**Not ideal for:**
• Low-ticket e-commerce only plays
• Businesses that don't rely on calls/meetings to close

Does that sound like you? Tell me your industry and I'll share what's most relevant.`,

    icp: `**AltusFlow Ideal Client Profile (ICP)**

**Industry:** B2B professional services, agencies, consulting, B2B SaaS, financial advisory, IT services

**Company size:**
• Revenue: $2M–$100M (sweet spot: $5M–$30M)
• Employees: 10–500
• Marketing spend: $3,000+/month

**Decision-makers we target:**
• Founder / CEO
• CMO / VP Marketing
• Head of Growth
• VP Sales

**Top pain signals (need 2+):**
• Leaky bucket — traffic without conversion
• Passive website, no 24/7 chat
• After-hours missed leads
• Low ad ROI / high CPC, few booked calls
• SDRs spending 10+ hrs/week on manual research

**We exclude:** Direct competitors, sub-10-employee shops (unless high ACV), low-ticket e-commerce, unverified contacts.

Sound like your company? <a href="#contact" class="chat-cta-link">Let's map your gaps →</a>`,

    lead_sourcing_specialist: `**How AltusFlow's Outbound Hunter sources leads**

Our lead sourcing engine follows a strict, accuracy-first workflow:

**1. Research** — Scans LinkedIn, X/Twitter, company sites, Google News, and job postings for ICP-aligned prospects showing intent signals.

**2. Qualify** — Every lead must pass ALL criteria:
• Revenue >$2M OR marketing spend >$3k/mo
• Decision-maker is Founder, C-level, or VP
• Active on social in last 30 days OR recent trigger (funding, hire, launch)
• Verified LinkedIn/website — no generic unverified contacts

**3. Personalize** — Each qualified lead gets a 1-sentence hook tied to a real trigger:
• "Posted about lead gen struggles last week…"
• "Just hired an SDR — our intent engine replaces manual research…"
• "Running Meta ads but site has no chat — we plug that leak…"

**4. Output** — Clean table: Company, Decision Maker, Title, URL, Personalization Hook. Borderline leads flagged in "Review Needed" — never fabricated.

**This is what we build for clients** — not just for ourselves. Want this running for your pipeline?

<a href="#contact" class="chat-cta-link">→ Start your systems analysis</a>`,

    greeting: `Hey! 👋 I'm the AltusFlow AI assistant — here to help you understand how we plug revenue leaks and build automated growth engines.

**I can help with:**
• Our 3 core systems (websites, ads, outbound)
• How intent-based lead sourcing works
• Whether you're a fit (ICP criteria)
• Getting you to a strategy call

What would you like to know?`,

    thanks: `You're welcome! If anything else comes up — pricing, timelines, or how the chatbot works on your site — just ask.

When you're ready, <a href="#contact" class="chat-cta-link">book your systems analysis here</a>. We're here to help.`,

    fallback: `Great question. Here's what I know for sure:

AltusFlow.ai builds **integrated growth engines** — not disconnected tools. Our 3 verticals are:

1. **AI-powered websites** with native 24/7 chat
2. **Meta ads & sales funnels** for inbound
3. **Intent-based lead sourcing** for outbound

Could you rephrase, or tap one of the quick buttons below? For a detailed answer tailored to your business, <a href="#contact" class="chat-cta-link">submit the contact form</a> and our team will follow up personally.`,
  };

  const INTENT_PATTERNS = [
    { intent: 'greeting', patterns: [/^(hi|hello|hey|yo|good\s*(morning|afternoon|evening)|sup)\b/i, /^howdy/i] },
    { intent: 'thanks', patterns: [/thank/i, /\bthanks\b/i, /appreciate/i, /helpful/i] },
    { intent: 'contact', patterns: [/book|call|demo|meeting|schedule|talk to|speak with|contact|get started|sign up|strategy|consult/i, /analyze my systems/i] },
    { intent: 'pricing', patterns: [/pric(e|ing)|cost|how much|budget|invest|afford|package|plan/i, /\$\d/] },
    { intent: 'websites', patterns: [/website|web\s*site|chatbot|chat\s*bot|ai\s*chat|conversion engine|landing page|storefront|brochure/i, /missing chatbot/i, /outdated website/i] },
    { intent: 'ads', patterns: [/meta|facebook|instagram|ad[s]?|funnel|inbound|ppc|campaign|click/i, /low ad conversion/i, /burning cash/i] },
    { intent: 'outbound', patterns: [/outbound|linkedin|sdr|prospect|outreach|cold email|social network|hunter/i, /wasting time on research/i] },
    { intent: 'lead_sourcing_specialist', patterns: [/lead sourc|find leads|source leads|personalization hook|decision.?maker|trigger event/i, /how do you find/i, /lead table/i] },
    { intent: 'icp', patterns: [/ideal customer|ideal client|\bicp\b|target (audience|market)|who is (this|it) for|good fit|company size/i, /fit for me|qualif(y|ication) criteria/i] },
    { intent: 'integration', patterns: [/integrat|connect|work together|pipeline|ecosystem|unfair advantage|autonomous|24\/7|background/i, /three system|3 vertical|all three/i] },
    { intent: 'process', patterns: [/how (does|do) it work|how long|timeline|process|step|onboard|get started|what happens/i, /how does altusflow/i] },
    { intent: 'problem', patterns: [/leaky bucket|leak|losing (revenue|deal|lead)|problem|bottleneck|challenge|struggle/i, /why.*not convert/i] },
    { intent: 'who', patterns: [/industr|b2b|saas|agency|consult/i, /do you work with/i, /right for me/i] },
    { intent: 'overview', patterns: [/what (is|does) altusflow|tell me about|what do you (do|offer)|services|about you|who are you/i, /^help$/i] },
  ];

  function matchIntent(text) {
    const normalized = text.trim().toLowerCase();
    for (const { intent, patterns } of INTENT_PATTERNS) {
      if (patterns.some((p) => p.test(normalized))) return intent;
    }
    return null;
  }

  function getResponse(intentOrText) {
    if (RESPONSES[intentOrText]) return RESPONSES[intentOrText];
    const intent = matchIntent(intentOrText);
    return RESPONSES[intent] || RESPONSES.fallback;
  }

  function formatMessage(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-medium">$1</strong>')
      .replace(/\n/g, '<br>')
      .replace(/• /g, '<span class="text-accent-light">•</span> ');
  }

  // ── DOM refs (set on init) ──
  let panel, messagesEl, inputEl, toggleBtn, closeBtn, sendBtn, quickActionsEl;

  function scrollToBottom() {
    requestAnimationFrame(() => {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    });
  }

  function addMessage(content, role) {
    const wrap = document.createElement('div');
    wrap.className = role === 'user' ? 'flex justify-end' : 'flex justify-start';

    const bubble = document.createElement('div');
    if (role === 'user') {
      bubble.className = 'max-w-[85%] rounded-2xl rounded-br-md bg-accent px-4 py-3 text-sm leading-relaxed text-white';
      bubble.textContent = content;
    } else {
      bubble.className = 'max-w-[90%] rounded-2xl rounded-bl-md glass px-4 py-3 text-sm leading-relaxed text-zinc-300';
      bubble.innerHTML = formatMessage(content);
      bubble.querySelectorAll('a.chat-cta-link').forEach((link) => {
        link.addEventListener('click', () => closePanel());
      });
    }

    wrap.appendChild(bubble);
    messagesEl.appendChild(wrap);
    scrollToBottom();
  }

  function showTyping() {
    const el = document.createElement('div');
    el.id = 'chat-typing';
    el.className = 'flex justify-start';
    el.innerHTML = `
      <div class="glass flex items-center gap-1.5 rounded-2xl rounded-bl-md px-4 py-3">
        <span class="chat-typing-dot"></span>
        <span class="chat-typing-dot" style="animation-delay:0.15s"></span>
        <span class="chat-typing-dot" style="animation-delay:0.3s"></span>
      </div>`;
    messagesEl.appendChild(el);
    scrollToBottom();
    return el;
  }

  function removeTyping() {
    document.getElementById('chat-typing')?.remove();
  }

  function botReply(intentOrText) {
    const typing = showTyping();
    const delay = 600 + Math.random() * 400;
    setTimeout(() => {
      removeTyping();
      addMessage(getResponse(intentOrText), 'bot');
      renderQuickActions();
    }, delay);
  }

  function handleUserMessage(text) {
    const trimmed = text.trim();
    if (!trimmed) return;
    addMessage(trimmed, 'user');
    inputEl.value = '';
    sendBtn.disabled = true;
    quickActionsEl.innerHTML = '';
    botReply(trimmed);
    setTimeout(() => { sendBtn.disabled = false; inputEl.focus(); }, 1200);
  }

  function renderQuickActions() {
    quickActionsEl.innerHTML = '';
    QUICK_ACTIONS.forEach(({ label, intent }) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chat-quick-btn shrink-0 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs font-medium text-zinc-300 transition hover:border-accent/30 hover:bg-accent/10 hover:text-white';
      btn.textContent = label;
      btn.addEventListener('click', () => {
        addMessage(label, 'user');
        quickActionsEl.innerHTML = '';
        botReply(intent);
      });
      quickActionsEl.appendChild(btn);
    });
  }

  function openPanel() {
    panel.classList.remove('hidden');
    panel.classList.add('chat-panel-open');
    toggleBtn.classList.add('hidden');
    inputEl.focus();
  }

  function closePanel() {
    panel.classList.remove('chat-panel-open');
    panel.classList.add('hidden');
    toggleBtn.classList.remove('hidden');
  }

  function init() {
    panel = document.getElementById('chat-panel');
    messagesEl = document.getElementById('chat-messages');
    inputEl = document.getElementById('chat-input');
    toggleBtn = document.getElementById('chat-toggle');
    closeBtn = document.getElementById('chat-close');
    sendBtn = document.getElementById('chat-send');
    quickActionsEl = document.getElementById('chat-quick-actions');

    if (!panel) return;

    toggleBtn.addEventListener('click', openPanel);
    closeBtn.addEventListener('click', closePanel);

    sendBtn.addEventListener('click', () => handleUserMessage(inputEl.value));
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleUserMessage(inputEl.value);
      }
    });
    inputEl.addEventListener('input', () => {
      sendBtn.disabled = !inputEl.value.trim();
    });

    // Welcome message on first open
    let welcomed = false;
    toggleBtn.addEventListener('click', () => {
      if (!welcomed) {
        welcomed = true;
        setTimeout(() => {
          addMessage(RESPONSES.greeting, 'bot');
          renderQuickActions();
        }, 300);
      }
    });

    // Auto-open from hero CTA
    document.querySelectorAll('a[href="#chatbot-demo"]').forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        openPanel();
        if (!welcomed) {
          welcomed = true;
          setTimeout(() => {
            addMessage(RESPONSES.greeting, 'bot');
            renderQuickActions();
          }, 300);
        }
        document.getElementById('chatbot-demo')?.scrollIntoView({ behavior: 'smooth' });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
