from datetime import date
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from sqlalchemy import select, func, and_, or_
from app.database import async_session_maker, engine

from app.hotels.models import Rooms
from app.users.models import Users


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def add(
            cls,
            user_id: int,
            room_id: int,
            date_from: date,
            date_to: date,
    ):
        async with async_session_maker() as session:

            booked_rooms = select(Bookings).where(
                and_(
                    Bookings.room_id == 1,
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from
                        ),
                    )
                )
            ).cte('booked_rooms')

            rooms_left = select(
                (Rooms.quantity - func.count(booked_rooms.c.room_id)).label('rooms-left')
            ).select_from(Rooms).join(
                booked_rooms, booked_rooms.c.room_id == Rooms.id
            ).where(room_id == 1).group_by(
                Rooms.quantity, booked_rooms.c.room_id
            )

            print(rooms_left.compile(engine, compile_kwargs={'literal_binds': True}))

            rooms_left = await session.execute(rooms_left)
            print(rooms_left.scalar())
