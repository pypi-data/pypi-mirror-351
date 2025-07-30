from ..http import HttpClient
from .schemas import ActivityListResponse, ActivityResponse, ActivityType


class Activities:
    """活动管理类."""

    def __init__(self, client: HttpClient) -> None:
        self.client = client

    async def list_activities(
        self,
        app_id: str = None,
        user_id: str = None,
        service_code: str = None,
        instance_id: str = None,
        currency_type: str = None,
        activity_type: str = None,
        page: int = 1,
        limit: int = 10,
    ) -> ActivityListResponse:
        """获取活动列表.

        Args:
            app_id: 应用ID（可选）
            user_id: 用户ID（可选）
            service_code: 服务代码（可选）
            instance_id: 实例ID（可选）
            currency_type: 信用货币类型（可选）
            activity_type: 活动类型（可选）
            page: 页码（默认1）
            limit: 每页数量（默认10）

        Returns:
            ActivityListResponse: 活动列表响应
        """
        # 构建查询参数
        params = {"page": page, "limit": limit}
        if app_id is not None:
            params["app_id"] = app_id
        if user_id is not None:
            params["user_id"] = user_id
        if service_code is not None:
            params["service_code"] = service_code
        if instance_id is not None:
            params["instance_id"] = instance_id
        if currency_type is not None:
            params["currency_type"] = currency_type
        if activity_type is not None:
            params["activity_type"] = activity_type

        response = await self.client.get("/activities", params=params)
        return ActivityListResponse(**response["data"])


__all__ = [
    "Activities",
    "ActivityType",
    "ActivityResponse",
    "ActivityListResponse",
]
