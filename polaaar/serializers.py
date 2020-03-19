from accounts.models import *
from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ['url','full_name','email']


class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = ['url','footprintWKT','eventRemarks','sample_name','collection_date',
        'collection_time','parent_event','parent_sample','samplingProtocol',
        'occurrence','environment','metadata_exists','occurrence_exists','environment_exists']
