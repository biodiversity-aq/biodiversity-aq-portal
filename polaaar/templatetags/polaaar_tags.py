from django import template
register = template.Library()


@register.filter(name='getUniqueEnv')
def getuniqueEnv(qs):
	Y = qs.order_by('env_variable__name').distinct('env_variable__name')
	return(Y)

@register.filter(name='getNum')
def getNum(qs):
	Y = qs.values_list('env_variable__var_type')
	try:
		x = Y.index('num')
	except:
		x = 0
	if x != 0:
		return True
	else:
		return False