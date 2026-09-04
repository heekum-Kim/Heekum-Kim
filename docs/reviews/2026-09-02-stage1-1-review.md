<!-- PR TARGET: https://github.com/heekum-Kim/Heekum-Kim | Stage 1.1 -->
# Stage 1.1 review — engagement brief

**Brief:** [`docs/briefs/perfect-competition-brief.md`](https://github.com/heekum-Kim/Heekum-Kim/blob/main/docs/briefs/perfect-competition-brief.md)

> Checked 2026-09-04. Your README and resume both landed this morning and they are real — that moved your Stage 0 off a hold and onto the floor, and it was the right thing to do first. This stage is the next one and it is due behind Stage 1.2 on 6 September, so the order below matters.

### Where things stand

docs/briefs/perfect-competition-brief.md exists at the right path and is one byte. The path and the commit are correct; the page has not been written.

AGENTS.md and prompt-log.md are also still one byte each, and CLAUDE.md, .gitignore and the analysis, capabilities, data and docs folders do not exist yet. Those belong to Stage 0 and are in that review.

### What this stage asks for

About a page in your own words, committed before you build anything. Four parts:

- The problem. What is being decided, by whom, and what it costs to decide it badly. What is fixed, what you get to choose, what limits the choice.

- What you are assuming, and which of those you would most want to test with more time.

- Your hypothesis. Three real numbers — beds of tomatoes, carrots and mesclun — and the mechanism you think decides it. You are not graded on being right.

- How you would know you were wrong. The specific result that would falsify it.

### The case, from the beginning

A market garden has 64 beds — 16 beds across four plots — and a 36-week season. Fixed costs are $20,000. The farmer is paid $50,000 and spends 720 hours in the field; up to four temporary workers are available at $25,000 each for 1,440 hours each. The farm cannot influence prices.

Tomatoes earn $8,800 a bed, carrots $2,094, mesclun $2,700. The bed caps are 20, 20 and 30, summing to 70 against 64 beds, so all three cannot be maxed.

Labor compounds. Each additional bed of a crop raises the labor every bed of that crop needs — 10 percent per bed for tomatoes, 2.5 percent for carrots, 1.25 percent for mesclun. The crop that earns the most per bed also gets expensive the fastest, and the question is where those two things cross. Pick a mix, say why, and say what result would tell you it was wrong.

### The order I would work in, given where you are

Three stages are open and Stage 1.2 — a written specification plus an Excel model built from it — is due 6 September. That is two days.

Realistically: finish the Stage 0 items tonight, since they are mechanical and most are one line each. Write this brief tomorrow; an hour of honest thinking beats a polished page. Then start the specification, and commit the brief before you touch the model, because Stage 1.3 asks you to compare the two and the commit history is the proof of which came first.

If that is not realistic alongside everything else you have on, say so — here in this thread or by email. I would much rather agree a sequence with you now than grade a gap later, and you have already shown this week that when you sit down to a thing you finish it properly.

---

### How to work this review

Treat this PR the way an analyst treats feedback from a senior reviewer — a review is a proposal to engage with, not a checklist to rubber-stamp.

1. **Read it yourself first.** Form your own view before you change anything. Disagreeing *with a documented reason* is a legitimate, senior response.
2. **Stress-test it with an LLM.** Paste this review and your brief into your assistant and ask it to (a) explain anything you are unsure of, and (b) argue the *other side* — where might the reviewer be wrong, and what would you give up by making each change.
3. **Then write the changes yourself.** For a brief this matters more than usual: a hypothesis you did not generate cannot be honestly compared against your model in Stage 3, and that comparison is the entire point of writing the brief first.
4. **Close the loop.** Reply in this thread with what you changed and what you pushed back on, then commit and push.

*One standing rule: do not revise your hypothesis to match what your model later tells you. If the model contradicts the brief, that is a finding, not an error.*

*Your score and the per-criterion breakdown are in your Lamaku comment, not here — this repository is public.*

— Adam
