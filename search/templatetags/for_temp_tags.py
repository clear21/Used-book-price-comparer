from django import template

#参照
#http://django-docs-ja.readthedocs.io/en/latest/howto/custom-template-tags.html

#全てのタグ・フィルタの情報
register = template.Library()

#文字列結合
def stradd(value , arg):
	return str(value) + str(arg)

register.filter('stradd' , stradd)

#価格表示用（例：\1,000）
def price_format(value):
	return "￥{0:,d}".format(int(value))

register.filter('price_format' , price_format)