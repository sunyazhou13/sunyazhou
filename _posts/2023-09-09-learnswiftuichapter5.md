---
layout: post
title: SwiftUI第四章学习总结
date: 2023-09-09 15:55 +0800
categories: [iOS, SwiftUI]
tags: [iOS, macOS, Objective-C, SwiftUI]
typora-root-url: ..
---


# 前言

本文具有强烈的个人感情色彩,如有观看不适,请尽快关闭. 本文仅作为个人学习记录使用,也欢迎在许可协议范围内转载或使用,请尊重版权并且保留原文链接,谢谢您的理解合作. 如果您觉得本站对您能有帮助,您可以使用RSS方式订阅本站,这样您将能在第一时间获取本站信息.


## SwiftUI课程

最近坚持学习swiftUI,周末有空把第四章都看完了,我这里说的看是动手实践+教程学习.记录一些容易遗忘的内容


### 主要内容包括

* 处理tabbar透明问题问题
*  处理单位格式化问题

### tabbar透明问题问题

用SwiftUI写完各种UI后发现 tabbar的视图被遮挡,

![](/assets/images/20230805LearnSwiftUIChapter5/before.gif)
![](/assets/images/20230805LearnSwiftUIChapter5/after.gif)

需要启动app的时候使用如下函数`applyTabbarBackground()`

``` swfit
import SwiftUI

@main
struct AppEntry: App {
    init() {
        applyTabbarBackground()
    }
    
    var body: some Scene {
        WindowGroup {
            HomeScreen()
        }
    }
    
    func applyTabbarBackground() {
        let tabbarAppearence = UITabBarAppearance()
        tabbarAppearence.configureWithTransparentBackground()
        tabbarAppearence.backgroundColor = .secondarySystemBackground.withAlphaComponent(0.3)
        tabbarAppearence.backgroundEffect = UIBlurEffect(style: .systemChromeMaterial)
        UITabBar.appearance().scrollEdgeAppearance = tabbarAppearence
    }
}
```

####  处理单位格式化问题

iOS系统提供了国家化的单位类 `Measurement `,帮我们处理 克，g, 英镑, pounds等单位的处理

``` swift
var desciption : String {
        let preferredUnit = Unit.getPreferredUnit(from: store)
        let measureMent = Measurement(value: wrappedValue, unit: unit.dimension)
        let converted = measureMent.converted(to: preferredUnit.dimension)
//        return converted.formatted(.measurement(width: .abbreviated, usage: .asProvided, numberFormatStyle: .number.precision(.fractionLength(0...1))))
        return converted.value.formatted(.number.precision(.fractionLength(0...1))) + " " + preferredUnit.localizedSymbol
    }
```

这里推荐看一下官方的WWDC20视频[Formatters: Make data human-friendly](https://developer.apple.com/videos/play/wwdc2020/10160/)

影片中介紹了能把日期、單位、數字和文字等等資料，根據使用者 Locale 進行格式化的工具


# 总结

其实第五章讲的比较多的是属性封装器的高度封装,我看篇幅实在太大,与其我在这记录一下不如大家亲自看一下[教程视频](https://www.bilibili.com/video/BV1bA411y71h/?spm_id_from=333.788&vd_source=9309f71afe97e633abeadc8407870e76),讲的比较透彻。

其次大篇讲述单元测试, 这里由于本人不太愿意写单元测试直接跳过。。。

一直跟进这门课程希望有所收获.