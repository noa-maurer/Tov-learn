# PostToolUse hook (matcher: Read): runs after Claude reads a file.
#
# Reminder of unfinished lessons (.claude/commands/learn/order.md): lessons can be learned in any order,
# and the learner may leave a lesson in the middle; nothing is blocked. When the file is a lesson script
# (X.Y_script.txt) — which Claude reads whenever a lesson starts, whatever started it (/learn X.Y, slides
# mode, resume) — check every other lesson that has a progress file, and if any isn't complete, add a
# factual note for Claude next to the read result, so it can remind the learner in one line. The lesson
# being opened is never listed: coming back to it is how it gets finished.
#
# A started lesson (it has progress/lesson-X.Y.md) is complete when:
#   - its progress file, or its module's progress/module-M.md, says "**Skip quiz passed:**"; or
#   - it was learned under the current rules (progress file has "**Exercises required:** yes", written
#     when learning starts): "Slides covered: all" and its required exercises recorded (exercises.md); or
#   - it was learned before these rules (no such line): all slides covered, shown by "Slides covered: all"
#     or by a Sessions-table row whose "Sections Covered" says all ("All 15", "All sections"). Exercises
#     aren't checked for those.
# A started lesson can only be completed by finishing it: the lesson skip quiz is offered only for
# lessons not started (order.md), so the note offers no skip quizzes.
# Optional lessons (type רשות in COURSE.md) are never listed.
# Fires every time a new lesson starts, in any session, while a started lesson isn't complete.
# It never fires at the end of a lesson (there's no Stop hook for this), so once per attempt.
# Any unexpected error -> exit 0 with no output (the read goes through as usual).

try {
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $hookInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
    $path = $hookInput.tool_input.file_path          # absolute, backslashes on Windows
    if (!$path -or $path -notmatch '(\d+\.\d+)_script\.txt$') { exit 0 }
    $lesson = $Matches[1]

    $progressDir = Join-Path $env:USERPROFILE "skill-tutor-tutorials\progress"
    if (!(Test-Path $progressDir)) { exit 0 }
    function Read-Text($file) {
        $p = Join-Path $progressDir $file
        if (Test-Path $p) { Get-Content $p -Raw -Encoding UTF8 } else { $null }
    }

    # Started lessons = lessons with a progress file, other than the one being opened, in number order
    $started = @(Get-ChildItem $progressDir -File -Filter "lesson-*.md" | ForEach-Object {
        if ($_.Name -match '^lesson-(\d+\.\d+)\.md$') { $Matches[1] } } |
        Where-Object { $_ -ne $lesson } | Sort-Object { [version]$_ } -Unique)

    # Optional lessons (type רשות in the course's COURSE.md) never get a reminder
    # courses/<course>/lessons/<module>/<X.Y-name>/X.Y_script.txt -> courses/<course>/COURSE.md
    $optional = @()
    $courseMd = Join-Path (Split-Path (Split-Path (Split-Path (Split-Path $path -Parent) -Parent) -Parent) -Parent) "COURSE.md"
    if (Test-Path $courseMd) {
        $optional = @(Get-Content $courseMd -Encoding UTF8 | ForEach-Object {
            if ($_ -match '^\|\s*(\d+\.\d+)\s*\|.*\|\s*רשות\s*\|\s*$') { $Matches[1] } })
    }

    # Older progress files (quiz.md format): a Sessions-table row whose 2nd column says all sections
    $legacyAllRow = '(?mi)^\|[^|\r\n]*\|\s*(all\b|הכל|כל )'
    $incomplete = @()
    foreach ($l in $started) {
        if ($optional -contains $l) { continue }
        $m = $l.Split('.')[0]
        $moduleText = Read-Text "module-$m.md"
        if ($moduleText -and $moduleText -match '\*\*Skip quiz passed:\*\*') { continue }
        $text = Read-Text "lesson-$l.md"
        $state = $null
        if ($text -match '\*\*Skip quiz passed:\*\*') {
            continue
        } elseif ($text -notmatch '\*\*Exercises required:\*\*\s*yes') {          # learned before the rules
            if ($text -notmatch 'Slides covered:\*\*\s*all' -and $text -notmatch $legacyAllRow) {
                $state = "learning started, slides not finished"
            }
        } elseif ($text -notmatch 'Slides covered:\*\*\s*all') {
            $state = "learning started, slides not finished"
        } else {
            $exercises = Read-Text "exercises-lesson-$l.md"
            if (!$exercises) {
                $state = "slides finished, no exercises started"
            } elseif ($exercises -match '\*\*נדרשים:\*\*\s*(\d+)') {   # a file without a count: can't tell
                $required = [int]$Matches[1]
                $recorded = ([regex]::Matches($exercises, '(?m)^## תרגיל')).Count
                if ($recorded -lt $required) { $state = "slides finished, $recorded of $required exercises recorded" }
            }
        }
        if ($state) { $incomplete += "$l ($state)" }
    }
    if ($incomplete.Count -eq 0) { exit 0 }

    $note = "Lesson $lesson is starting. Other lessons the learner already started are not complete yet: " +
            ($incomplete -join "; ") + ". Under this course's rules (.claude/commands/learn/order.md), " +
            "the learner may learn lessons in any order and leave a lesson in the middle, so lesson $lesson " +
            "starts as usual; those lessons stay in progress until their slides and required exercises are done, " +
            "and the learner gets a one-line reminder that they can go back to them. " +
            "The lesson skip quiz doesn't apply to a lesson whose learning already started."
    @{ hookSpecificOutput = @{ hookEventName = "PostToolUse"; additionalContext = $note } } |
        ConvertTo-Json -Compress -Depth 3
    exit 0
} catch {
    exit 0
}
