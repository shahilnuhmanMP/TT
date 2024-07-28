from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source= 'user.username')
    trusted_person_name =  serializers.ReadOnlyField(source= 'trusted_person.name')
    child_name = serializers.ReadOnlyField(source= 'child.name')
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