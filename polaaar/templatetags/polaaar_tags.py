from django import template
register = template.Library()


@register.filter(name="getTrueOccurrence")
def getTrueOccurrence(qs):
	TFl = []		
	Y=qs.event_hierarchy.prefetch_related('event').all()
	for y in Y:
		Z = y.event.all()
		for z in Z:
			TFl.append(z.occurrence_exists)

	if True in TFl:
		return("True")
	else:
		return("False")


@register.filter(name="getTrueSequences")
def getTrueSequences(qs):
	TFl = []		
	Y=qs.event_hierarchy.prefetch_related('event').all()
	for y in Y:
		Z = y.event.all()
		for z in Z:
			TFl.append(z.sequences_exists)

	if True in TFl:
		return("True")
	else:
		return("False")


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