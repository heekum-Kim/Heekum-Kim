<!-- PR TARGET: https://github.com/heekum-Kim/Heekum-Kim | Stage 1.1 -->
# Stage 1.1 review — engagement brief

**Brief:** [`docs/briefs/perfect-competition-brief.md`](https://github.com/heekum-Kim/Heekum-Kim/blob/main/docs/briefs/perfect-competition-brief.md)

> Graded 2026-09-07 against the brief you committed on 6 September. Two passes ago this file was one byte and the stage was held rather than scored. It is a real brief now, it gets the central economics of the case right, and the two things it is missing are both quick.

| Criterion | Where it stands |
|---|---|
| Problem restated in your own voice | You do restate it, and the sentence that matters most is there and is yours: because the price is set by the market, the only decision left is the crop mix. That is the definition of a price taker written as a decision rather than as a definition, and plenty of briefs in this cohort never get there. What holds the criterion down is that the rest of the section transcribes the case tables rather than reading them — the parameters, then all three crops with their prices, hours, fertilizer and caps — in one unbroken block with no sections. The reader cannot tell where the case stops and you start. |
| Hypothesis names a specific mix | You name three whole numbers, which is what this criterion asks for: 20 carrots, 15 tomatoes, 30 mesclun. The problem is that they add to 65, and the brief says four lines earlier that there are 64 beds. Naming a mix earns most of this criterion. Naming one that breaks a constraint you yourself wrote down cannot earn all of it, because the mix is not something the farm could plant. |
| Economic mechanism | The core insight is right, it is the hardest one in the case, and you state it clearly: tomatoes earn the most per bed, but a 10% compounding labor penalty per bed works against that advantage, and at some point it wins. That is the mechanism the case is built to teach. Two things stop it short. You conclude that carrots are the most profitable crop because they use the least labor and the least fertilizer — but carrots are also the lowest-earning crop on the page at $2,094 a bed against tomatoes' $8,800, and profit is what is left after cost, so an argument made only from the cost side cannot rank them. And the derivation of the rate is off: you write 720 field hours implying about $34.72 an hour, but $50,000 divided by 720 is $69.44. The $34.72 you are using is $50,000 divided by 1,440, which is the right number reached by a sentence that does not produce it. |
| Falsifiability and process | There is no falsification section. Nothing in the brief names an outcome that would show the hypothesis was wrong, which means that as written it cannot be tested against your model — and testing it is the entire reason the brief is committed before the model is built. What this criterion does credit is process, and your process is clean: the file is at the canonical path, docs/briefs/perfect-competition-brief.md, and it was committed before anything resembling a model existed in the repository. The history proves the sequence, which is the part that cannot be reconstructed later. |

### Sixty-five beds into sixty-four

20 carrots plus 15 tomatoes plus 30 mesclun is 65, and the farm has 64 beds. Every crop is inside its own cap, so the error is not in any single number — it is that the three together ask for one bed more than exists.

Do not fix it now. The brief is committed and dated, and from here it is evidence rather than a draft. Your model will not be able to return 65 beds, so it will hand you a comparison to write about, and explaining that gap honestly is worth more in the analysis stage than a brief that was quietly corrected afterwards.

The thing to carry forward is the habit: when a mix is written down, add it up against the constraint on the same page. It takes five seconds and it is the check that catches this class of error every time.

### The missing section is the cheapest work on the page

Falsifiability is the single largest gap in this brief and it is three sentences of work. It asks one question: what would the model have to return for you to conclude your reasoning was wrong?

Your own brief already contains two of them. You predict 15 tomato beds because the compounding penalty bites — so if the model returns close to 20, the penalty is weaker than you thought, and if it returns fewer than about 8, it is far stronger. You predict carrots and mesclun run to their caps — so if the model leaves either short of its cap, something you have not accounted for is pushing them away.

Write those down with numbers in them and the section is finished. A threshold with a number is testable; "if the model disagrees" is not.

### Your repository is still mostly empty, and that is the other half of your grade

Two of the fourteen canonical paths hold a file with anything in it. AGENTS.md, prompt-log.md and .gitignore all exist and are all empty, and analysis/, analysis/figures/, capabilities/, data/, docs/ and docs/decisions/ do not exist at all.

That structure is graded in its own right at Stage 0, and it is also the thing the next stage needs in order to have somewhere to live. Stage 1.2 wants capabilities/marginal-analysis/spec.md and capabilities/marginal-analysis/model.xlsx, and neither the capabilities folder nor the one beneath it exists yet.

Ten one-line README files would move seven of those paths from missing to present. AGENTS.md is the one worth real thought rather than a line: how you want an assistant to explain things, what it may draft for you, what it may not, and what must never be pasted into a model.

### One practical thing

You still have not submitted this repository through the assignment in Lamaku for any stage — the URL reached me directly. Please submit it, so the record shows what you have done.

Stage 1.2 is the specification and the Excel workbook, and it is the largest single piece of the case. If the remaining work is not realistic in the time left, say so in this thread and we will work out an order rather than letting it drift.

---

### How to work this review

Treat this PR the way an analyst treats feedback from a senior reviewer — a review is a proposal to engage with, not a checklist to rubber-stamp.

1. **Read it yourself first.** Form your own view before you change anything. Disagreeing *with a documented reason* is a legitimate, senior response.
2. **Stress-test it with an LLM.** Paste this review and your brief into your assistant and ask it to (a) explain anything you are unsure of, and (b) argue the *other side* — where might the reviewer be wrong, and what would you give up by making each change.
3. **Then write the changes yourself.** For a brief, this matters more than usual: a hypothesis you did not generate cannot be honestly compared against your model in Stage 3, and that comparison is the entire point of writing the brief first.
4. **Close the loop.** Reply in this thread with what you changed and what you pushed back on, then commit and push.

*One standing rule for this stage: do not revise your hypothesis to match what your model later tells you. If the model contradicts the brief, that is a finding, not an error — Stage 3 asks you to explain the gap, and a brief quietly edited to be right afterwards has nothing left to explain.*

*Your score and the per-criterion breakdown are in your Lamaku comment, not here — this repository is public.*

— Adam
