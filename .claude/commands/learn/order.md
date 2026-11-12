# Lesson Order — Shared Rules (reference)

*Reference module, not routed. Read it when a hook note says started lessons are not complete, and whenever you suggest or start a lesson (`resume.md`, `setup.md`, `teaching.md`, `slides.md`, `quiz.md`).*

Respond in `session.language` throughout. Address the learner using `session.address`.

---

## Principle — free choice, honest completion

**Lessons can be learned in any order, and the learner may leave a lesson in the middle.** The course order — the lesson list (`## רשימת שיעורים`) in the active course's `COURSE.md` — is the suggested order, not a requirement. A learner who finds a lesson too hard right now, or not what they need, may switch to another lesson and come back later. Nothing blocks a lesson from starting.

What keeps learning honest is **completion**: a lesson counts as complete only when one of these is true — never just because it was started or because the learner moved on.

A lesson is **started** once it has a progress file `~/skill-tutor-tutorials/progress/lesson-{lesson_number}.md` (learning started, or a lesson skip quiz was taken). A lesson is **complete** when:

1. **Finished** — all its slides were covered and its required exercises are done (`exercises.md`; exercises skipped under the paid-resources rule count as done). Its progress file has `**Slides covered:** all [N]`.
   - Lessons learned under the current rules get the line `**Exercises required:** yes` in their progress file when learning starts — the learner chose to learn, or failed the lesson skip quiz (`teaching.md` Step 3, `slides.md` Step 1).
   - Lessons learned before these rules have no such line. For those, covering all the slides is enough — shown by `**Slides covered:** all`, or by a row in the file's Sessions table whose "Sections Covered" says all (e.g. `All 15`, `All sections`). Their exercises aren't checked.
2. **Passed by a lesson skip quiz** — score 8+ (`teaching.md`, Step 3). Its progress file has `**Skip quiz passed:**`.
3. **Passed by a module skip quiz** — its whole module was passed (`quiz.md`, "Module Skip Quiz" — `quiz module X`). `~/skill-tutor-tutorials/progress/module-{X}.md` has `**Skip quiz passed:**`.

A started lesson that isn't complete is **in progress** — in `/learn status`, in suggestions, and anywhere else lessons are counted (`status.md`). Never call it complete, finished or passed.

Claude never skips a lesson's exercises on its own: within a lesson, the exercises always come after the slides (`exercises.md`). Leaving a lesson is the learner's choice, and the lesson then simply stays in progress.

---

## When started lessons are not complete — a one-line reminder

A hook checks this whenever a lesson starts and adds a note listing the other started lessons that aren't complete. When that happens:

1. Before teaching the requested lesson, mention it to the learner in **one short line**: which lessons aren't complete yet — the lessons **listed in the note**, never the lesson being opened — what's missing in each (slides, or how many exercises), and that they can come back to them whenever they like. Template: "שיעור [מספר מההערה] עדיין לא הושלם ([מה חסר]), אפשר לחזור אליו מתי שתרצי." Write it right the first time; don't correct yourself in the text.
2. Then start the requested lesson as usual. **Don't ask** whether to go back first, don't explain rules, and don't make the reminder longer than one line. If the learner says they'd rather go back, continue that lesson instead.

The reminder appears every time a new lesson starts while another started lesson isn't complete.

**Skip quizzes are only for lessons not started.** The lesson skip quiz is offered **only for a lesson that is not started**: once learning a lesson started, it's completed by its slides and required exercises — otherwise leaving a hard lesson and quizzing on it would skip its exercises. The module skip quiz is offered only for a module **having no lesson started yet and no earlier module-quiz attempt** (one attempt only — `quiz.md`).

---

## Suggesting the next lesson

When suggesting what to learn next:

1. If a started lesson isn't complete, suggest going back to it first (say what's missing: slides, or how many exercises), and say the learner may choose another lesson instead.
2. Otherwise, suggest the **first lesson in the course order that isn't complete**, and say the learner may choose any other lesson that isn't complete. You may also suggest related lessons for **review** (e.g. from the knowledge map).
