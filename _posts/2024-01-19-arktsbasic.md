---
layout: post
title: ArkTS基础语法
date: 2024-01-19 10:19 +0800
categories: [ArkUI, HarmonyOS]
tags: [鸿蒙OS开发, HarmonyOS, ArkTS]
typora-root-url: ..
---


![](/assets/images/20240116HarmonyPhoneSendFileTomacOS/harmonyOS.webp)

# 前言

本文具有强烈的个人感情色彩,如有观看不适,请尽快关闭. 本文仅作为个人学习记录使用,也欢迎在许可协议范围内转载或使用,请尊重版权并且保留原文链接,谢谢您的理解合作. 如果您觉得本站对您能有帮助,您可以使用RSS方式订阅本站,这样您将能在第一时间获取本站信息.

## 学习记录

在看过几遍鸿蒙教程视频和文档后,我觉得把容易遗忘的基础都记录下来,以备后续使用的时候随时查找.

#### 基础类型和函数方法

``` ts
let number1: number = 99 // 默认情况下 正常情况下给的数字 就是十进制的哦
let number2: number = 0b10011 // 2进制 由0b开头的
let number3: number = 0o1234567 // 8进制 由0o开头的
let number4: number = 0x6464ab // 16进制 由日x开头的

// TODO 字符串
let string1: string = 'sunyazhou'
let string2: string = "sunyazhou"
let string3:string = "你的名字是: ${string2}"

// TODO 联合类型、 布尔 真ture/假false
let objectType : string | number | boolean
objectType = true
objectType = "sunyazhou"
objectType = 635464
objectType = false

// TODO 数组
let stringArray1: Array<string> = ['AAA','BBB','CCC']; //0下标开始的
let stringArray2: string[] = ['AAA','BBB','CCC'];

// TODO 枚举
enum Color {Red, Green, Yellow};
let color: Color = Color.Red;

// TODO 元组 和swift中的元组一样,可以理解为多类型的字典,key都是字符串 value是不同的数据类型
let name1:[string, number];
name1 = [@"孙先生", 20]; //必须按照规定顺序和类型写内容

// TODO void 无返回类型型
function name(params): void {}

// Null
let str1: null = null
// undefined
let str2: undefined = undefined
```

#### 作用域范围

``` ts
@Entry
@Component
struct LearnDetail {
  @State message: string = 'Hello World';
  
  // 里面不加let,外面的成员需要加let
  number1: number = 99
  
  build() {
    Row() {
      Column() {
        Text(this.message)
          .fontSize(50)
          .fontWeight(FontWeight.Bold)
      }
      .width('100%')
    }
    .height('100%')
  }
}
```

#### 图片控件

加载 常规本地资源

``` ts
Image($r(app.media.icon))
```  

加载 网络资源

``` ts
Image("https://www.sunyazhou.com/assets/images/20240116HarmonyPhoneSendFileTomacOS/harmonyOS.webp")
```
加载 本地任何资源

``` ts
Image($rawfile("sunyazhou.png"))
```

# 总结

随时积累记录