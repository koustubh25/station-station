---
title: 'Part 4: Building Station Station - Where SDD Helped (and Where It Didn''t)'
published: false
description: An honest look at Spec-Driven Development's real-world benefits and limitations through actual debugging challenges from Station Station.
tags: 'debugging, ai, productivity, development'
series: Building with Spec-Driven Development
id: 2989892
---

In Parts 1-3, we covered Spec-Driven Development, the Station Station project, and the agent-os workflow. We saw a structured process that delivered 8 features, fully deployed and working. But I've been painting a rosy picture. Let me be honest about the challenges.

This part is about the real development experience: Where did the structured SDD approach actually help? Where did I still struggle despite having specs and tasks? What problems can structure solve, and what problems require good old-fashioned debugging?

If you're considering SDD for your next project, this is the part you need to read. Because understanding what structure can and can't solve is critical to setting realistic expectations.

## Challenge 1: Cloudflare Authentication Bypass

Let me start with the most frustrating part of the entire project: getting authentication to work with the Myki portal.

**The Context:**
The whole project depends on accessing Myki transaction data. No authentication = no data = no project. This was the critical blocker. Everything else was blocked until this worked.

**The Problem:**
The Myki portal is protected by Cloudflare Turnstile, which actively detects and blocks headless browsers. My first attempt using standard Playwright headless mode failed immediately with the "Verifying you are human..." overlay blocking form access.

**The Spec:**
"Use Playwright to authenticate with Myki portal and extract session tokens for API calls."

Simple requirement, right? But the spec didn't capture the complexity of Cloudflare bot detection.

### How SDD Helped

The structured approach provided a framework for tackling this beast:

**Clear success criteria:** "Extract Bearer token from authentication response" - The spec told the AI (and me) exactly what success looked like, even if neither of us knew how to get there yet.

**Task breakdown kept me focused:** Instead of having the AI try to solve "make authentication work" all at once, the tasks broke it down into pieces:
1. Launch browser with Playwright
2. Navigate to login page
3. Fill in credentials
4. Submit form
5. Extract authentication tokens

When the AI's implementation of step 3 (fill in credentials) was blocked by Cloudflare, the task breakdown showed me exactly where the problem was.

**Documentation of attempts:** Each failed approach got documented in the spec as "out of scope" or "doesn't work because..." This prevented me from asking the AI to retry the same failed approaches days later.

### What SDD Couldn't Solve

But here's the brutal truth: **specs don't solve hard technical problems for you.**

The AI tried implementing authentication multiple ways based on the spec. Each attempt failed. Over two days, I kept iterating:

**Attempt 1: AI implements standard headless Playwright**
```python
browser = playwright.chromium.launch(headless=True)
```
Result: Blocked by Cloudflare immediately. "Verifying you are human..."

**Attempt 2: I ask AI to try headed mode (visible browser)**
```python
browser = playwright.chromium.launch(headless=False)
```
Result: Better, but still detected as automation. Random CAPTCHA challenges.

**Attempt 3: I ask AI to try user-agent and header spoofing**
```python
context = browser.new_context(user_agent="...")
```
Result: Cloudflare is smarter than that. Still blocked.

**Attempt 4: AI tries stealth mode plugins**
Result: Helped a bit, but not consistent. Sometimes worked, sometimes didn't.

### The Solution (After Two Days of Frustration)

What finally worked: **Browser profile trust signals**

After researching Cloudflare bypass techniques, I figured out the solution and told the AI to implement it:

```python
# Create empty Chrome profile directory structure
profile_dir = create_empty_chrome_profile()
# Launch with profile - appears as "real" browser to Cloudflare
browser = playwright.chromium.launch_persistent_context(
    user_data_dir=profile_dir,
    headless=False
)
```

The profile directory contains just enough metadata (Cookies, Preferences, History files - all empty) to make Playwright look like a legitimate Chrome browser instead of automation.

### Why This Was So Frustrating

**The spec couldn't help because:**
- This required deep knowledge of browser fingerprinting and bot detection
- Solutions aren't documented well (Cloudflare actively tries to prevent bypass)
- Trial and error was the only way to find what worked
- Each attempt took 5-10 minutes to test (AI implements → I run the code → see if blocked)

**What I actually needed to do:**
- Research how Cloudflare Turnstile detects automation
- Learn that browser profiles affect fingerprinting
- Try approach after approach until something worked
- Debug headless browser issues by inspecting what Cloudflare was detecting

None of this came from the spec. The spec told the AI *what* to achieve. But figuring out *how* required me to research, experiment, find the solution, and then tell the AI to implement it.

### The Takeaway

**What SDD provided:**
- Clear goal to work toward (extract Bearer token)
- Focus on one step at a time instead of being overwhelmed
- Documentation of failed approaches to avoid repetition
- Motivation to keep going (this was Task 1 on a roadmap of 8 features - couldn't give up)

**What SDD couldn't provide:**
- Technical solution to Cloudflare bypass
- Knowledge of browser fingerprinting
- Shortcuts to avoid trial-and-error debugging
- The actual working approach (that required research and experimentation)

**Would specialized subagents have helped?**
Honestly, I don't know—I didn't try them for this problem. Agent-os has advanced features like specialized research agents and orchestrated task execution that might have helped with researching Cloudflare bypass techniques. But I was using the standard workflow, so I can't say whether those advanced features would have shortened the two-day struggle.

**Lesson learned:**
SDD gives you structure to tackle hard problems systematically. But **hard problems are still hard**. Structure doesn't replace technical knowledge, research, and persistence. It just gives you a framework to keep trying without getting lost.

When I finally got authentication working after two days, having it documented as "Task 1: COMPLETE ✓" with detailed notes on the working approach was incredibly valuable. Future features could reference "see Task 1 for Cloudflare bypass pattern." Without that documentation, I might have forgotten the solution by the time I needed to debug it again.

## Challenge 2: The Multi-Layer Bug

After finally getting authentication working, I ran into a different kind of frustration: the `manualAttendanceDates` feature bug.

**The Context:**
This requirement came much later, after the entire end-to-end system was already working. The app was successfully tracking attendance based on Myki transactions, deployed and running. But then I realized I needed a way to record office attendance on days when I drove to work instead of taking the train. No Myki transaction = no automatic detection. The solution was to add a `manualAttendanceDates` config field where I could explicitly list dates I was in the office.

This was an enhancement to an already-working system, not part of the original implementation.

**The Spec:**
Clear requirements. Well-defined tasks. Config schema documented. Expected behavior spelled out.

**The Implementation:**
Feature got implemented according to the tasks. Initial version deployed.

**The Problem:**
Manual dates weren't showing up correctly. But it wasn't just one bug—it was multiple issues across different parts of the system.

### How SDD Helped

Having the spec gave me a debugging roadmap:

1. **Check the spec requirements** - What should happen? "Manual dates should appear on the calendar with the same styling as PTV-detected dates"
2. **Follow the task breakdown** - Config parsing → Python backend → GitHub Actions workflow → JSON output → Frontend rendering
3. **Trace the data flow** - The spec documented the exact data structure at each layer

I could systematically check each layer by reviewing the code:
- **Python code:** Reviewing the implementation, I could see it wasn't properly merging manual dates with PTV-detected dates
- **Workflow file:** Looking at GitHub Actions, I realized it needed updates to handle the new field
- **UI:** Checking the frontend code, I spotted where it needed changes to render manual dates correctly

This wasn't a single bug, but multiple integration issues across three different components.

### What SDD Couldn't Solve

Even with perfect specs, I still had to:
- **Actually review the code** across all three layers to spot the issues
- **Give the AI specific hints** - "Look at how manual dates are merged in the Python code," "Check the workflow file," "The UI might not be checking the right field"
- **Understand the integration points** - recognizing that adding one field means touching Python backend, GitHub Actions workflow, and React frontend
- **Connect the dots across components** - understanding how the config file flows through Python processing, gets written to JSON, picked up by GitHub Actions, and rendered by the UI

The spec told me *what* should happen. It didn't tell me that integrating a new field into an existing multi-layer system would require touching all these different pieces. The AI could implement each fix once I pointed it to the right location, but finding those locations required me to review the code and understand the full data flow.

### The Takeaway

**What SDD provided:**
- Clear expected behavior to test against
- Systematic way to isolate which layer was failing
- Documentation of the intended data structure

**What still required human debugging:**
- Understanding multi-layer integration issues
- Recognizing when different components had different assumptions
- Finding the exact line where the mismatch occurred

## Challenge 3: Timezone Handling

**The Context:**
Calendar dates were displaying incorrectly—off by 1 day from the actual values in `attendance.json`.

**The Spec:**
"Display attended days on calendar matching the dates in the JSON file exactly."

Simple, right? Match the dates. But there was a subtle problem.

### How SDD Helped

The spec was clear about *what* should happen (dates must match), which made it obvious when they didn't. Without a spec, I might have thought "close enough" or missed the off-by-one bug entirely.

The task breakdown also helped isolate the problem:
- Task: "Parse attendance dates from JSON"
- Task: "Mark calendar tiles for attended dates"

The bug was in the date parsing task, not the calendar rendering task. Task isolation made debugging faster.

### What SDD Couldn't Solve

The spec said "match the dates exactly" but didn't specify *how* to handle timezones. The bug was subtle:

```javascript
// Initial implementation - caused timezone conversion
const dateString = date.toISOString().split('T')[0];
// For dates near midnight, UTC conversion shifts the date!
```

The problem: JavaScript's `toISOString()` converts to UTC. For dates near midnight, this can shift the date forward or backward. Nov 1, 2024 01:00 AEDT becomes Oct 31, 2024 14:00 UTC—wrong day!

**Why the spec didn't prevent this:**
The spec didn't say "use local timezone, not UTC" because I didn't think about timezones when writing it. The requirement seemed obvious: match the dates. But "obvious" hides assumptions.

### The Fix

```javascript
// Corrected implementation - uses local timezone
const dateString = date.toLocaleDateString('en-CA'); // YYYY-MM-DD format
```

### The Takeaway

**What SDD provided:**
- Clear success criteria (dates must match exactly)
- Quick detection that something was wrong
- Task isolation to narrow down where the bug was

**What SDD didn't prevent:**
- Subtle implementation details (timezone handling)
- Hidden assumptions in "obvious" requirements
- Need for domain knowledge (how JavaScript handles dates)

**Lesson learned:**
Good specs need to surface non-obvious assumptions. "Match the dates" should have been "Match the dates using local timezone to avoid UTC conversion issues." But you often don't know to specify this until you've been bitten by the bug.

## Challenge 4: Third-Party Library Integration

**The Context:**
Integrating the `date-holidays` npm package to automatically detect Victoria public holidays.

**The Spec:**
"Use date-holidays library to fetch Victoria public holidays. Display them on the calendar with red text."

### How SDD Helped

The spec documented exactly which library to use and what the expected behavior was. When the integration didn't work as expected, I could reference the spec to confirm what was supposed to happen.

### What SDD Couldn't Solve

The library returned dates in an unexpected format: `"YYYY-MM-DD HH:MM:SS"` strings instead of JavaScript Date objects.

```javascript
// Initial attempt based on spec
const holidayDate = new Date(holiday.date);
// Assumed library returns Date objects - it doesn't!
```

**Why the spec didn't prevent this:**
The spec said "use the library" but didn't document the exact return format because I hadn't investigated the library deeply when writing the spec. I assumed standard Date objects.

### The Fix

I had to inspect the actual library output, recognize the format mismatch, and handle it explicitly:

```javascript
// Working solution after investigation
const dateString = holiday.date.substring(0, 10); // "2025-11-04"
const [year, month, day] = dateString.split('-').map(Number);
const holidayDate = new Date(year, month - 1, day); // Uses local timezone
```

### The Takeaway

**What SDD provided:**
- Documentation of which library to use (no decision paralysis)
- Clear requirement for what should be displayed (public holidays with red text)
- Task to test the integration

**What SDD didn't prevent:**
- Runtime surprises from third-party libraries
- Need to investigate actual library behavior vs documented behavior
- Format mismatch that only appears when you run the code

**Lesson learned:**
Specs can't predict every third-party library quirk. You discover these by running code and inspecting actual output. The structured approach helps you document the quirks once you find them, so future tasks can reference the pattern.

## Challenge 5: User Preferences vs Developer Assumptions

**The Context:**
During development, weekends were displaying in red text (standard react-calendar behavior). I assumed this was confusing since it wasn't attendance data.

**The Plan:**
Remove the red weekend styling via CSS override. Seemed like a clean UI improvement.

**What Actually Happened:**
Before implementing the change, I asked the user (myself, wearing the user hat instead of developer hat). Response: "I really liked keeping weekends and public holidays in red."

I almost removed a feature I valued because I was thinking like a developer, not a user.

### How SDD Helped

The structured workflow created natural checkpoints for user feedback:
- After completing a task group, review with user
- Before removing functionality, validate with user
- Spec updates require user approval

Without this structure, I would have just removed the feature mid-coding session without stopping to think "Should I ask about this?"

### What SDD Couldn't Solve

SDD doesn't tell you what users want. It creates opportunities to ask, but you still have to:
- Actually ask the question
- Listen to the answer
- Override your own assumptions

### The Takeaway

**What SDD provided:**
- Natural review checkpoints to get user feedback
- Process that encourages "ask before removing"
- Documentation of decisions (why we kept the feature)

**What SDD didn't prevent:**
- Making wrong assumptions in the first place
- Need for actual user communication
- Temptation to "just fix it" without asking

**Lesson learned:**
Structure creates opportunities for better decisions, but you still have to take advantage of those opportunities. The review checkpoint is useless if you skip it.

## Where SDD Provided the Most Value

After going through these challenges, here's where the structured approach actually helped:

### 1. Clear Success Criteria

Every bug was obvious because the spec defined success. "Dates should match exactly" meant off-by-one was clearly wrong. Without specs, I might have rationalized it: "Close enough, probably a display thing."

### 2. Systematic Debugging

Task breakdown gave me a debugging roadmap. Instead of randomly checking files, I could trace the data flow through the task list:
1. Config parsing (Task 1)
2. Backend processing (Task 2)
3. JSON output (Task 3)
4. Frontend rendering (Task 4)

Check each layer systematically until you find the broken one.

### 3. Documentation of Decisions

When I came back a week later to add a new feature, the specs told me:
- Why certain approaches were chosen
- What assumptions were made (and documented)
- How data flows through the system

Without this documentation, I would have re-learned the codebase every time.

### 4. Review Checkpoints

The workflow forced me to pause and review:
- After each task group
- Before major changes
- When user feedback was needed

These pauses prevented rushing ahead with wrong assumptions.

## Where SDD Couldn't Replace Human Judgment

But let's be honest about what structure can't solve:

### 1. Multi-Layer Integration Issues

Specs describe individual components well. But when components need to work together, you still have to understand the full picture. The manualAttendanceDates bug required understanding backend + frontend + data contract all at once.

### 2. Hidden Assumptions and Edge Cases

"Match the dates" seemed clear until timezone conversion bit me. "Use the library" seemed clear until format mismatches appeared. Good specs surface assumptions, but you often don't know what to surface until you've been bitten.

### 3. Third-Party Library Quirks

Specs can't predict runtime behavior of external dependencies. You discover these by running code, inspecting output, and debugging when things don't work as documented.

### 4. User Preferences and Domain Knowledge

Structure can't tell you what users value or what domain-specific constraints matter. You still need actual user communication and domain expertise.

## The Honest ROI of SDD

Let's be real about the time investment:

**Time spent on specs:** ~4-5 hours across all features
**Time spent on implementation:** ~2 days
**Time spent debugging:** ~4-6 hours (timezone, manualAttendanceDates, library integration)

**Total:** ~3 days for 8 features shipped and deployed

### Where SDD Saved Time

**Debugging was faster:**
- Systematic task-by-task checking vs random file jumping
- Spec told me what should happen vs guessing
- Data flow documented vs reverse-engineering it

**Resumability was huge:**
- Came back a week later, knew exactly where I left off
- Spec reminded me why decisions were made
- Task list showed what was done and what was next

**Fewer forgotten requirements:**
- Everything documented upfront vs relying on memory
- Edge cases captured in spec vs discovered in production
- Complete feature set shipped vs "80% done" abandonment

### Where SDD Cost Time

**Upfront spec creation:**
- 4-5 hours thinking and documenting
- But this is thinking time I'd need anyway, just formalized

**Learning the workflow:**
- First project with agent-os had a learning curve
- Second project would be faster

**Maintaining documentation:**
- When specs changed, had to update docs
- But this paid off when resuming work later

## The Takeaway

Spec-Driven Development isn't magic. It won't prevent bugs, eliminate debugging, or replace human judgment. But it provides:

- **Structure** when you'd otherwise be lost
- **Documentation** when you'd otherwise forget
- **Checkpoints** when you'd otherwise rush ahead with wrong assumptions
- **Resumability** when you'd otherwise re-learn the codebase

The challenges I faced—timezone bugs, library quirks, multi-layer issues—would have happened with or without SDD. The difference is how I dealt with them:

**Without SDD:** Random debugging, forgotten context, abandoned projects
**With SDD:** Systematic debugging, documented decisions, completed features

That's the honest ROI.

## What's Next

We've now seen the complete picture: the workflow (Part 3) and where it actually helps vs where you still struggle (Part 4). You know the realistic benefits and the honest limitations.

In Part 5, we'll wrap up with a decision framework: when should you use SDD for your project, and when is a simpler approach better? We'll also cover how to get started with Station Station yourself (it's free and open source), and where to go from here.

If you're ready to make the call on whether Spec-Driven Development fits your workflow, Part 5 has the answers.

---

**About This Series**

This is Part 4 of a 5-part series on Spec-Driven Development with agent-os:
- [**Part 1: Introduction to Spec-Driven Development**](#) <!-- Update with Dev.to URL after publishing -->
- [**Part 2: The Station Station Project - A Real-World Case Study**](#) <!-- Update with Dev.to URL after publishing -->
- [**Part 3: Agent-OS Workflow in Action**](#) <!-- Update with Dev.to URL after publishing -->
- **Part 4: Where SDD Helped (and Where It Didn't)** (you are here)
- [**Part 5: Should You Use Spec-Driven Development?**](#) <!-- Update with Dev.to URL after publishing -->
