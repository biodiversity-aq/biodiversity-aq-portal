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