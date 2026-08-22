#!/usr/bin/env python3
"""Fix dead self-domain links (old Hexo-era URLs) across posts."""
import os

POSTS = "/Users/sunyazhou/Documents/sunyazhou/_posts"

# old -> new (all new URLs verified 200 on live site)
MAPPING = {
    "http://sunyazhou.com/2017/03/17/Learning-AV-Foundation-AVAudioPlayer/":
        "https://www.sunyazhou.com/2017/03/LearningAVFoundationAVAudioPlayer/",
    "https://www.sunyazhou.com/2017/03/17/Learning-AV-Foundation-AVAudioPlayer/":
        "https://www.sunyazhou.com/2017/03/LearningAVFoundationAVAudioPlayer/",
    "http://www.sunyazhou.com/2017/06/20/enable-static-analyer/":
        "https://www.sunyazhou.com/2017/06/EnableStaticAnalyer/",
    "https://www.sunyazhou.com/2017/09/29/20170929MarkdownTable/":
        "https://www.sunyazhou.com/2017/09/MarkdownTable/",
    "https://www.sunyazhou.com/2017/10/16/20171016UIViewRendering/":
        "https://www.sunyazhou.com/2017/10/UIViewRendering/",
    "https://www.sunyazhou.com/2017/10/25/20171025markdownSkill/":
        "https://www.sunyazhou.com/2017/10/MarkdownSkill/",
    "https://www.sunyazhou.com/2020/08/08/20200808iOSinterviewAnswers/":
        "https://www.sunyazhou.com/2020/08/iOSinterviewAnswers2/",
    "https://www.sunyazhou.com/tags/iOS%E9%9D%A2%E8%AF%95%E9%A2%98/":
        "https://www.sunyazhou.com/2020/07/iOSinterviewAnswers1/",
    "https://www.sunyazhou.com/images/logo2.jpg":
        "https://www.sunyazhou.com/assets/images/20181108AwemeAlbumAnimation/album1.avif",
    "http://localhost:4000/2017/03/20/Access-privacy-sensitive-data-private-access-permission/":
        "https://www.sunyazhou.com/2017/03/AccessPrivacySensitive/",
    "http://localhost:4000/2017/02/10/build-hexo-blog-Tutorial/":
        "https://www.sunyazhou.com/2017/02/BuildHexoBlogTutorial/",
}


def main():
    total = 0
    for root, dirs, files in os.walk(POSTS):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding='utf-8') as f:
                content = f.read()
            orig = content
            count = 0
            for old, new in MAPPING.items():
                n = content.count(old)
                if n:
                    content = content.replace(old, new)
                    count += n
                    print(f"  {os.path.relpath(path, POSTS)}: {n}x {old[:60]}...")
            if content != orig:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                total += count
    print(f"\nTotal replacements: {total}")


if __name__ == '__main__':
    main()
