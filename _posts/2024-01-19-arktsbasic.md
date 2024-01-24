---
layout: post
title: ArkTS和ArkUI基础语法
date: 2024-01-19 10:19 +0800
categories: [ArkUI, HarmonyOS]
tags: [鸿蒙OS开发, HarmonyOS, ArkTS]
typora-root-url: ..
---


![](/assets/images/20240116HarmonyPhoneSendFileTomacOS/harmonyOS.webp)

# 前言

本文具有强烈的个人感情色彩,如有观看不适,请尽快关闭. 本文仅作为个人学习记录使用,也欢迎在许可协议范围内转载或使用,请尊重版权并且保留原文链接,谢谢您的理解合作. 如果您觉得本站对您能有帮助,您可以使用RSS方式订阅本站,这样您将能在第一时间获取本站信息.

## 学习记录

### DevEco Studio快捷键

| 快捷键 | 用途 | 备注 |
| ------| ------ | ------ |
| ⌘(Command) + `B` |  进入到类或者对象的定义文件中中 | 类似Xcode中的  ⌘(Command) + `→`|
| ⌘(Command) +  ⇧(Shift) + ⌫(Back) |  与上面相反,返回上一级 | 类似Xcode中的  ⌘(Command) + `←`|
| | | |
| | | |

在看过几遍鸿蒙教程视频和文档后,我觉得把容易遗忘的基础都记录下来,以备后续使用的时候随时查找.

### ArkTS基础部分

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

### ArkUI部分

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

#### 装饰器@Styles

@Styles装饰器可以将多条样式设置提炼成一个方法，直接在组件声明的位置调用。通过@Styles装饰器可以快速定义并复用自定义样式。用于快速定义并复用自定义样式.  

* 当前@Styles仅支持通用属性和通用事件。
* @Styles方法不支持参数

> 从API version 9开始，该装饰器支持在ArkTS卡片中使用。

使用全局的@Styles封装的样式  

``` ts
@Styles function globalStyles() {
  .width(150)
  .height(300)
  .backgroundColor(Color.Pink)
}
```

定义在组件内的@Styles封装的样式

``` ts
struct LearnDetail {
  @State heightValue: number = 100
  // 定义在组件内的@Styles封装的样式
  @Styles innerStyle() {
    .width(200)
    .height(this.heightValue)
    .backgroundColor(Color.Yellow)
    .onClick(() => {
      this.heightValue = 200
    })
  }

  build() {
    ...  
  }
}
```

如何使用

``` ts
@Entry
@Component
struct LearnDetail {
  @State heightValue: number = 100
  // 定义在组件内的@Styles封装的样式
  @Styles innerStyle() {
    .width(200)
    .height(this.heightValue)
    .backgroundColor(Color.Yellow)
    .onClick(() => {
      this.heightValue = 200
    })
  }

  build() {
    Row() {
      Column() {
        // 使用全局的@Styles封装的样式
        Text('sunyazhou.com')
          .globalStyles ()
          .fontSize(30)
        // 使用组件内的@Styles封装的样式
        Text('迈腾大队长')
          .innerStyle()
          .fontSize(30)
      }
      .width('100%')
    }
    .height('100%')
  }
}

@Styles function globalStyles() {
  .width(150)
  .height(300)
  .backgroundColor(Color.Pink)
}
```

以上是是如何使用 @Styles装饰器的代码, [参考官方@Styles文档](https://developer.harmonyos.com/cn/docs/documentation/doc-guides-V2/arkts-style-0000001630145729-V2)

#### @Extend装饰器: 定义扩展组件样式

装饰器使用语法

``` ts
@Extend(UIComponentName) function functionName { ... }
```

* 和@Styles不同，@Extend仅支持在全局定义，不支持在组件内部定义。

* 和@Styles不同，@Extend支持封装指定的组件的私有属性和私有事件，以及预定义相同组件的@Extend的方法。
* 和@Styles不同，@Extend装饰的方法支持参数，开发者可以在调用时传递参数，调用遵循TS方法传值调用。
* @Extend装饰的方法的参数可以为function，作为Event事件的句柄
* @Extend的参数可以为状态变量，当状态变量改变时，UI可以正常的被刷新渲染。
* @Extend可以协变调用

如下调用协变调用

``` ts
// @Extend(Text)可以支持Text的私有属性fontColor
@Extend(Text) function fancy () {
  .fontColor(Color.Red)
}
// superFancyText可以调用预定义的fancy
@Extend(Text) function superFancyText(size:number) {
    .fontSize(size)
    .fancy() //这里调用的是上方定义的@extend
}
```

使用@Extend示例代码如下:

``` ts
@Entry
@Component
struct LearnDetail {
  @State heightValue: number = 100

  build() {
    Row() {
      Column() {
        Text("sunyazhou.com").textExtend1(20, Color.Green)
        Text("迈腾大队长")
          .textExtend1(20, Color.Blue)
      }
      .width('100%')
    }
    .height('100%')
  }
}

@Extend(Text) function textStyles1() {
  .textAlign(TextAlign.Center)
  .fontStyle(FontStyle.Italic)
  .decoration({
    type: TextDecorationType.Underline
  })
}

@Extend(Text) function textExtend1(fontSize: number, fontColor: Color) {
  .fontSize(fontSize)
  .fontColor(fontColor)
  .textStyles1()
}

```

![](/assets/images/20240119ArkTSBasic/extend_example.webp)

[参考@Extend官方文档](https://developer.harmonyos.com/cn/docs/documentation/doc-guides-V2/arkts-extend-0000001580345074-V2)

#### @Prop装饰器:父子单向同步

初始化规则图示  
![](/assets/images/20240119ArkTSBasic/rules.webp)



[@Prop参考文档](https://developer.harmonyos.com/cn/docs/documentation/doc-guides-V2/arkts-prop-0000001580185150-V2)



# 总结

随时积累记录