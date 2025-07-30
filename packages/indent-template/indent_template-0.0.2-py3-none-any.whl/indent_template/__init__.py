
# インデントを崩さずに文字列を置き換える [indent_template]

import sys

# インデント文字一覧
indent_symbol_list = list("\t ")

# その行のインデントを明らかにする
def get_indent(line_str):
	indent_str = ""
	for letter in line_str:
		# インデントから出たら終了
		if letter not in indent_symbol_list:
			break
		# 追記
		indent_str += letter
	return indent_str

# 置き換え後の文字列の2行目以降にインデントを施す
def add_indent(rep_str, indent_str):
	# 行分解
	ls = rep_str.split("\n")
	# 2行目以降にインデントを付加
	for idx in range(1, len(ls)):
		ls[idx] = indent_str + ls[idx]
	# 行結合
	indented_rep_str = "\n".join(ls)
	return indented_rep_str

# 1パターン・1行だけ置き換え
def one_replace(
	line_str,	# 元の文字列 (1行)
	key,	# 置き換える対象の文字列
	rep_str	# 置き換え後の文字列
):
	# その行のインデントを明らかにする
	indent_str = get_indent(line_str)
	# 置き換え後の文字列の2行目以降にインデントを施す
	indented_rep_str = add_indent(rep_str, indent_str)
	# 置き換えて返す
	return line_str.replace(key, indented_rep_str)

# インデントを崩さずに文字列を置き換える [indent_template]
def replace(
	template_str,	# 置き換え元の文字列
	replace_dic	# 置き換えパターン
):
	# 行ごとに区切って置き換えを実行
	line_ls = template_str.split("\n")
	line_n = len(line_ls)
	for idx in range(line_n):
		# 置き換えパターンをすべて置き換え
		for key in replace_dic:
			rep_str = str(replace_dic[key])	# 置き換え後が文字列型であることを保証 (数値などを想定)
			# 1パターン・1行だけ置き換え
			line_ls[idx] = one_replace(
				line_ls[idx],	# 元の文字列 (1行)
				key,	# 置き換える対象の文字列
				rep_str	# 置き換え後の文字列
			)
	# 結合して返す
	result_str = "\n".join(line_ls)
	return result_str
