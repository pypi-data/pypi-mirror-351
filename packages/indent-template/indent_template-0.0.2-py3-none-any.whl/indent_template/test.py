
# インデントを崩さずに文字列を置き換える [indent_template]
# 【動作確認 / 使用例】

import sys
from ezpip import load_develop
# インデントを崩さずに文字列を置き換える [indent_template]
indent_template = load_develop("indent_template", "../", develop_flag = True)

# 置き換え元の文字列
template_str = """
def func():
	ls = VALUE_HERE
	print(str(ls + VALUE_HERE))
"""

# 置き換え後文字列
rep_str = """[
	"hoge",
	"fuga"
]"""

# インデントを崩さずに文字列を置き換える [indent_template]
result_str = indent_template.replace(
	template_str,	# 置き換え元の文字列
	{"VALUE_HERE": rep_str}	# 置き換えパターン
)
# 結果確認
print(result_str)

"""【参考】結果
def func():
        ls = [
                "hoge",
                "fuga"
        ]
        print(str(ls + [
                "hoge",
                "fuga"
        ]))
"""