---
layout: post
title: Picking In Metal
date: 2024-08-12 08:55 +0000
categories: [iOS, SwiftUI]
tags: [iOS, SwiftUI, Swift, Objective-C]
typora-root-url: ..
math: true
---

# Preface

This post is strongly colored by personal opinions. If it makes you uncomfortable, please close the page as soon as possible. This post is for personal learning records only. Reposting or sharing within the scope of the license agreement is welcome, but please respect the copyright and keep the original link. Thank you for your understanding and cooperation. If you find this site helpful, you can subscribe via RSS. Thanks for your support!


![](/assets/images/20240813PickingAndHitTestinginMetal/picking.avif)


# Learning Metal Recently

When I got to chapter 12, I came across a problem I had long wanted to solve but never found an answer to: how to detect a click on an element in a 3D scene. For example, when you bring a 3D scene into a phone or PC, you can tell which 3D model you clicked through a finger touch or a mouse click.

In the book Metal.by.Tutorials.4th.2023.12.pdf, I found the answer - `Object Picking`

![](/assets/images/20240813PickingAndHitTestinginMetal/Metal.by.Tutorials.4th.2023.12.avif)


``` sh
To get started with multipass rendering, you’ll create a simple render pass that adds object picking to your app. When you click a model in your scene, that model will render in a slightly different shade.
There are several ways to hit-test rendered objects. For example, you could do the math to convert the 2D touch location to a 3D ray and then perform ray intersection to see which object intersects the ray. Warren Moore describes this method in his Picking and Hit-Testing in Metal (https://bit.ly/3rlzm9b) article. Alternatively, you could render a texture where each object is rendered in a different color or object ID. Then, you calculate the texture coordinate from the screen touch location and read the texture to see which object was hit.
You’re going to store the model’s object ID into a texture in one render pass. You’ll then send the touch location to the fragment shader in the second render pass and read the texture from the first pass. If the fragment being rendered is from the selected object, you’ll render that fragment in a different color.

```

This article solved a problem I had been exploring for a long time: how to click elements in 3D space from 2D space. The core idea is a method called **3D ray and object intersection**.

The following articles solve this problem. Besides this approach, there is also one that **uses a color/object ID to distinguish which object was clicked**.

Below is a selection of articles on the picking technique 

[Picking and Hit-Testing in Metal](https://bit.ly/3rlzm9b)  
[Picking and Hit-Testing in Metal Demo](https://github.com/metal-by-example/metal-picking)

# Summary

I discussed this with a computer graphics colleague before, and he gave me some resources for learning Vulkan, which I have organized here 

``` sh
https://github.com/KhronosGroup/Vulkan-Guide
https://github.com/KhronosGroup/Khronosdotorg/blob/main/api/vulkan/resources.md

Tutorial:
https://gavinkg.github.io/ILearnVulkanFromScratch-CN/
https://vulkan-tutorial.com/
https://software.intel.com/content/www/us/en/develop/articles/api-without-secrets-introduction-to-vulkan-preface.html
https://renderdoc.org/vulkan-in-30-minutes.html
https://www.fasterthan.life/blog/2017/7/11/i-am-graphics-and-so-can-you-part-1
``` 
