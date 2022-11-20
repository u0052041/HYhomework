from rest_framework import viewsets, status, mixins, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache

from account.models import Member, FollowerRelation
from account.serializers import (
    MemberRegisterSerializer, MemberFollowerSerializer, MemberFollowedSerializer, MemberFansSerializer,
    MemberFriendSerializer
)


class MemberRegisterViewSet(mixins.CreateModelMixin,
                            viewsets.GenericViewSet):

    model = Member
    queryset = Member.objects.all()
    serializer_class = MemberRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MemberFollowerViewSet(mixins.CreateModelMixin,
                            viewsets.GenericViewSet):

    model = FollowerRelation
    queryset = FollowerRelation.objects.all()
    serializer_class = MemberFollowerSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):

        serializer_mapping = {
            'fans_page': MemberFansSerializer,
            'followed_page': MemberFollowedSerializer,
            'friend_page': MemberFriendSerializer
        }
        if self.action_map and serializer_mapping.get(self.action_map.get('get')):
            return serializer_mapping.get(self.action_map.get('get'))

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)

    @action(url_path='unfollow', detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, *args, **kwargs):
        follow_member_id = request.data.get('follow_member')
        obj = self.queryset.filter(member=self.request.user, follow_member_id=follow_member_id).first()
        if not obj:
            return Response('target member not found', status=status.HTTP_400_BAD_REQUEST)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(url_path='fans-page', detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def fans_page(self, request, *args, **kwargs):
        # 粉絲清單
        ret = cache.get(f'member_fans_cache:{self.request.user}')
        if ret:
            page = self.paginate_queryset(ret)
            return self.get_paginated_response(page)

        queryset = self.queryset.filter(follow_member=self.request.user).select_related('member').order_by('-followed_date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(url_path='followed-page', detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def followed_page(self, request, *args, **kwargs):
        # 關注清單
        ret = cache.get(f'member_follow_cache:{self.request.user.id}')
        if ret:
            page = self.paginate_queryset(ret)
            return self.get_paginated_response(page)

        queryset = self.queryset.filter(member=self.request.user).select_related('follow_member').order_by('-followed_date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(url_path='friend-page', detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def friend_page(self, request, *args, **kwargs):
        # 好友清單
        ret = cache.get(f'member_friend_cache:{self.request.user.id}')
        if ret:
            page = self.paginate_queryset(ret)
            return self.get_paginated_response(page)

        followed_member = self.queryset.filter(member=self.request.user).values('follow_member')
        queryset = self.queryset.filter(follow_member=self.request.user, member__in=followed_member)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
