from .desk_tracking import DeskStatusRepository, UserStatusRepository, DeskStatus, UserStatus
from .check_in_out import CheckInOutSystem

def new_user_status(id: str) -> UserStatus:
    return UserStatus(
        id=id,
        current_desk_id=None,
    )

def new_desk_status(id: str) -> DeskStatus:
    return DeskStatus(
        id=id,
        height_cm=None,
        position=None,
        sitting_seconds=0,
        standing_seconds=0,
        position_seconds=0,
        target_seconds=None,
        timer_overdue=False,
        reminder_due=False,
        last_reading_at=None,
        current_user_id=None,
    )


def test_check_in_out_checkin_normal():
    desk_statuses = DeskStatusRepository()
    user_statuses = UserStatusRepository()
    system = CheckInOutSystem(desk_statuses, user_statuses)

    user_id = "user1"
    desk_id = "desk1"
    user_statuses.create(new_user_status(user_id))
    desk_statuses.create(new_desk_status(desk_id))

    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None

    assert system.checkin(desk_id, user_id)
    assert user_statuses.get(user_id).current_desk_id == desk_id
    assert desk_statuses.get(desk_id).current_user_id == user_id


def test_check_in_out_checkin_busy():
    desk_statuses = DeskStatusRepository()
    user_statuses = UserStatusRepository()
    system = CheckInOutSystem(desk_statuses, user_statuses)

    user_id = "user1"
    user_id2 = "user2"
    desk_id = "desk1"
    user_statuses.create(new_user_status(user_id))
    user_statuses.create(new_user_status(user_id2))
    desk_statuses.create(new_desk_status(desk_id))

    assert user_statuses.get(user_id).current_desk_id == None
    assert user_statuses.get(user_id2).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None

    assert system.checkin(desk_id, user_id)
    assert user_statuses.get(user_id).current_desk_id == desk_id
    assert desk_statuses.get(desk_id).current_user_id == user_id

    assert not system.checkin(desk_id, user_id2)
    assert user_statuses.get(user_id).current_desk_id == desk_id
    assert desk_statuses.get(desk_id).current_user_id == user_id
    assert user_statuses.get(user_id2).current_desk_id == None


def test_check_in_out_checkin_move():
    desk_statuses = DeskStatusRepository()
    user_statuses = UserStatusRepository()
    system = CheckInOutSystem(desk_statuses, user_statuses)

    user_id = "user1"
    desk_id = "desk1"
    desk_id2 = "desk2"
    user_statuses.create(new_user_status(user_id))
    desk_statuses.create(new_desk_status(desk_id))
    desk_statuses.create(new_desk_status(desk_id2))

    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None
    assert desk_statuses.get(desk_id2).current_user_id == None

    assert system.checkin(desk_id, user_id)
    assert user_statuses.get(user_id).current_desk_id == desk_id
    assert desk_statuses.get(desk_id).current_user_id == user_id

    assert system.checkin(desk_id2, user_id)
    assert user_statuses.get(user_id).current_desk_id == desk_id2
    assert desk_statuses.get(desk_id).current_user_id == None
    assert desk_statuses.get(desk_id2).current_user_id == user_id


def test_check_in_out_checkout_normal():
    desk_statuses = DeskStatusRepository()
    user_statuses = UserStatusRepository()
    system = CheckInOutSystem(desk_statuses, user_statuses)

    user_id = "user1"
    desk_id = "desk1"
    user_statuses.create(new_user_status(user_id))
    desk_statuses.create(new_desk_status(desk_id))

    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None

    assert system.checkin(desk_id, user_id)
    assert system.checkout(desk_id, user_id)
    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None


def test_check_in_out_checkout_empty():
    desk_statuses = DeskStatusRepository()
    user_statuses = UserStatusRepository()
    system = CheckInOutSystem(desk_statuses, user_statuses)

    user_id = "user1"
    desk_id = "desk1"
    user_statuses.create(new_user_status(user_id))
    desk_statuses.create(new_desk_status(desk_id))
    
    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None

    assert not system.checkout(desk_id, user_id)
    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None


def test_check_in_out_checkout_twice():
    desk_statuses = DeskStatusRepository()
    user_statuses = UserStatusRepository()
    system = CheckInOutSystem(desk_statuses, user_statuses)

    user_id = "user1"
    desk_id = "desk1"
    user_statuses.create(new_user_status(user_id))
    desk_statuses.create(new_desk_status(desk_id))

    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None

    assert system.checkin(desk_id, user_id)
    assert system.checkout(desk_id, user_id)
    assert not system.checkout(desk_id, user_id)
    assert user_statuses.get(user_id).current_desk_id == None
    assert desk_statuses.get(desk_id).current_user_id == None
