from datetime import datetime
from django.dispatch import receiver
from collections import OrderedDict
from django.core.cache import cache
from django.db.models.signals import pre_delete, post_save
from django.db import models
from django.contrib.auth.models import User, UserManager
# Create your models here.

class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        now = datetime.now()
        setattr(model_instance, self.attname, now)
        return now


class AutoNewDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        if not add:
            return getattr(model_instance, self.attname)
        now = datetime.now()
        setattr(model_instance, self.attname, now)
        return now


class Member(User):

    phone = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=64, null=True)
    created_at = AutoNewDateTimeField(editable=False, db_index=True)
    objects =  UserManager()


class FollowerRelation(models.Model):

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='followers')
    follow_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='fans')
    followed_date = AutoNewDateTimeField(editable=False, db_index=True)


@receiver(post_save, sender=FollowerRelation)
def add_follower_relation_cache(sender, instance, *args, **kwargs):
    from account.serializers import MemberFansSerializer, MemberFollowedSerializer, MemberFriendSerializer

    follow_member, member = instance.follow_member, instance.member
    member_fans_cache_key = f'member_fans_cache:{follow_member.id}'
    member_followed_cache_key = f'member_follow_cache:{member.id}'
    member_friend_cache_key = f'member_follow_cache:{member.id}'
    follow_member_friend_cache_key = f'member_follow_cache:{follow_member.id}'

    if not cache.get(member_fans_cache_key):
        fans_query = follow_member.fans.select_related('member').all()
        serializer = MemberFansSerializer(fans_query, many=True)
        cache.set(member_fans_cache_key, serializer.data, timeout=60*60*6)
    elif cache.get(member_fans_cache_key):
        serializer = MemberFansSerializer(instance, many=False)
        cache_data = cache.get(member_fans_cache_key)
        cache_data.append(OrderedDict(serializer.data))
        cache.set(member_fans_cache_key, cache_data, timeout=60*60*6)

    if not cache.get(member_followed_cache_key):
        follow_query = member.followers.select_related('follow_member').all()
        serializer = MemberFollowedSerializer(follow_query, many=True)
        cache.set(member_followed_cache_key, serializer.data, timeout=60*60*6)
    elif cache.get(member_followed_cache_key):
        serializer = MemberFollowedSerializer(instance, many=False)
        cache_data = cache.get(member_followed_cache_key)
        cache_data.append(OrderedDict(serializer.data))
        cache.set(member_followed_cache_key, cache_data, timeout=60*60*6)

    # 相互關注才須加快取
    if FollowerRelation.objects.filter(member=instance.follow_member, follow_member=instance.member).exists():
        if not cache.get(member_friend_cache_key):
            followed_member = FollowerRelation.objects.filter(member=member).values('follow_member')
            queryset = FollowerRelation.objects.filter(follow_member=member, member__in=followed_member)
            serializer = MemberFriendSerializer(queryset, many=True)
            cache.set(member_friend_cache_key, serializer.data, timeout=60*60*6)
        else:
            serializer = MemberFollowedSerializer(instance, many=False)
            cache_data = cache.get(member_friend_cache_key)
            cache_data.append(OrderedDict(serializer.data))
            cache.set(member_friend_cache_key, cache_data, timeout=60*60*6)

        if not cache.get(follow_member_friend_cache_key):
            followed_member = FollowerRelation.objects.filter(member=follow_member).values('follow_member')
            queryset = FollowerRelation.objects.filter(follow_member=follow_member, member__in=followed_member)
            serializer = MemberFriendSerializer(queryset, many=True)
            cache.set(follow_member_friend_cache_key, serializer.data, timeout=60*60*6)
        else:
            serializer = MemberFollowedSerializer(instance, many=False)
            cache_data = cache.get(follow_member_friend_cache_key)
            cache_data.append(OrderedDict(serializer.data))
            cache.set(follow_member_friend_cache_key, cache_data, timeout=60*60*6)


@receiver(pre_delete, sender=FollowerRelation)
def remove_follower_relation_cache(sender, instance, *args, **kwargs):
    follow_member, member = instance.follow_member, instance.member
    member_fans_cache_key = f'member_fans_cache:{follow_member.id}'
    member_followed_cache_key = f'member_follow_cache:{member.id}'
    member_friend_cache_key = f'member_follow_cache:{member.id}'
    follow_member_friend_cache_key = f'member_follow_cache:{follow_member.id}'

    if cache.get(member_fans_cache_key):
        cache_data = cache.get(member_fans_cache_key)
        for elem in cache_data:
            if elem['member_info']['member_id'] == member.id:
                cache_data.remove(elem)
                cache.set(member_fans_cache_key, cache_data, 60*60*6)
                break

    if cache.get(member_followed_cache_key):
        cache_data = cache.get(member_followed_cache_key)
        for elem in cache_data:
            if elem['member_info']['member_id'] == follow_member.id:
                cache_data.remove(elem)
                cache.set(member_followed_cache_key, cache_data, 60*60*6)
                break

    if cache.get(member_friend_cache_key):
        cache_data = cache.get(member_friend_cache_key)
        for elem in cache_data:
            if elem['member_info']['member_id'] == follow_member.id:
                cache_data.remove(elem)
                cache.set(member_friend_cache_key, cache_data, 60*60*6)
                break

    if cache.get(follow_member_friend_cache_key):
        cache_data = cache.get(follow_member_friend_cache_key)
        for elem in cache_data:
            if elem['member_info']['member_id'] == member.id:
                cache_data.remove(elem)
                cache.set(follow_member_friend_cache_key, cache_data, 60*60*6)
                break
