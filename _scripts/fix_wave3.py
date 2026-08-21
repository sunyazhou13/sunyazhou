#!/usr/bin/env python3
"""Wave 3: fix mid-line "X is/are as follows:" remnants + replacements lost to
the wave-2 dict-key collision bug. Exact substring replacements, prose-only impact.

Usage: python3 fix_wave3.py [--apply]
"""
import sys
from pathlib import Path

POSTS = Path("/Users/sunyazhou/Documents/sunyazhou/_posts/en")
APPLY = "--apply" in sys.argv

# (file, old, new)  — replace ALL occurrences within the file unless noted
FIXES = [
    # --- replacements lost in wave 2 (dict duplicate-key bug) ---
    ("2020-07-21-iOSinterviewAnswers1.md",
     "both store the current class's properties, ivars, methods, protocols, and so on.",
     "both store the current class's properties, ivars, methods, and protocols."),
    ("2020-07-21-iOSinterviewAnswers1.md",
     "the so-called full message forwarding mechanism kicks in.",
     "the full message forwarding mechanism kicks in."),
    ("2020-09-17-Block.md",
     "At this point, do you understand Block's internal implementation?",
     "So — do you understand Block's internal implementation now?"),
    ("2023-03-22-podxcassets.md",
     "The above clearly doesn't meet our needs.",
     "That clearly doesn't meet our needs."),
    ("2023-03-22-podxcassets.md",
     "The above clearly doesn\u2019t meet our needs.",
     "That clearly doesn\u2019t meet our needs."),
    ("2023-03-22-podxcassets.md",
     "At this point we need to do a few things:",
     "Now we need to do a few things:"),
    ("2024-01-19-arktsbasic.md",
     "Obviously these decorators use a unified identifier and consistent types. According to the documentation, the details are as follows:",
     "As you can see, these decorators use a unified identifier and consistent types. Here are the details from the documentation:"),
    ("2018-05-07-AudioUnit.md",
     "High Pass, Low Pass, Band Pass, Delay, Limiter, etc. are not used very often.",
     "High Pass, Low Pass, Band Pass, Delay, and Limiter are not used very often."),
    # --- mid-line "as follows" remnants ---
    ("2017-02-18-ScanBoundsTracking.md",
     "*The core code is as follows*, using",
     "*Here's the core code*, using"),
    ("2017-03-11-LearningAVFoundationAVSpeechSynthesizer.md",
     "The delegate methods of `AVSpeechSynthesizer` are as follows — mainly for monitoring speech playback status:",
     "The delegate methods of `AVSpeechSynthesizer` are listed below — they mainly monitor speech playback status:"),
    ("2017-06-16-LearningAVFoundationAVAssetBasic.md",
     "The specific contents of this chapter are as follows:",
     "Here's what this chapter covers:"),
    ("2017-06-16-LearningAVFoundationAVAssetBasic.md",
     "_**`AVAsset.tracks`**_ is as follows",
     "Here's _**`AVAsset.tracks`**_:"),
    ("2017-06-26-RsaUniversalCrossPlatformiOSAndroidPhp.md",
     "Use Java's Cipher class to implement the encryption/decryption class. The code is as follows:",
     "Use Java's Cipher class to implement the encryption/decryption class. Here's the code:"),
    ("2017-06-26-RsaUniversalCrossPlatformiOSAndroidPhp.md",
     "use the openssl API to implement RSA encryption and decryption. The code is as follows:",
     "use the openssl API to implement RSA encryption and decryption. Here's the code:"),
    ("2017-12-15-CellAddKVO.md",
     "Recently I ran into a problem in development, as follows:",
     "Recently I ran into a problem in development:"),
    ("2017-12-15-CellAddKVO.md",
     "so I organized a state machine table as follows:",
     "so I put together a state machine table:"),
    ("2017-12-30-FinalSummary.md",
     "The key events of this year are mainly as follows:",
     "Here are the key events of this year:"),
    ("2018-03-04-LearningAVFoundationPlayingVideo.md",
     "In fact, the string values contained in the array are as follows:",
     "In fact, the array's string values look like this:"),
    ("2018-03-08-WhatIsThedSYM.md",
     "If you want it in `Debug`, configure Xcode as follows:",
     "If you want it in `Debug`, configure Xcode like this:"),
    ("2018-04-02-RunLoop.md",
     "The logic inside these two functions is roughly as follows:",
     "The logic inside these two functions goes roughly like this:"),
    ("2018-04-02-RunLoop.md",
     "The observable time points are as follows:",
     "Here are the observable time points:"),
    ("2018-04-02-RunLoop.md",
     "The structures of `CFRunLoopMode` and `CFRunLoop` are roughly as follows:",
     "Here's roughly what the `CFRunLoopMode` and `CFRunLoop` structures look like:"),
    ("2018-04-02-RunLoop.md",
     "the internal logic of `RunLoop` is roughly as follows:",
     "here's roughly the internal logic of `RunLoop`:"),
    ("2018-04-02-RunLoop.md",
     "The internal code is organized as follows (if it's too long to read, you can skip it; there will be explanations later)",
     "The internal code is below (it's long, so feel free to skip it; there will be explanations later)"),
    ("2018-04-02-RunLoop.md",
     "The call stack inside this function is roughly as follows:",
     "Here's roughly the call stack inside this function:"),
    ("2018-04-02-RunLoop.md",
     "Its principle is roughly as follows:",
     "Here's roughly how it works:"),
    ("2018-05-15-HowToCreateTopBottomRoundedCornersForViews.md",
     "And write the triggered event. The complete code is as follows.",
     "And write the triggered event. Here's the complete code."),
    ("2018-06-01-Random.md",
     "The 64-bit random number generator can then be implemented as follows:",
     "You can then implement the 64-bit random number generator like this:"),
    ("2018-06-01-Random.md",
     "Usage is as follows",
     "Usage looks like this"),
    ("2018-11-06-AwemeTopBottomScrollDemo.md",
     "I won't beat around the bush — the code is as follows and it's very simple to implement.",
     "I won't beat around the bush — here's the code, and it's very simple to implement."),
    ("2019-07-26-LoadingAnimationI.md",
     "the internal code needs to update the relevant `layer`'s `frame`. The code is as follows:",
     "the internal code needs to update the relevant `layer`'s `frame`. Here's the code:"),
    ("2019-09-26-MasonryPanViewDemo.md",
     "The specific code is as follows:",
     "Here's the specific code:"),
    ("2020-07-21-iOSinterviewAnswers1.md",
     "`class_data_bits_t` is as follows:",
     "Here's `class_data_bits_t`:"),
    ("2020-07-21-iOSinterviewAnswers1.md",
     "a pointer of type objc_method, which is a struct, as follows:",
     "a pointer of type objc_method, which is a struct, shown below:"),
    ("2020-08-08-iOSinterviewAnswers2.md",
     "Its structure is as follows:",
     "Here's its structure:"),
    ("2020-08-08-iOSinterviewAnswers2.md",
     "This function's declaration in Clang is as follows:",
     "Here's this function's declaration in Clang:"),
    ("2020-08-08-iOSinterviewAnswers2.md",
     "Its definition is as follows:",
     "Here's its definition:"),
    ("2020-08-08-iOSinterviewAnswers2.md",
     "When an object is released, the basic flow is as follows:",
     "Here's the basic flow when an object is released:"),
    ("2020-08-08-iOSinterviewAnswers2.md",
     "This function's implementation is as follows:",
     "Here's this function's implementation:"),
    ("2020-09-17-Block.md",
     "Below I wrote a sample `TestClass.m` class in which the block code is as follows:",
     "Below is a sample `TestClass.m` class I wrote, with the block code shown here:"),
    ("2020-09-19-GCD.md",
     "The specifics of the priority QoS are as follows:",
     "Here are the specifics of the priority QoS:"),
    ("2020-12-05-iOSsynchronousTimeWithServer.md",
     "The science background knowledge used in this post is as follows:",
     "Here's the background knowledge used in this post:"),
    ("2022-04-06-CVPixelBufferRef.md",
     "`_textureCache` must be created in advance; the creation method is as follows:",
     "`_textureCache` must be created in advance; here's how:"),
    ("2022-07-11-ioscrashtype.md",
     "Generally speaking, the common crash types are as follows:",
     "Here are the common crash types:"),
    ("2022-07-11-iosoom.md",
     "Its characteristics can be summarized as follows:",
     "In short:"),
    ("2022-07-11-iosoom.md",
     "The specific flow is as follows:",
     "Here's the specific flow:"),
    ("2023-04-26-cocoapodsuserguide.md",
     "you can see the Gemfile as follows — it depends on several `gem`s.",
     "you can see the Gemfile below — it depends on several `gem`s."),
    ("2023-04-26-cocoapodsuserguide.md",
     "The main flow is as follows:",
     "Here's the main flow:"),
    ("2023-08-04-ios17widget.md",
     "if you don't want it, you can remove it as follows:",
     "if you don't want it, here's how to remove it:"),
    ("2024-01-16-HarmonyPhoneSendFileTomacOS.md",
     "The command format is as follows:",
     "Here's the command format:"),
    ("2024-02-21-MotionShake.md",
     "The common sensors in iOS are as follows:",
     "Here are the common sensors in iOS:"),
]


def main():
    ok = miss = 0
    by_file = {}
    for fname, old, new in FIXES:
        by_file.setdefault(fname, []).append((old, new))
    for fname, pairs in by_file.items():
        fp = POSTS / fname
        if not fp.exists():
            print(f"[MISSING FILE] {fname}")
            miss += len(pairs)
            continue
        text = fp.read_text()
        for old, new in pairs:
            n = text.count(old)
            if n == 0:
                print(f"[NOT FOUND] {fname}: {old[:90]}")
                miss += 1
            else:
                text = text.replace(old, new)
                ok += n
                if APPLY:
                    print(f"[OK x{n}] {fname}: {old[:70]}")
        if APPLY:
            fp.write_text(text)
    mode = "APPLIED" if APPLY else "DRY RUN"
    print(f"=== {mode}: {ok} replaced, {miss} not found ===")


if __name__ == "__main__":
    main()
