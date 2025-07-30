# range(∞) ツール [range_inf]
# 【動作確認 / 使用例】

import sys
import ezpip
range_inf = ezpip.load_develop("range_inf", "../", develop_flag = True)

# 二乗が10を超えるまで繰り返す
for i in range_inf:
	n = i ** 2
	if n > 10: break
	print(n)
