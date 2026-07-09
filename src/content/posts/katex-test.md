---
title: KaTeX 數學公式測試
published: 2026-07-09
description: 驗證網站的數學公式渲染——行內、區塊、矩陣與對齊環境。
tags: [測試, KaTeX]
category: 網站建置
lang: zh_TW
---

這篇是網站 KaTeX 支援的驗證文（M1 Issue #3），順便記錄幾個資結課會用到的式子。

## 行內公式

質能等價 $E = mc^2$，歐拉恆等式 $e^{i\pi} + 1 = 0$，等比級數和 $\sum_{i=0}^{n} 2^i = 2^{n+1} - 1$。

## 區塊公式

一元二次方程式的解：

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

合併排序的時間複雜度遞迴式與其解：

$$
T(n) = 2\,T\!\left(\frac{n}{2}\right) + O(n) \implies T(n) = O(n \log n)
$$

高斯積分：

$$
\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}
$$

## 矩陣

$$
\begin{pmatrix} a & b \\ c & d \end{pmatrix}
\begin{pmatrix} x \\ y \end{pmatrix}
=
\begin{pmatrix} ax + by \\ cx + dy \end{pmatrix}
$$

## 對齊環境

$$
\begin{aligned}
(a+b)^2 &= (a+b)(a+b) \\
        &= a^2 + ab + ba + b^2 \\
        &= a^2 + 2ab + b^2
\end{aligned}
$$

以上全部正常顯示的話，Issue #3 收工。
