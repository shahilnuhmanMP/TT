from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

from .models import Child, TrustedPerson

class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'

class TrustedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedPerson
        fields = '__all__'