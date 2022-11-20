from rest_framework import serializers
from django.db import transaction

from account.models import Member, FollowerRelation
from account.utils import _fake_grant_token


class MemberRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = '__all__'

    def create(self, validated_data):

        phone = validated_data.pop('phone')
        password = validated_data.pop('password')

        with transaction.atomic():
            member = Member.objects.create_user(password=password, **validated_data)

        member.phone = phone
        member.save()
        return member

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        auth = _fake_grant_token(instance)
        ret['auth'] = auth
        return ret


class MemberFollowerSerializer(serializers.ModelSerializer):

    class Meta:
        model = FollowerRelation
        fields = ['member', 'follow_member', 'followed_date']

    def to_internal_value(self, data):
        request = self.context.get('request')
        data['member'] = request.user.id
        return super().to_internal_value(data)

    def create(self, validated_data):
        if FollowerRelation.objects.filter(member=validated_data['member'],
                                           follow_member=validated_data['follow_member']):
            raise serializers.ValidationError({'error': 'already followed'})

        return super().create(validated_data)


class MemberFollowedSerializer(MemberFollowerSerializer):
    member_info = serializers.SerializerMethodField()

    class Meta:
        model = FollowerRelation
        fields = ['member_info', 'followed_date']

    def get_member_info(self, instance):
        return {
            'member_id': instance.follow_member_id,
            'member_name': instance.follow_member.name,
            'member_username': instance.follow_member.username,
        }


class MemberFansSerializer(MemberFollowerSerializer):
    member_info = serializers.SerializerMethodField()

    class Meta:
        model = FollowerRelation
        fields = ['member_info', 'followed_date']

    def get_member_info(self, instance):
        return {
            'member_id': instance.member_id,
            'member_name': instance.member.name,
            'member_username': instance.member.username,
        }


class MemberFriendSerializer(MemberFollowerSerializer):
    member_info = serializers.SerializerMethodField()

    class Meta:
        model = FollowerRelation
        fields = ['member_info']

    def get_member_info(self, instance):
        return {
            'member_id': instance.member_id,
            'member_name': instance.member.name,
            'member_username': instance.member.username,
        }
