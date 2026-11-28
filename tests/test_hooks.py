"""Hook tests for the stuck and unfinished-lessons hooks (no-order version) (.claude/scripts).

Runs each hook script with PowerShell (-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File
<script>), with the hook input as UTF-8 JSON on stdin. A last section runs the exact commands from
.claude/settings.json through Git Bash, as Claude Code does on Windows, including a machine without
PowerShell (Mac/Linux). Uses a fake course and a fake USERPROFILE in a temporary folder (with Hebrew in the path, like
real installs), so real learner data is never touched.

Windows only (the hooks are PowerShell). Run: python tests/test_hooks.py
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # Hebrew test names on any console

SCRIPTS = Path(__file__).resolve().parent.parent / ".claude" / "scripts"
if shutil.which("powershell.exe") is None:
    print("SKIPPED — powershell.exe not found (the hooks are Windows PowerShell)")
    sys.exit(0)


def run(script, payload, env=None):
    p = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden",
                        "-File", str(SCRIPTS / script)],
                       input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                       capture_output=True, env=env, timeout=60)
    out = p.stdout.decode("utf-8", errors="replace").strip()
    return p.returncode, (json.loads(out) if out else None)


results = []
def check(name, ok, detail=""):
    results.append(f"[{'OK  ' if ok else 'FAIL'}] {name}" + ("" if ok else f"  -> {detail}"))


# ---- detect-stuck.ps1 ----
for text, want in [("לא הבנתי את השקף על טוקנים", True), ("הקוד לא עובד, יש שגיאה", True), ("אני לא מבינה למה", True),
                   ("נתקעתי בתרגיל 2", True), ("it doesn't work", True), ("I'm stuck on the exercise", True),
                   ("continue", False), ("/learn 2.4", False), ("מה זה API?", False), ("המערכת עובדת מצוין", False)]:
    code, out = run("detect-stuck.ps1", {"hook_event_name": "UserPromptSubmit", "prompt": text})
    ctx = out["hookSpecificOutput"]["additionalContext"] if out else ""
    check(f"stuck: {text!r} -> {want}", code == 0 and (out is not None) == want and (not want or "stuck.md" in ctx), out)
code, out = run("detect-stuck.ps1", {"prompt": "לא הבנתי"})
ctx = out["hookSpecificOutput"]["additionalContext"] if out else ""
check("stuck: Hebrew round trip + factual wording (no 'read'/'follow' commands)",
      "לא הבנתי" in ctx and "read " not in ctx.lower() and "follow it" not in ctx.lower(), ctx)

# ---- check-unfinished-lessons.ps1 ----
H = "check-unfinished-lessons.ps1"
check("old hook script is gone", not (SCRIPTS / "check-lesson-order.ps1").exists())
settings = Path(SCRIPTS.parent, "settings.json").read_text(encoding="utf-8")
check("settings.json points at the new hook", H in settings and "check-lesson-order" not in settings)
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp, "טוב טק", "Tov-learn")
    lessons = root / "courses" / "demo" / "lessons"
    for mod, lesson in [("00-a", "0.1"), ("00-a", "0.2"), ("01-b", "1.1"), ("01-b", "1.2"), ("02-c", "2.1")]:
        d = lessons / mod / f"{lesson}-x"; d.mkdir(parents=True)
        (d / f"{lesson}_script.txt").write_text("Title: x", encoding="utf-8")
    (root / "courses" / "demo" / "COURSE.md").write_text(
        "| מספר | שם |\n|---|---|\n| 0.1 | a |\n| 0.2 | b |\n| 1.1 | c |\n| 1.2 | d |\n", encoding="utf-8")
    home = Path(tmp, "home"); prog = home / "skill-tutor-tutorials" / "progress"
    env = dict(os.environ, USERPROFILE=str(home))
    script = lambda l: str(next(lessons.rglob(f"{l}_script.txt")))
    read = lambda path: {"hook_event_name": "PostToolUse", "tool_name": "Read", "tool_input": {"file_path": path}, "tool_response": {}}
    note = lambda out: out["hookSpecificOutput"]["additionalContext"] if out else ""
    start = lambda l: run(H, read(script(l)), env)[1]
    new = "**Slides covered:** all 9\n**Exercises required:** yes\n"
    def put(name, text, enc="utf-8"): (prog / name).write_text(text, encoding=enc)
    def drop(name): (prog / name).unlink(missing_ok=True)
    ex = lambda req, n, extra="": f"# תרגילים — שיעור x\n**נדרשים:** {req}{extra}\n\n" + "".join(f"## תרגיל {i} — x\n---\n" for i in range(1, n + 1))

    check("no progress folder at all -> nothing", start("1.2") is None)
    prog.mkdir(parents=True)
    _, out = run(H, read(str(root / "CLAUDE.md")), env)
    check("non-script read -> nothing", out is None, out)
    check("first lesson, nothing started -> nothing", start("0.1") is None)
    check("JUMP: nothing started, open 1.2 -> nothing (any order)", start("1.2") is None)
    check("JUMP: open a lesson missing from COURSE.md (2.1) -> nothing", start("2.1") is None)

    put("lesson-1.2.md", new); put("exercises-lesson-1.2.md", ex(2, 2))
    check("1.2 complete, open 0.1 (going back) -> nothing", start("0.1") is None)

    put("lesson-0.1.md", "**Exercises required:** yes\n")
    out = start("1.1")
    check("REMIND: 0.1 started, slides not finished -> note", "0.1 (learning started, slides not finished)" in note(out), out)
    check("note doesn't list complete or not-started lessons", "1.2" not in note(out) and "0.2" not in note(out), note(out))
    check("note: any order, leave in the middle, lesson starts as usual, one-line reminder",
          "any order" in note(out) and "leave a lesson in the middle" in note(out)
          and "starts as usual" in note(out) and "one-line reminder" in note(out), note(out))
    check("note: no blocking wording", not any(w in note(out).lower() for w in ("block", "wait", "only after", "begins only")), note(out))
    check("note: no skip quiz for a started lesson",
          "skip quiz doesn't apply to a lesson whose learning already started" in note(out), note(out))
    check("note is factual (no imperative 'read'/'follow')", "read " not in note(out).lower() and "follow" not in note(out).lower(), note(out))
    check("RETURN: opening the started lesson itself (0.1) -> nothing", start("0.1") is None)

    put("lesson-0.1.md", "<!-- auto-save -->\n**שיעור:** 0.1\n<!-- /auto-save -->\n\n" + new, "utf-8-sig")
    check("BLOCK: 0.1 slides done, no exercises file (BOM + auto-save block) -> note",
          "0.1 (slides finished, no exercises started)" in note(start("2.1")))
    put("exercises-lesson-0.1.md", ex(3, 1))
    check("BLOCK: 1 of 3 exercises -> note with count", "1 of 3 exercises recorded" in note(start("2.1")))
    put("exercises-lesson-0.1.md", ex(3, 2) + "## תרגיל 3 — ג (דולג — דורש תשלום)\n**סיבה:** x\n---\n")
    check("0.1 complete incl. paid-skipped -> nothing", start("2.1") is None)
    tag = " (רק התרגילים שקשורים לנושאים שנענו לא נכון במבחן הדילוג)"
    put("exercises-lesson-0.1.md", ex(2, 1, tag))
    check("failed skip quiz, 1 of 2 related exercises -> note", "1 of 2" in note(start("2.1")))
    put("exercises-lesson-0.1.md", ex(0, 0, tag))
    check("failed skip quiz, 0 related exercises -> nothing", start("2.1") is None)
    put("exercises-lesson-0.1.md", "## תרגיל 1 — old format, no count\n")
    check("old exercises file without נדרשים -> nothing (can't tell)", start("2.1") is None)

    drop("exercises-lesson-0.1.md"); put("lesson-0.1.md", "**Skip quiz passed:** 8/10 (21-10-2026)\n")
    check("lesson skip quiz passed -> nothing", start("2.1") is None)
    put("lesson-0.1.md", "**Slides covered:** all 9\n")
    check("legacy lesson (no marker), all slides -> nothing", start("2.1") is None)
    sessions = lambda cov: ("## Sessions\n| Date | Sections Covered | Quiz Score | Notes |\n"
                            f"|------|-----------------|-----------|-------|\n| 17-06-2026 | {cov} | 8/10 | x |\n")
    put("lesson-0.1.md", sessions("All 15"))
    check("legacy quiz-format file, 'All 15' -> nothing", start("2.1") is None)
    put("lesson-0.1.md", sessions("1–5"))
    check("legacy quiz-format file, some sections -> slides not finished",
          "0.1 (learning started, slides not finished)" in note(start("2.1")))

    put("lesson-1.1.md", "**Exercises required:** yes\n")
    out = start("2.1")
    check("two started incomplete lessons -> both listed, in number order",
          "0.1 (" in note(out) and "1.1 (" in note(out) and note(out).index("0.1 (") < note(out).index("1.1 ("), note(out))
    put("module-1.md", "**Skip quiz passed:** 9/10 (21-10-2026)\n")
    out = start("2.1")
    check("module 1 passed by module skip quiz -> 1.1 not listed", "1.1" not in note(out) and "0.1 (" in note(out), note(out))
    put("module-1.md", "| 21-10-2026 | 6/10 | 1.2 | not passed |\n")
    check("module 1 quiz not passed -> 1.1 still listed", "1.1 (" in note(start("2.1")))
    put("lesson-notes.md", "x"); put("lesson-1.x.md", "x")
    check("unrelated lesson-* file names are ignored", "notes" not in note(start("2.1")) and "1.x" not in note(start("2.1")))

    code, out = run(H, {}, env)
    check("empty input -> safe exit", code == 0 and out is None, out)

# ---- check-unfinished-lessons.ps1: optional lessons (type רשות in COURSE.md) ----
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp, "טוב טק", "Tov-learn")
    lessons = root / "courses" / "demo" / "lessons"
    for mod, l in [("00-a", "0.1"), ("00-a", "0.5"), ("01-b", "1.1")]:
        d = lessons / mod / f"{l}-x"; d.mkdir(parents=True)
        (d / f"{l}_script.txt").write_text("Title: x", encoding="utf-8")
    (root / "courses" / "demo" / "COURSE.md").write_text(
        "| מספר | שם | סוג |\n|---|---|---|\n| 0.1 | a | תיאורטי |\n| 0.5 | b | רשות |\n| 1.1 | c | מעשי |\n", encoding="utf-8")
    home = Path(tmp, "home"); prog = home / "skill-tutor-tutorials" / "progress"; prog.mkdir(parents=True)
    env = dict(os.environ, USERPROFILE=str(home))
    start = lambda l: note(run(H, read(str(next(lessons.rglob(f"{l}_script.txt")))), env)[1])
    (prog / "lesson-0.5.md").write_text("**Exercises required:** yes\n", encoding="utf-8")
    check("optional: 0.5 unfinished -> no reminder", start("1.1") == "", start("1.1"))
    (prog / "lesson-0.1.md").write_text("**Exercises required:** yes\n", encoding="utf-8")
    n_ = start("1.1")
    check("optional: required 0.1 unfinished -> reminder, 0.5 not listed",
          "0.1 (learning started, slides not finished)" in n_ and "0.5" not in n_, n_)

# ---- .claude/settings.json: the exact hook commands (shell form) ----
# Claude Code runs a shell-form hook with Git Bash on Windows and sh on Mac/Linux. These run the
# commands from settings.json through Git Bash: Hebrew round trip, the "_script.txt" pre-filter, and a
# machine without PowerShell (Mac/Linux), where every hook must exit 0 silently.
REPO = SCRIPTS.parent.parent
def git_bash():
    git = shutil.which("git")
    cands = [Path(os.environ.get("ProgramFiles", r"C:\Program Files"), "Git", "bin", "bash.exe")]
    if git:
        cands += [Path(git).resolve().parent.parent / "bin" / "bash.exe", Path(git).resolve().parent.parent.parent / "bin" / "bash.exe"]
    return next((c for c in cands if c.is_file()), None)

BASH = git_bash()
if BASH is None:
    results.append("[SKIP] settings.json commands: Git Bash not found")
else:
    hooks = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]
    STUCK_CMD = hooks["UserPromptSubmit"][0]["hooks"][0]["command"]
    ORDER_CMD = next(h["hooks"][0]["command"] for h in hooks["PostToolUse"] if h.get("matcher") == "Read")
    usr_bin = BASH.parent.parent / "usr" / "bin"           # cat etc., without the Windows folders (no PowerShell)

    def sh(cmd, payload, path=None, extra=None):
        e = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO), **(extra or {}))
        if path is not None: e["PATH"] = path
        p = subprocess.run([str(BASH), "-c", cmd], input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                           capture_output=True, env=e, timeout=60)
        out = p.stdout.decode("utf-8", errors="replace").strip()
        return p.returncode, out, p.stderr.decode("utf-8", errors="replace").strip()

    code, out, _ = sh(STUCK_CMD, {"hook_event_name": "UserPromptSubmit", "prompt": "נתקעתי בתרגיל"})
    check("settings: stuck command via Git Bash, Hebrew round trip", code == 0 and "stuck.md" in out and "נתקעתי" in out, out)
    code, out, _ = sh(STUCK_CMD, {"hook_event_name": "UserPromptSubmit", "prompt": "continue"})
    check("settings: stuck command, ordinary prompt -> nothing", code == 0 and out == "", out)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp, "טוב טק", "Tov-learn"); lessons = root / "courses" / "demo" / "lessons"
        for l in ("0.1", "0.2"):
            d = lessons / "00-a" / f"{l}-x"; d.mkdir(parents=True)
            (d / f"{l}_script.txt").write_text("Title: x", encoding="utf-8")
        (root / "courses" / "demo" / "COURSE.md").write_text("| מספר | שם |\n|---|---|\n| 0.1 | a |\n| 0.2 | b |\n", encoding="utf-8")
        home = Path(tmp, "home"); (home / "skill-tutor-tutorials" / "progress").mkdir(parents=True)
        (home / "skill-tutor-tutorials" / "progress" / "lesson-0.1.md").write_text("**Exercises required:** yes\n", encoding="utf-8")
        s02 = str(lessons / "00-a" / "0.2-x" / "0.2_script.txt")
        code, out, _ = sh(ORDER_CMD, read(s02), extra={"USERPROFILE": str(home)})
        check("settings: reminder command via Git Bash, Hebrew path -> note", code == 0 and "0.1 (learning started, slides not finished)" in out, out)

        # A stand-in "powershell" that only records that it was started
        shim = Path(tmp, "shim"); shim.mkdir(); mark = Path(tmp, "started")
        (shim / "powershell").write_text(f"#!/bin/sh\ncat >/dev/null\n: > '{mark.as_posix()}'\n", encoding="utf-8", newline="\n")
        shim_path = f"{shim};{usr_bin}"
        sh(ORDER_CMD, read(str(root / "CLAUDE.md")), path=shim_path)
        check("settings: order command, non-script read -> PowerShell not started", not mark.exists())
        sh(ORDER_CMD, read(s02), path=shim_path)
        check("settings: order command, script read -> PowerShell started", mark.exists())

    # Mac/Linux: no PowerShell on PATH -> exit 0, no output, no error text
    for name, cmd, payload in [("stuck", STUCK_CMD, {"prompt": "נתקעתי"}),
                               ("order", ORDER_CMD, read("/home/x/Tov-learn/courses/c/lessons/m/0.2-x/0.2_script.txt"))]:
        code, out, err = sh(cmd, payload, path=str(usr_bin))
        check(f"settings: {name} command without PowerShell (Mac/Linux) -> silent exit 0",
              code == 0 and out == "" and err == "", (code, out, err))

print("\n".join(results))
passed = sum(r.startswith("[OK") for r in results)
failed = sum(r.startswith("[FAIL") for r in results)
print(f"\n{passed}/{passed + failed} passed" + (f", {len(results) - passed - failed} skipped" if passed + failed < len(results) else ""))
sys.exit(1 if failed else 0)
