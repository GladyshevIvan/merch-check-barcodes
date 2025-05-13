from uuid import UUID
from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Shops(Base):
    '''Таблица с информацией о магазинах'''

    __tablename__ = 'shops'

    shop_id: Mapped[UUID] = mapped_column(primary_key=True)
    fn: Mapped[str] = mapped_column(primary_key=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)

    # Ограничения для таблицы
    __table_args__ = (
        CheckConstraint('fn ~ \'^[0-9]{16}$\'', name='fn_length_constraint'),  # Ограничение для fn: 16 цифр
    )


class UsedChecks(Base):
    '''Таблица с использованными чеками'''

    __tablename__ = 'used_checks'

    fp: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fn: Mapped[str] = mapped_column(primary_key=True)
    i: Mapped[int] = mapped_column(BigInteger, nullable=False)
    t: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


    #Ограничения для таблицы
    __table_args__ = (
        CheckConstraint('fp BETWEEN 0 AND 9999999999', name='fp_length_constraint'), #Ограничение для fp: максимум 10 цифр
        CheckConstraint('fn ~ \'^[0-9]{16}$\'', name='fn_length_constraint'),  #Ограничение для fn: 16 цифр
        CheckConstraint('i BETWEEN 0 AND 9999999999', name='i_length_constraint'),  #Ограничение для i: максимум 10 цифр
    )


class CompletedTasks(Base):
    '''Таблица с засчитанной работой'''

    __tablename__ = 'completed_tasks'

    employee_id: Mapped[UUID] = mapped_column(primary_key=True)
    shop_id: Mapped[UUID] = mapped_column(primary_key=True)
    date_and_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)