---
layout: post
title: 使用Masonry高阶方法对子视图统一布局,
date: 2024-03-22 13:24 +0000
categories: [iOS, SwiftUI]
tags: [iOS,iPadOS,watchOS, SwiftUI]
typora-root-url: ..
---


# 前言

本文具有强烈的个人感情色彩,如有观看不适,请尽快关闭. 本文仅作为个人学习记录使用,也欢迎在许可协议范围内转载或使用,请尊重版权并且保留原文链接,谢谢您的理解合作. 如果您觉得本站对您能有帮助,您可以使用RSS方式订阅本站,这样您将能在第一时间获取本站信息.


## 背景介绍

* 视图出现时机,时序随机
* 视图顺序固定
* 低代码,功能简单实用

## 效果演示

![](/assets/images/20240322MasonryRelayoutViews/MasonryRelayout.gif)

## 实现代码


``` objc

const CGSize MTSubviewSize60_60 = CGSizeMake(60, 60);

- (void)layoutAllEntryViewsIfNeeded
{
    NSSortDescriptor *ascendingSort = [[NSSortDescriptor alloc] initWithKey:@"tag" ascending:YES];
    NSArray <UIView *> *allEntries = [[self.allEntryContainerView subviews] sortedArrayUsingDescriptors:[NSArray arrayWithObject:ascendingSort]];
    if (allEntries.count == 0) { return; }
    if (allEntries.count == 1) {
        UIView *entryView = [allEntries kw_objectAtIndex:0];
        [entryView mas_remakeConstraints:^(MASConstraintMaker *make) {
            make.size.mas_equalTo(MTSubviewSize60_60);
            make.right.equalTo(self.allEntryContainerView.mas_right).offset(-10);
            make.centerY.equalTo(self.allEntryContainerView.mas_centerY);
        }];
    } else {
        // 使用 mas_distributeViewsAlongAxis 方法对三个视图进行水平右对齐并一次排开
        [allEntries mas_remakeConstraints:^(MASConstraintMaker *make) {
            make.size.mas_equalTo(MTSubviewSize60_60);
            make.centerY.equalTo(self.allEntryContainerView.mas_centerY);
        }];
        //必须 allEntries.count >= 2 才能用下述方法, 下面间距算法 容器宽度-所用容量宽度(包含右侧间隙+每个item大小+每个item之间的间隙)
        CGFloat leadSpace = self.allEntryContainerView.width - allEntries.count * MTSubviewSize60_60.width - 10 - (allEntries.count - 1) * 10;
        [allEntries mas_distributeViewsAlongAxis:MASAxisTypeHorizontal withFixedSpacing:10 leadSpacing:leadSpace tailSpacing:10];
    }
    [UIView animateWithDuration:0.3 animations:^{
        [self.allEntryContainerView layoutIfNeeded];
    }];
}
```

# 总结

深入了解Masonry的api使用.用高阶用法实现复杂的功能.