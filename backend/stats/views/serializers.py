from rest_framework import serializers

from stats.logic.processing import KINDS


class BaseSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_valid(raise_exception=True)

    def get(self, key):
        return self.validated_data[key]


class ClearSerializer(BaseSerializer):
    kind = serializers.CharField(required=True)

    def validate_kind(self, value):
        if value not in KINDS:
            raise serializers.ValidationError('Incorrect kind.')
        return value


class ExtendTokenSerializer(BaseSerializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        if 'access_token' not in value:
            raise serializers.ValidationError('Incorrect token string.')
        return value
