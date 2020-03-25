import django
django.setup()
from polaaar.models import *

TFl = []
X = ProjectMetadata.objects.prefetch_related('event_hierarchy').all()
for x in X:
	Y=x.event_hierarchy.prefetch_related('event').all()
	for y in Y:
		Z = y.event.all()
		for z in Z:
			TFl.append(z.occurrence_exists)

if True in TFl:
	return("True")
else:
	return("False")