from .desk_tracking import DeskStatusRepository, UserStatusRepository

class CheckInOutSystem:
    def __init__(self, desk_statuses: DeskStatusRepository, user_statuses: UserStatusRepository):
        self.desk_statuses = desk_statuses
        self.user_statuses = user_statuses
    
    def checkin(self, desk_id: str, user_id: str) -> bool:
        desk_status = self.desk_statuses.get(desk_id)
        if desk_status is None:
            return False
        user_status = self.user_statuses.get(user_id)
        if user_status is None:
            return False
        
        if desk_status.current_user_id == user_id:
            return False
        if desk_status.current_user_id is not None:
            return False
        
        if user_status.current_desk_id is not None:
            if not self.checkout(user_status.current_desk_id, user_id):
                return False
        
        user_status.current_desk_id = desk_id
        desk_status.current_user_id = user_id
        self.desk_statuses.update(desk_status)
        self.user_statuses.update(user_status)
        return True
        
    def checkout(self, desk_id: str, user_id: str) -> bool:
        desk_status = self.desk_statuses.get(desk_id)
        if desk_status is None:
            return False
        user_status = self.user_statuses.get(user_id)
        if user_status is None:
            return False
        
        if user_status.current_desk_id is None:
            return False
        
        user_status.current_desk_id = None
        desk_status.current_user_id = None
        self.desk_statuses.update(desk_status)
        self.user_statuses.update(user_status)
        return True
