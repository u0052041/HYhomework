# HYhomework

## Description
包含功能:
1. 註冊會員和 access_token
2. 關注
3. 取消關注
4. 粉絲列表
5. 關注列表
6. 好友列表
7. 用 redis 管理關注/粉絲/好友 內容的快取


## API Endpoint


#### Register Member
```
HTTP_METHOD: POST
ENDPOINT: /api/member/register/

Description:
register account and return userinfo with access_token

Payload Field:
name(required)
username(required)
password(required)
phone(required)

Response:
{
    "id",
    "password",
    "last_login",
    "is_superuser",
    "username",
    "first_name",
    "last_name",
    "email",
    "is_staff",
    "is_active",
    "date_joined",
    "phone",
    "name",
    "created_at",
    "groups",
    "user_permissions",
    "auth": {
        "member_id",
        "member_name",
        "token_type",
        "access_token",
        "refresh_token",
        "expires",
        "expires_at",
    }
}
```

#### Follow other Member
```
HTTP_METHOD: POST
ENDPOINT: /api/member/follower/

Description:
follow other account with member_id

Payload Field:
follow_member(required)
```

#### Unfollow other Member
```
HTTP_METHOD: DELETE
ENDPOINT: /api/member/follower/unfollow/

Description:
unfollow other account with member_id

Payload Field:
follow_member(required)
```

#### Fans Page List
```
HTTP_METHOD: GET
ENDPOINT: /api/member/follower/fans-page/

Description:
list fans page

Query Params:
limit(optional)
offset(optional)

Response:
{
    "count",
    "next",
    "previous",
    "results",
        {
            "member_info": {
                "member_id",
                "member_name",
                "member_username",
            },
            "followed_date",
        }
    ]
}
```

#### Follow Page List
```
HTTP_METHOD: GET
ENDPOINT: /api/member/follower/followed-page/

Description:
list followed page

Query Params:
limit(optional)
offset(optional)

Response:
{
    "count",
    "next",
    "previous",
    "results",
        {
            "member_info": {
                "member_id",
                "member_name",
                "member_username",
            },
            "followed_date",
        }
    ]
}
```

#### Friends Page List
```
HTTP_METHOD: GET
ENDPOINT: /api/member/follower/friend-page/

Description:
list friends page

Query Params:
limit(optional)
offset(optional)

Response:
{
    "count",
    "next",
    "previous",
    "results",
        {
            "member_info": {
                "member_id",
                "member_name",
                "member_username",
            },
            "followed_date",
        }
    ]
}
```
