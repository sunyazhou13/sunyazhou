---
layout: post
title: The Smoothstep Function
date: 2024-05-15 01:42 +0000
categories: [iOS, Swift]
tags: [iOS, macOS, Objective-C, Swift]
typora-root-url: ..
---

# Preface

This article is highly personal in tone. If you find it uncomfortable to read, please close it as soon as possible. This article is only a personal learning record. Reposts and sharing are welcome within the scope of the license agreement. Please respect the copyright and keep the original link. Thank you for your understanding and cooperation. If you find this site helpful, you can subscribe via RSS. Thanks for your support!

# How do you control a value within a certain range so that it never exceeds the upper or lower bounds of the range?

## In development, we often compute range-bounded values, like this:

``` c
float a = 某个输入值
float maxValue = 1;
//check  0 < a < the limit, assuming maxValue = 1

if (a <= 0) {
	a = 0;
} else if (a >= maxValue) {
	a = maxValue	
}

return a;

```

Obviously, this is the kind of code with zero technical content I wrote when I first learned C.

## The way I write it after years of working

``` c
//Include the standard library header; the import statement is omitted here...

float a = 某个输入值
float maxValue = 1;
//Elegance never goes out of style
float a = min(max(0, a), maxValue); // 0 <= a <= 1
return a;
```

This style gets it done in one line and looks much more impressive, clamping the value within the min and max range.

I even asked all the technical guys at my previous company about this question. My question was:

**Is there a function that combines min + max to clamp a value within a certain range?**

Most people weren't sure. Damn.

## smoothstep() — the Hermite smooth interpolation function

However, years later, I realized I wasn't that elegant either. There are many functions in the standard library that you need to improve your awareness of to know what they do.

While reading `Metal by Tutorials`, a fragment shader snippet caught my eye.

``` txt
“smoothstep

smoothstep(edge0, edge1, x) returns a smooth Hermite interpolation between 0 and 1.


Note: edge1 must be greater than edge0, and x should be edge0 <= x <= edge1.”

摘录来自
Metal by Tutorials
此材料可能受版权保护。
```

Here's the fragment shader code:

``` c
float color = smoothstep(0, params.width, in.position.x);
return float4(color, color, color, 1);

```

Yes — after all these years, this function I've been using is actually called a `smoothstep function`.

# Summary

Obviously, the next step is: define a global inline function wrapping smoothstep().

``` c
inline xx_smoothstep(T minEdge, T maxEdge, value) {
	return smoothstep(minEdge, maxEdge, value); 
}

```

This approach solves all range-value problems in engineering. It turns out that the technology I've been pursuing all these years comes down to a rise in awareness.
