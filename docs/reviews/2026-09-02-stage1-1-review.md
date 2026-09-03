<!-- PR TARGET: https://github.com/heekum-Kim/Heekum-Kim | Stage 1.1 (2.5 pts) -->
# Stage 1.1 review — engagement brief

**Brief:** [`docs/briefs/perfect-competition-brief.md`](https://github.com/heekum-Kim/Heekum-Kim/blob/main/docs/briefs/perfect-competition-brief.md)

> Checked 2026-09-02. This is the first feedback you have had from me, so it covers what the stage wants as much as what is in the repository. Your Stage 0 review is separate and you should read that one first — the two together are about three hours of work and they are both still open to you.

### What is in the file right now

docs/briefs/perfect-competition-brief.md was created on 30 August and it is a single blank line — one byte. The path is right and the commit is clean, so nothing is lost; the writing has not happened yet.

The same is true of AGENTS.md, RESUME.md, and prompt-log.md. They exist and they are empty. That is a recognisable pattern — the scaffold gets built in one sitting and the content is meant to follow — and it is easy to fix now and awkward to fix in three weeks.

### What this stage asks for

About a page, in your own words, written and committed before you build anything. Four parts:

- The problem. What is being decided, by whom, and what it costs to decide it badly. What is fixed, what you get to choose, and what limits the choice. The test is whether you can state it without re-reading the case page.

- What you are assuming. What you are taking as given, and which of those you would most want to test if you had more time.

- Your hypothesis. Three real numbers — how many beds of tomatoes, carrots, and mesclun — and the mechanism you think decides it. You are not graded on being right. A hedged prediction that would survive any outcome is the only kind that is worthless.

- How you would know you were wrong. The specific result that would falsify what you just wrote. This is where most of this cohort loses points, so write it carefully: "if the model shows a different mix" is true of every hypothesis ever written and tests nothing. "If the model plants more than 14 tomato beds, I underestimated how fast the 10 percent labor penalty compounds" is a real test.

### The shape of the case, so you can start from something

A market garden has 64 beds — 16 beds across four plots — and a 36-week season. Fixed costs are $20,000. The farmer is paid $50,000 and spends 720 hours in the field; up to four temporary workers are available at $25,000 each for 1,440 hours each. The farm cannot influence prices; it takes what the market gives.

Tomatoes earn $8,800 a bed, carrots $2,094, mesclun $2,700. The bed caps are 20, 20, and 30, which sum to 70 against 64 beds, so all three cannot be maxed and something has to give.

The part that makes it interesting is that labor compounds. Each additional bed of a crop raises the labor required for every bed of that crop — 10 percent per bed for tomatoes, 2.5 percent for carrots, 1.25 percent for mesclun. The crop that earns the most per bed also gets expensive the fastest, and the question is where those two things cross.

Pick a mix, say why, and say what result would tell you it was wrong. That is the whole deliverable, and an hour of honest thinking beats a polished page.

### Where you are in the sequence, and what i would do this week

Three stages are open. Stage 0 is the repository itself, Stage 1.1 is this brief, and Stage 1.2 — the specification and the Excel model — is due 6 September. You are behind, and it is recoverable, but only in that order: the brief has to be committed before the model exists, because Stage 1.3 asks you to explain why your prediction and your model disagreed and the commit history is the proof of which came first.

So: finish Stage 0 tonight (README bio and RESUME.md are the two that matter), write this brief tomorrow, and start the specification after that. If that is not realistic given what else you have on, tell me and we will work out what to prioritise — that conversation is much more useful now than in a week.

One thing already works in your favour: I have write access to your repository, so reviews reach you as pull requests attached to your actual files. Three people in this cohort have not set that up.

---

### How to work this review

Treat this PR the way an analyst treats feedback from a senior reviewer — a review is a proposal to engage with, not a checklist to rubber-stamp.

1. **Read it yourself first.** Form your own view before you change anything. Disagreeing *with a documented reason* is a legitimate, senior response.
2. **Stress-test it with an LLM.** Paste this review and your brief into your assistant and ask it to (a) explain anything you are unsure of, and (b) argue the *other side* — where might the reviewer be wrong, and what would you give up by making each change.
3. **Then write the changes yourself.** For a brief, this matters more than usual: a hypothesis you did not generate cannot be honestly compared against your model in Stage 3, and that comparison is the entire point of writing the brief first.
4. **Close the loop.** Reply in this thread with what you changed and what you pushed back on, then commit and push.

*One standing rule for this stage: do not revise your hypothesis to match what your model later tells you. If the model contradicts the brief, that is a finding, not an error — Stage 3 asks you to explain the gap, and a brief quietly edited to be right afterwards has nothing left to explain.*

— Adam
