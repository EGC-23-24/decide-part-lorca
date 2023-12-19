from rest_framework import serializers

from .models import Question, QuestionOption, QuestionOptionRanked, Voting, QuestionOptionYesNo
from base.serializers import KeySerializer, AuthSerializer


class QuestionOptionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for QuestionOption model.

    Provides serialization for QuestionOption objects with hyperlinked relationships.

    Attributes:
        Meta: Meta class with model and field specifications.
    """

    class Meta:
        """
        Meta class for QuestionOptionSerializer.

        Specifies the model and fields to be serialized.
        """

        model = QuestionOption
        fields = ('number', 'option')


class QuestionOptionRankedSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for QuestionOptionRanked model.

    Provides serialization for QuestionOptionRanked objects with hyperlinked relationships.

    Attributes:
        Meta: Meta class with model and field specifications.
    """

    class Meta:
        """
        Meta class for QuestionOptionRankedSerializer.

        Specifies the model and fields to be serialized.
        """

        model = QuestionOptionRanked
        fields = ('number', 'option')


class QuestionOptionYesNoSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for QuestionOptionYesNo model.

    Provides serialization for QuestionOptionYesNo objects with hyperlinked relationships.

    Attributes:
        Meta: Meta class with model and field specifications.
    """

    class Meta:
        """
        Meta class for QuestionOptionYesNoSerializer.

        Specifies the model and fields to be serialized.
        """

        model = QuestionOptionYesNo
        fields = ('number', 'option')


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Question model.

    Provides serialization for Question objects with hyperlinked relationships. Includes a custom method for serializing related options based on the question type.

    Attributes:
        options (SerializerMethodField): Field to serialize related options.
        Meta: Meta class with model and field specifications.
    """

    options = serializers.SerializerMethodField()

    def get_options(self, instance):
        """
        Custom method to serialize related options based on the question type.

        :param instance: The Question instance being serialized.
        :type instance: Question
        :return: Serialized data of related options.
        :rtype: dict or None
        """

        if instance.type == 'C':
            serializer = QuestionOptionSerializer(
                instance.options.all(), many=True).data
        elif instance.type == 'R':
            serializer = QuestionOptionRankedSerializer(
                instance.ranked_options.all(), many=True).data
        elif instance.type == 'Y':
            serializer = QuestionOptionYesNoSerializer(
                instance.yesno_options.all(), many=True).data
        elif instance.type == 'M':
            serializer = QuestionOptionSerializer(
                instance.options.all(), many=True).data
        elif instance.type == 'T':
            serializer = None
        return serializer

    class Meta:
        """
        Meta class for QuestionSerializer.

        Specifies the model and fields to be serialized.
        """

        model = Question
        fields = ('desc', 'options', 'type')


class VotingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for Voting model.

    Provides serialization for Voting objects with hyperlinked relationships and nested serialization for related objects.

    Attributes:
        question (QuestionSerializer): Nested serializer for the related question.
        pub_key (KeySerializer): Nested serializer for the related public key.
        auths (AuthSerializer): Nested serializer for related authorizations.
        Meta: Meta class with model and field specifications.
    """

    question = QuestionSerializer(many=False)
    pub_key = KeySerializer()
    auths = AuthSerializer(many=True)

    class Meta:
        """
        Meta class for VotingSerializer.

        Specifies the model and fields to be serialized.
        """

        model = Voting
        fields = (
            'id',
            'name',
            'desc',
            'question',
            'start_date',
            'end_date',
            'future_stop',
            'pub_key',
            'auths',
            'tally',
            'postproc')


class SimpleVotingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Simplified serializer for Voting model.

    Provides a simpler serialization for Voting objects focusing on key details.

    Attributes:
        question (QuestionSerializer): Nested serializer for the related question.
        Meta: Meta class with model and field specifications.
    """

    question = QuestionSerializer(many=False)

    class Meta:
        """
        Meta class for SimpleVotingSerializer.

        Specifies the model and fields to be serialized.
        """

        model = Voting
        fields = (
            'name',
            'desc',
            'question',
            'start_date',
            'end_date',
            'future_stop')
