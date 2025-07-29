from NEMO.models import Project, Tool, User
from NEMO.serializers import ModelSerializer
from NEMO.views.constants import CHAR_FIELD_MAXIMUM_LENGTH, CHAR_FIELD_MEDIUM_LENGTH
from rest_flex_fields.serializers import FlexFieldsSerializerMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField, ListField

from NEMO_publications.models import (
    PublicationData,
    PublicationDataM2MValidationError,
    PublicationMetadata,
    UserPublicationStatus,
    validation_publication_data_m2m,
)
from NEMO_publications.utils import sanitize_doi


class PublicationMetadataSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = PublicationMetadata
        fields = "__all__"
        expandable_fields = {
            "creator": "NEMO.serializers.UserSerializer",
        }


class PublicationDataSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = PublicationData

        fields = "__all__"
        expandable_fields = {
            "metadata": "NEMO_publications.serializers.PublicationMetadataSerializer",
            "tools": ("NEMO.serializers.ToolSerializer", {"many": True}),
            "authors": ("NEMO.serializers.UserSerializer", {"many": True}),
            "projects": ("NEMO.serializers.ProjectSerializer", {"many": True}),
            "creator": "NEMO.serializers.UserSerializer",
        }

    def validate(self, data):
        try:
            m2m_fields = {
                "authors": User.objects.filter(id__in=[obj.id for obj in data["authors"]] if data["authors"] else []),
                "projects": Project.objects.filter(
                    id__in=[obj.id for obj in data["projects"]] if data["projects"] else []
                ),
                "tools": Tool.objects.filter(id__in=[obj.id for obj in data["tools"]] if data["tools"] else []),
            }
            validation_publication_data_m2m(m2m_fields, data["creator"])
            return data
        except PublicationDataM2MValidationError as e:
            raise ValidationError(e.message)


class PublicationSerializer(serializers.Serializer):
    doi = CharField(max_length=CHAR_FIELD_MAXIMUM_LENGTH, read_only=True)
    title = CharField(max_length=CHAR_FIELD_MAXIMUM_LENGTH, read_only=True)
    journal = CharField(max_length=CHAR_FIELD_MAXIMUM_LENGTH, read_only=True)
    year = IntegerField(read_only=True)
    status = IntegerField(read_only=True)
    authors = ListField()
    tools = ListField()
    projects = ListField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        fields = "__all__"


# This serializer allows to send either a username or a user id
class UserPublicationStatusSerializer(serializers.ModelSerializer):
    user = CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)

    class Meta:
        model = UserPublicationStatus
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation["user"] = instance.user.id
        except (ValueError, TypeError):
            representation["user"] = None
        return representation

    def validate_user(self, value):
        # Check if the input is a username or ID and fetch the user
        try:
            if value.isdigit():  # Try to process as an ID
                return User.objects.get(id=value)
            else:  # Else assume it is a username
                return User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found. Provide a valid username or ID.")

    def validate_doi(self, value):
        return sanitize_doi(value)
