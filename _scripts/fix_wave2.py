#!/usr/bin/env python3
"""
Wave 2 fixes for AI-translation artifacts in English posts (prose only).

Two passes:
1. EXACT: curated per-file replacements (sentence rewrites).
2. GENERIC: safe pattern transforms on prose lines only
   (skip front matter, code fences, Preface/Introduction disclaimers, tables).

Usage:
  python3 fix_wave2.py          # dry run, prints changes
  python3 fix_wave2.py --apply  # write changes
"""
import re
import sys
from pathlib import Path

POSTS = Path("/Users/sunyazhou/Documents/sunyazhou/_posts/en")
APPLY = "--apply" in sys.argv

# ---------------------------------------------------------------------------
# Pass 1: exact curated replacements
# ---------------------------------------------------------------------------
EXACT = {
    "2017-01-13-UIViewControllerCodeStandard.md": [
        ("The following is a comprehensive list of these methods, including when they are called and some details:",
         "Here's a comprehensive list of these methods, including when they're called and some details:"),
        ("The following is some example code showing how to implement",
         "Here's some example code showing how to implement"),
    ],
    "2017-02-09-HowtToDisableWebviewNSScrollViewScroll.md": [
        ("The above code is for `macOS` development.",
         "Note: the code above is for `macOS` development."),
    ],
    "2017-03-17-LearningAVFoundationAVAudioPlayer.md": [
        ("such as 0.5x, 1.0x, 2.0x, etc. 1.0 means normal speed",
         "such as 0.5x, 1.0x, or 2.0x. 1.0 means normal speed"),
        ("`[self setupNotifications];` will be explained later",
         "I'll explain `[self setupNotifications];` later"),
    ],
    "2017-03-28-LearningAVFoundationAVAudioRecorder.md": [
        ("The above roughly covers the process of wrapping `BDRecorder`.",
         "That roughly covers the process of wrapping `BDRecorder`."),
    ],
    "2017-04-20-UniqueFilenameInSystem.md": [
        ("to solve the problem of filename conflicts when creating files.",
         "to deal with filename conflicts when creating files."),
    ],
    "2017-06-16-LearningAVFoundationAVAssetBasic.md": [
        ("by identifier, media type, media characteristics, etc.",
         "by identifier, media type, or media characteristics."),
        ("including artist, performer, album, music genre, and so on.",
         "including the artist, performer, album, and genre."),
    ],
    "2017-07-13-ios11NewSkills.md": [
        ("Making everything one queue obviously doesn't fit the business requirements.",
         "Making everything one queue clearly doesn't fit the business requirements."),
    ],
    "2017-08-07-LearningAVFoundationAVAssetSenior.md": [
        ("To solve the problem of uneven key-value layouts, this protocol was created.",
         "To deal with uneven key-value layouts, this protocol was created."),
        ("it defines its own genre sets for TV, movies, audiobooks, etc.",
         "it defines its own genre sets for TV, movies, and audiobooks."),
    ],
    "2017-12-30-FinalSummary.md": [
        ("At this point, I think a country where",
         "By this point, I think a country where"),
        ("they must have gone through at least part of what I did: income, status, and so on.",
         "they must have gone through at least part of what I did: income, status, all of it."),
    ],
    "2018-01-12-AVAudioSessionCategory.md": [
        ("`plugging/unplugging headphones`, `incoming calls`, `invoking siri`, and so on happen",
         "`plugging/unplugging headphones`, `incoming calls`, or `invoking siri` happen"),
        ("Incoming calls, alarms, and so on are all categorized as general interruptions.",
         "Incoming calls, alarms, and the like are all categorized as general interruptions."),
        ("to provide the context for recording, muting, and so on.",
         "to provide the context for recording, muting, and the like."),
    ],
    "2018-03-04-LearningAVFoundationPlayingVideo.md": [
        ("`subtitle tracks`, `alternate camera angles`, and so on.",
         "`subtitle tracks`, `alternate camera angles`, and more."),
        ("observing playback progress callbacks, extracting subtitles, and so on.",
         "observing playback progress callbacks, extracting subtitles, and more."),
    ],
    "2018-03-05-ComputerGraphicsRenderingProcess.md": [
        ("The so-called screen resolution generally refers to",
         "Screen resolution generally refers to"),
        ("including coordinates, pixels, resolution, and so on.",
         "including coordinates, pixels, resolution, and the like."),
    ],
    "2018-04-02-RunLoop.md": [
        ("including recognizing `UIGesture`/handling `screen rotation`/sending to `UIWindow`, etc.",
         "including recognizing `UIGesture`/handling `screen rotation`/sending to `UIWindow`."),
        ("such as `frame`, `backgroundColor`, etc.",
         "such as `frame` and `backgroundColor`."),
        ("The principle will be explained below.",
         "More on that below."),
    ],
    "2018-05-07-AudioUnit.md": [
        ('and so on...', '.'),
        ("High Pass, Low Pass, Band Pass, Delay, Limiter, etc. are not used very often.",
         "High Pass, Low Pass, Band Pass, Delay, and Limiter are not used very often."),
    ],
    "2018-05-08-ManualControlUIViewControllerLifeCycle.md": [
        ("the early NetEase News, Toutiao, and so on.",
         "think the early NetEase News or Toutiao."),
        ("methods like `viewWillAppear`, `viewDidAppear`, etc. manually",
         "methods like `viewWillAppear` or `viewDidAppear` manually"),
        ("custom Tab switching, paged content switching, and so on.",
         "custom Tab switching, paged content switching, that kind of thing."),
    ],
    "2018-05-15-HowToCreateTopBottomRoundedCornersForViews.md": [
        ("to solve the problem of rounding different corners.",
         "to round different corners."),
    ],
    "2018-06-08-SwiftRandom.md": [
        ("The above implements a shuffle-like sorting of numbers from 1 to 20.",
         "That gives you a shuffle-like sorting of numbers from 1 to 20."),
    ],
    "2018-06-15-NSAttributeString.md": [
        ("Everyone obviously understands why the error occurs.",
         "It's obvious why the error occurs."),
    ],
    "2018-09-20-IncreasingTapAreaOfButton.md": [
        ("or whether it's visible, etc. — add those checks yourself_",
         "or whether it's visible — add those checks yourself_"),
    ],
    "2018-11-06-AwemeTopBottomScrollDemo.md": [
        ("video pause, play, stop, etc.",
         "video pause, play, stop, and the rest."),
    ],
    "2018-11-13-AllKeypathOfCALayer.md": [
        ("That's every keypath I've collected so far — for reference only.",
         "That's every keypath I've collected so far; hope it saves you some time."),
        ("Without further ado, let's show a code snippet to demonstrate the topic of this post:",
         "Without further ado, here's a code snippet demonstrating the topic of this post:"),
    ],
    "2018-12-21-AwemeTransition.md": [
        ("The dismiss transition animation set up in steps 5~7 will be explained below.",
         "I'll cover the dismiss transition animation set up in steps 5–7 below."),
    ],
    "2019-02-15-Tools.md": [
        ("the dimensions, file size, start/end points, etc.",
         "the dimensions, file size, and start/end points."),
    ],
    "2019-12-30-FinalSummary.md": [
        ("Kitchen cabinets, bedroom wooden wardrobes, etc. — the carpentry work",
         "Kitchen cabinets, bedroom wooden wardrobes, and the like — the carpentry work"),
        ("bank cards, Alipay, WeChat, work residence permit, residence permit, and so on.",
         "bank cards, Alipay, WeChat, work residence permit, residence permit — all of it."),
        ("I have a rough idea of the renovation process; here it is for your reference if you renovate later:",
         "I have a rough idea of the renovation process; here it is in case you renovate later:"),
    ],
    "2020-02-07-SunyazhouTheory.md": [
        ("someone always asks about how high the salary is working in Beijing and so on.",
         "someone always asks how much I make working in Beijing — that kind of thing."),
    ],
    "2020-03-20-NSURLProtocol.md": [
        ("In summary, NSURLProtocol is very powerful.",
         "All in all, NSURLProtocol is very powerful."),
    ],
    "2020-07-21-iOSinterviewAnswers1.md": [
        ("both store the current class's properties, ivars, methods, protocols, and so on.",
         "both store the current class's properties, ivars, methods, and protocols."),
        ("the so-called full message forwarding mechanism kicks in.",
         "the full message forwarding mechanism kicks in."),
    ],
    "2020-08-08-iOSinterviewAnswers2.md": [
        ("The above code shows the core objects for implementing associated object technology. Let's introduce the internal implementation of each core object separately.",
         "The code above shows the core objects behind associated objects. Let's walk through the internal implementation of each one."),
        ("The above code is eventually rewritten by the compiler into the following:",
         "The compiler eventually rewrites that code into:"),
    ],
    "2020-09-01-iOSinterviewAnswers4.md": [
        ('The so-called "asynchronous" here means',
         'The "asynchronous" here means'),
    ],
    "2020-09-02-iOSinterviewAnswers5.md": [
        ("we covered memory, associated objects, ARC, AutoreleasePool, weak objects, NSNotificationCenter, etc.",
         "we covered memory, associated objects, ARC, AutoreleasePool, weak objects, and NSNotificationCenter."),
    ],
    "2020-09-17-Block.md": [
        ("At this point, do you understand Block's internal implementation?",
         "So — do you understand Block's internal implementation now?"),
    ],
    "2020-09-19-GCD.md": [
        ("the synchronous task dispatched to the main thread obviously dies a tragic death — jamming the main thread beyond rescue.",
         "the synchronous task dispatched to the main thread is dead on arrival — it jams the main thread beyond rescue."),
    ],
    "2020-09-20-UIViewGraphic.md": [
        ("Also frame rate, battery, image aliasing, and so on.",
         "Also frame rate, battery, image aliasing, and the like."),
    ],
    "2020-10-16-XcodeSourceEditorNotWork.md": [
        ("so I'm recording it here.",
         "so I'm jotting it down here."),
    ],
    "2020-12-31-FinalSummary.md": [
        ("personnel arrangements, and so on.",
         "personnel arrangements — all of it."),
    ],
    "2021-01-21-TextGradient.md": [
        ("That's obviously not being straightforward.",
         "That's just not being upfront."),
    ],
    "2021-04-06-WCDBPractice.md": [
        ("the conversation list, the message list, and so on — to WCDB.",
         "the conversation list, the message list, all of it — to WCDB."),
    ],
    "2021-12-26-FinalSummary.md": [
        ("Consumption habits, attitude toward life, psychological expectations, acceptance, acknowledging my own mediocrity, and so on.",
         "Consumption habits, attitude toward life, psychological expectations, acceptance, acknowledging my own mediocrity — all of it."),
        ("algorithms are not used much in daily work.",
         "algorithms don't come up much in day-to-day work."),
        ("In summary, learning algorithms is an essential skill for programmers.",
         "The bottom line: learning algorithms is an essential skill for programmers."),
    ],
    "2022-04-06-CVPixelBufferRef.md": [
        ("`shader` compilation, `DataBuffer` loading, and so on.",
         "`shader` compilation, `DataBuffer` loading, and more."),
    ],
    "2022-04-13-YZ3DMenu.md": [
        ("Add a new window and overlay a Blur blur and container on it, along with the encapsulated dashboard menu view.",
         "Add a new window, overlay a blur effect and a container on it, along with the dashboard menu view we wrapped up."),
    ],
    "2022-07-11-ioscrashtype.md": [
        ("This is for reference only.",
         "Take it as a rough guide."),
    ],
    "2022-12-03-thesunyazhoutheoryii.md": [
        ("In summary, I hereby establish the Second Theory of Sunyazhou:",
         "All of which is to say, I hereby establish the Second Theory of Sunyazhou:"),
    ],
    "2022-12-24-FinalSummary.md": [
        ("window-function fitting, filtering, and so on.",
         "window-function fitting, filtering, and more."),
        ("or some Laplace theorems, Hilbert theorems, etc. — all rather academic",
         "or some Laplace theorems, Hilbert theorems, and the like — all rather academic"),
        ('is far more impressive than Wang Jianlin\'s "small goal".',
         'beats Wang Jianlin\'s "small goal" by a mile.'),
    ],
    "2023-02-01-swift-defer.md": [
        ("The above example uses a defer statement",
         "The example above uses a defer statement"),
    ],
    "2023-03-06-safecast.md": [
        ("Usage is as follows",
         "Usage looks like this:"),
    ],
    "2023-03-22-podxcassets.md": [
        ("The above clearly doesn't meet our needs.",
         "That clearly doesn't meet our needs."),
        ("At this point we need to do a few things:",
         "Now we need to do a few things:"),
    ],
    "2023-04-26-cocoapodsuserguide.md": [
        ("`Bundler`, `RubyGems`, and so on.",
         "`Bundler`, `RubyGems`, and more."),
        ("which build settings to apply, and so on.",
         "which build settings to apply."),
    ],
    "2023-08-04-ios17widget.md": [
        ("In actual development, you need to implement your own AppIntent object:",
         "In practice, you need to implement your own AppIntent object:"),
    ],
    "2023-09-03-learnswiftuichapter4.md": [
        ("At this point, we need to modify the following code in the project:",
         "Now we need to modify this code in the project:"),
        ("The above code all uses @AppStorage to store basic data types.",
         "All the code above uses @AppStorage to store basic data types."),
    ],
    "2023-09-09-learnswiftuichapter5.md": [
        ("rather than me recording it here, it's better if you watch",
         "rather than me writing it all out here, you're better off watching"),
    ],
    "2023-10-31-sqlstandard.md": [
        ("And so on.",
         "You get the idea."),
    ],
    "2023-12-31-FinalSummary.md": [
        ("computer vision, and medical image processing quickly — and so on.",
         "computer vision, and medical image processing quickly."),
        ("we lack the knowledge to solve the problem of being restricted by poverty.",
         "we lack the knowledge to break out of the restrictions poverty imposes."),
        ("to solve the problem of financial freedom in the future.",
         "to work toward financial freedom down the road."),
        ("There's always an endless pile of courses, books, articles, tutorials, and so on to learn.",
         "There's always an endless pile of courses, books, articles, and tutorials to learn."),
        ("To solve the problem of my pockets looking terrible, bulging and anything but elegant from carrying various things every time I went out,",
         "To fix my pockets — which looked terrible, bulging and anything but elegant from all the stuff I carried every time I went out —"),
    ],
    "2024-01-16-HarmonyPhoneSendFileTomacOS.md": [
        ("At this point, open a new terminal",
         "Now open a new terminal"),
    ],
    "2024-01-19-arktsbasic.md": [
        ("Obviously these decorators use a unified identifier and consistent types. According to the documentation, the details are as follows:",
         "As you can see, these decorators use a unified identifier and consistent types. Here are the details from the documentation:"),
    ],
    "2024-02-21-MotionShake.md": [
        ("We'll write an MTCMMotionTool class to encapsulate the accelerometer sensor implementation",
         "We'll write an MTCMMotionTool class to wrap up the accelerometer sensor implementation"),
    ],
    "2024-03-22-masonryrelayoutviews.md": [
        ("Based on the background above, the problems we need to solve are as follows",
         "Given the background above, here are the problems we need to solve:"),
    ],
    "2024-07-31-uiapplicationsignificanttimechangenotification.md": [
        ("such as data backup, refreshing the user interface, and so on.",
         "such as data backup or refreshing the user interface."),
    ],
    "2024-08-11-docatchinswift.md": [
        ("so I'm recording it here.",
         "so I'm writing it down here."),
    ],
    "2024-08-22-multiblockembedded.md": [
        ("are used to solve the problem of retain cycles.",
         "are used to break retain cycles."),
        ("The following is an example showing how to use",
         "Here's an example showing how to use"),
    ],
    "2024-11-06-coretextcalculatedheight.md": [
        ("The following is an Objective-C code example that uses CoreText to draw text and calculate its height:",
         "Here's an Objective-C example that uses CoreText to draw text and calculate its height:"),
    ],
    "2024-12-31-FinalSummary.md": [
        ("At this point, work is no longer a question of stability",
         "By now, work is no longer a question of stability"),
        ("the [Phong lighting model](https://www.cs.utexas.edu/~bajaj/graphics2012/cs354/lectures/lect14.pdf) paper, the Fresnel lighting model, and so on.",
         "the [Phong lighting model](https://www.cs.utexas.edu/~bajaj/graphics2012/cs354/lectures/lect14.pdf) paper, the Fresnel lighting model, and more."),
        ("What I want to say is: whatever the curve,",
         "Here's what I'd say: whatever the curve,"),
    ],
    "2025-05-11-MemoryAlignmentAlgorithm.md": [
        ("It is quite interesting, so I am recording it here.",
         "It's quite interesting, so I'm writing it down here."),
    ],
    "2025-10-20-interpolating-points-in-ios-with-uibezierpath.md": [
        ("corresponds to P1, and so on.",
         "corresponds to P1, and so on for the remaining points."),
        ("In addition to the category, I have also created a small iOS application that supports adding points and fitting them with either method, and also allows changing the alpha value of the Catmull-Rom curve. The application allows users to dynamically adjust the values and see their effects.",
         "Alongside the category, I've also built a small iOS application that supports adding points, fitting them with either method, and changing the alpha value of the Catmull-Rom curve. You can tweak the values dynamically and see the effects right away."),
    ],
    "2025-11-17-swiftaiagent.md": [
        ("Even more impressive! The agent:",
         "Even better — the agent:"),
    ],
    "2025-12-31-finalsummary.md": [
        ('from the perspective of a "social scrap" like myself',
         'through the eyes of a "social scrap" like myself'),
        ("Finally, what I want to say is: this year,",
         "One last thing: this year,"),
        ("operations on determinants, vectors, matrices, etc.",
         "operations on determinants, vectors, and matrices."),
    ],
    "2026-01-23-audiometadata.md": [
        ("As follows:", "Here's the output:"),
        ("The .m file is as follows:", "Here's the .m file:"),
    ],
    "2026-03-16-magicalparticleeffectswithswiftuicanvas.md": [
        ("shapes, images, and so on.",
         "shapes, images, and more."),
    ],
    "2026-07-03-crossplatformdesktopframeworkcomparison.md": [
        ("The following is a quantitative comparison from a pure AI Agent development perspective.",
         "Here's a quantitative comparison from a pure AI Agent development perspective."),
    ],
    # --- manual flags from generic pass ---
    "2017-10-16-UIViewRendering.md": [
        (", the calculation formula is as follows:", ". The formula is:"),
    ],
    "2020-07-21-iOSinterviewAnswers1.md": [
        ("If obtained via the `class_copyIvarList()` function, the output is as follows:",
         "If you go through the `class_copyIvarList()` function, the output looks like this:"),
        ("If obtained via the `class_copyPropertyList()` function, the output is as follows:",
         "If you go through the `class_copyPropertyList()` function, the output looks like this:"),
    ],
    "2020-09-17-Block.md": [
        ("Block's internal implementation is as follows:",
         "Here's Block's internal implementation:"),
    ],
    "2023-03-22-podxcassets.md": [
        ("When using it, the code is as follows:",
         "Here's the code for using it:"),
    ],
    "2024-01-19-arktsbasic.md": [
        ("When we start the preview, the lifecycle functions are as follows:",
         "When we start the preview, the lifecycle functions run in this order:"),
        ("Sample code using @Extend is as follows:",
         "Here's some sample code using @Extend:"),
    ],
}

# AudioUnit "uncle voice" line — quotes may be curly; handle separately with a regex-free fallback
AUDIOUNIT_FALLBACK = [
    ('It is used to implement effects like "uncle voice", "KTV", "monitor return" and so on...',
     'It is used to implement effects like "uncle voice", "KTV", and "monitor return".'),
    ('It is used to implement effects like \u201cuncle voice\u201d, \u201cKTV\u201d, \u201cmonitor return\u201d and so on...',
     'It is used to implement effects like \u201cuncle voice\u201d, \u201cKTV\u201d, and \u201cmonitor return\u201d.'),
]

# ---------------------------------------------------------------------------
# Pass 2: generic transforms (prose lines only)
# ---------------------------------------------------------------------------
LOWER_WORDS = {"the", "a", "an", "this", "that", "these", "those", "it", "its", "my", "our", "their"}

ASFOLLOWS_RE = re.compile(
    r'^(?P<pre>(?:[*>-]|\d+\.)?\s*)(?P<sent>[A-Za-z][^.!?]{2,140}?) (?P<verb>is|are) as follows(?P<punct>:|\.)?\s*$'
)
FOLLOWING_IS_RE = re.compile(r'^(?P<pre>(?:[*>-]|\d+\.)?\s*)The following is (?P<rest>a|an|the|some|my|one)\b')


def transform_generic(line):
    """Return (new_line, note) or (line, None)."""
    m = ASFOLLOWS_RE.match(line)
    if m:
        sent = m.group("sent")
        first_word = sent.split(" ", 1)[0]
        if first_word.lower() in LOWER_WORDS:
            lowered = first_word.lower() + sent[len(first_word):]
            verb = m.group("verb")
            punct = m.group("punct") or ":"
            lead = "Here's" if verb == "is" else "Here are"
            return f'{m.group("pre")}{lead} {lowered}{punct}', "as-follows"
        return line, f"MANUAL as-follows: {sent[:60]}"
    m = FOLLOWING_IS_RE.match(line)
    if m:
        return f'{m.group("pre")}Here\'s {m.group("rest")}{line[m.end():]}', "following-is"
    return line, None


def prose_mask(lines):
    """Boolean list: True = prose line eligible for generic transforms."""
    mask = []
    in_fm = False
    in_code = False
    in_disclaimer = False
    for i, line in enumerate(lines):
        s = line.strip()
        if i == 0 and s == "---":
            in_fm = True
            mask.append(False)
            continue
        if in_fm:
            mask.append(False)
            if s == "---":
                in_fm = False
            continue
        if s.startswith("```"):
            in_code = not in_code
            mask.append(False)
            continue
        if in_code:
            mask.append(False)
            continue
        if re.match(r'^#{1,3}\s+(Preface|Introduction)\s*$', s):
            in_disclaimer = True
            mask.append(False)
            continue
        if in_disclaimer:
            if s.startswith("#"):
                in_disclaimer = False
                mask.append(True)
            else:
                mask.append(False)
            continue
        mask.append(True)
    return mask


def main():
    log = []
    exact_ok = exact_miss = 0
    generic_count = manual_flags = 0

    all_files = {fp.name: fp for fp in POSTS.glob("*.md")}

    # --- Pass 1: exact ---
    for fname, pairs in EXACT.items():
        if fname == "2018-05-07-AudioUnit.md":
            pairs = AUDIOUNIT_FALLBACK
        fp = all_files.get(fname)
        if not fp:
            log.append(f"[MISSING FILE] {fname}")
            exact_miss += len(pairs)
            continue
        text = fp.read_text()
        for old, new in pairs:
            if old in text:
                text = text.replace(old, new, 1)
                exact_ok += 1
                log.append(f"[EXACT] {fname}: {old[:80]}")
            else:
                exact_miss += 1
                log.append(f"[NOT FOUND] {fname}: {old[:100]}")
        if APPLY:
            fp.write_text(text)

    # --- Pass 2: generic ---
    for fname in sorted(all_files):
        fp = all_files[fname]
        lines = fp.read_text().split("\n")
        mask = prose_mask(lines)
        changed = False
        for i, line in enumerate(lines):
            if not mask[i] or not line.strip():
                continue
            # skip table rows and images
            s = line.lstrip()
            if s.startswith("|") or s.startswith("!["):
                continue
            new_line, note = transform_generic(line)
            if note and note.startswith("MANUAL"):
                manual_flags += 1
                log.append(f"[{note}] {fname} L{i+1}: {line.strip()[:120]}")
            elif new_line != line:
                generic_count += 1
                changed = True
                lines[i] = new_line
                log.append(f"[GENERIC] {fname} L{i+1}:\n    - {line.strip()[:130]}\n    + {new_line.strip()[:130]}")
        if changed and APPLY:
            fp.write_text("\n".join(lines))

    mode = "APPLIED" if APPLY else "DRY RUN"
    print(f"=== {mode} ===")
    print(f"exact applied: {exact_ok}, not found: {exact_miss}")
    print(f"generic changes: {generic_count}, manual flags: {manual_flags}")
    with open("/tmp/fix_wave2_log.txt", "w") as f:
        f.write("\n".join(log))
    print("log -> /tmp/fix_wave2_log.txt")


if __name__ == "__main__":
    main()
