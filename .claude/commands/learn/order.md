# Lesson Order — Shared Rules (reference)

*Reference module, not routed. Read it when a hook note says started lessons are not complete, and whenever you suggest or start a lesson (`resume.md`, `setup.md`, `teaching.md`, `slides.md`, `quiz.md`).*

Respond in `session.language` throughout. Address the learner using `session.address`.

---

## Principle — finish what you started

**Lessons can be learned in any order.** The course order — the lesson list (`## רשימת שיעורים`) in the active course's `COURSE.md` — is the suggested order, not a requirement: the learner may choose any lesson.

But **a new lesson starts only when every lesson the learner already started is complete**. A lesson is **started** once it has a progress file `~/skill-tutor-tutorials/progress/lesson-{lesson_number}.md` (learning started, or a lesson skip quiz was taken). Lessons never started don't block anything.

A started lesson is **complete** when one of these is true:

1. **Finished** — all its slides were covered and its required exercises are done (`exercises.md`; exercises skipped under the paid-resources rule count as done). Its progress file has `**Slides covered:** all [N]`.
   - Lessons learned under the current rules get the line `**Exercises required:** yes` in their progress file when learning starts — the learner chose to learn, or failed the lesson skip quiz (`teaching.md` Step 3, `slides.md` Step 1).
   - Lessons learned before these rules have no such line. For those, covering all the slides is enough — shown by `**Slides covered:** all`, or by a row in the file's Sessions table whose "Sections Covered" says all (e.g. `All 15`, `All sections`). Their exercises aren't checked.
2. **Passed by a lesson skip quiz** — score 8+ (`teaching.md`, Step 3). Its progress file has `**Skip quiz passed:**`.
3. **Passed by a module skip quiz** — its whole module was passed (`quiz.md`, "Module Skip Quiz" — `quiz module X`). `~/skill-tutor-tutorials/progress/module-{X}.md` has `**Skip quiz passed:**`.

A started lesson whose slides aren't finished blocks a new lesson too — otherwise stopping in the middle of the slides would avoid the exercises.

Reviewing a lesson that's already complete is always allowed.

---

## When started lessons are not complete

A hook checks this whenever a lesson starts and adds a note listing the started lessons that aren't complete. When that happens, **before teaching the requested lesson**:

1. Tell the learner briefly that lessons can be learned in any order, but a started lesson is finished before a new one begins — and which started lessons aren't complete yet, and what's missing in each (slides, or how many exercises).
2. Offer to **finish them**, starting from the first one listed: continue its slides, or do its remaining exercises (following `exercises.md`). Once learning a lesson started, it's completed by its slides and required exercises — the lesson skip quiz isn't offered for it, even when only exercises remain.
3. When every started lesson is complete, start the requested lesson.

Don't start the requested lesson "just this once", even if asked; explain the rule kindly and offer to finish the started lessons. The exercises rules (`exercises.md`), including the paid-resources exception, still apply.

**Skip quizzes wait too.** A lesson skip quiz or a module skip quiz starts new lessons, so it's also offered only when every started lesson is complete. The lesson skip quiz is offered **only for a lesson that is not started**. The module skip quiz is offered only for a module **having no lesson started yet and no earlier module-quiz attempt** (one attempt only — `quiz.md`).

---

## Suggesting the next lesson

When suggesting what to learn next:

1. If a started lesson isn't complete, suggest finishing it first.
2. Otherwise, suggest the **first lesson in the course order that isn't complete**, and say the learner may choose any other lesson that isn't complete. You may also suggest related lessons for **review** (e.g. from the knowledge map).
