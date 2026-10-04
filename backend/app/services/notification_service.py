from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification


class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        title: str,
        message: str,
        type: str = "info",
        user_id: Optional[str] = None,
        link_url: Optional[str] = None
    ) -> Notification:
        """Create and persist an in-app notification."""
        notif = Notification(
            title=title,
            message=message,
            type=type,
            user_id=user_id,
            link_url=link_url,
            is_read=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif


notification_service = NotificationService()
