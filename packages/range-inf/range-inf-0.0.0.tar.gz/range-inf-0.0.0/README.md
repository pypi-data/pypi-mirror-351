English description follows Japanese.

```python
for i in range(∞):
	...
```
のようなことができるツール

## 使い方
```python
import range_inf

# 2乗が10を超えるまで繰り返す
for i in range_inf:
	n = i ** 2
	if n > 10: break
	print(n)	# -> 0\n1\n4\n9
```

## ツール概要
- range(10)と同じような使用感で、無限に続くrange(無限大)を使いたいときのツール
- 上記の使用例のようにfor文等で使ってください
- いつ終了すべきかが予め分からないループを、whileではなくforで使えるため、簡単にインデックスが取得出来ます

## 詳細
- itertoolsに同様のものがありますが、最短の記述でサクッと使いたいときに便利です
- ネストして2重で使ったり、breakで中断した後再度使用しても、通常のgenerator等と異なり途中から始まることなく、リセットされて最初から始まるように作られています

---

## Usage
```python
import range_inf

# Repeat until the square exceeds 10
for i in range_inf:
	n = i ** 2
	if n > 10: break
	print(n)	# -> 0\n1\n4\n9
```

## Overview
* A tool that provides an infinite `range(∞)` with the same feel as `range(10)`
* Use it in `for` loops as shown above
* Ideal for loops where the exit condition isn't known in advance — allows index tracking using a `for` loop instead of `while`

## Details
* While `itertools` provides similar functionality, this tool is convenient when you want the shortest and cleanest syntax
* It can be nested or reused after a `break`, and unlike typical generators, it always resets and starts from the beginning
