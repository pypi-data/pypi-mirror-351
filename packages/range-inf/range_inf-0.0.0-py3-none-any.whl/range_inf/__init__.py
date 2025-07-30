# range(∞) ツール [range_inf]

import sys

# range_infオブジェクトのクラス
class RangeInf:
	# 初期化処理
	def __init__(self):
		pass
	# for文脈での利用時
	def __iter__(self):
		i = 0
		while True:
			yield i
			i += 1
	# 文字列化
	def __str__(self):
		return "<range-inf [0, 1, 2, ...]>"
	# 文字列化その2
	def __repr__(self): return str(self)

# オブジェクトをモジュールそのものと同一視
sys.modules[__name__] = RangeInf()
