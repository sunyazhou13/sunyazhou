---
layout: post
title: NS-OPTIONS的用法
date: 2022-09-16 17:02 +0800
categories: [iOS开发]
tags: [iOS, Objective-C]
typora-root-url: ..

---


# 前言

本文具有强烈的个人感情色彩,如有观看不适,请尽快关闭. 本文仅作为个人学习记录使用,也欢迎在许可协议范围内转载或使用,请尊重版权并且保留原文链接,谢谢您的理解合作. 如果您觉得本站对您能有帮助,您可以使用RSS方式订阅本站,这样您将能在第一时间获取本站信息.


#### 定义:

``` objc
typedef NS_OPTIONS(NSUInteger, MyOption) {
  MyOptionNone = 0, //二进制0000,十进制0
  MyOption1 = 1 << 0,//0001,1
  MyOption2 = 1 << 1,//0010,2
  MyOption3 = 1 << 2,//0100,4
  MyOption4 = 1 << 3,//1000,8
};
```


#### 使用

``` objc
//声明定义枚举变量
MyOption option = MyOption1 | MyOption2;//0001 | 0010 = 0011,3

//检查是否包含某选型
if (option & MyOption3) { //0011 & 0100 = 0000
     //包含MyOption3
} else {
     //不包含MyOption3
}

//增加选项
option = option | MyOption4;//0011 | 1000 = 1011, 11
//减少选项
option = option & (~MyOption4);//1011 & (~1000) = 1011 & 0111 = 0011, 3
```