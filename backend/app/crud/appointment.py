from __future__ import annotations

from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.appointment import Appointment, Counselor


class CRUDCounselor(CRUDBase[Counselor, dict, dict]):
    def list_active(self, db: Session) -> List[Counselor]:
        return db.query(Counselor).filter(Counselor.is_active == True).all()

    def get_by_user(self, db: Session, user_id: int) -> Optional[Counselor]:
        return db.query(Counselor).filter(Counselor.user_id == user_id).first()

    def deactivate(self, db: Session, counselor: Counselor):
        counselor.is_active = False
        db.commit()


class CRUDAppointment(CRUDBase[Appointment, dict, dict]):
    def list_by_user(self, db: Session, user_id: int) -> List[Appointment]:
        return (
            db.query(Appointment)
            .filter(Appointment.user_id == user_id)
            .order_by(desc(Appointment.appointment_time))
            .all()
        )

    def list_by_counselor(self, db: Session, counselor_id: int) -> List[Appointment]:
        return (
            db.query(Appointment)
            .filter(Appointment.counselor_id == counselor_id)
            .order_by(desc(Appointment.appointment_time))
            .all()
        )

    def list_all(self, db: Session) -> List[Appointment]:
        return db.query(Appointment).order_by(desc(Appointment.appointment_time)).all()

    def update_status(
        self, db: Session, appt: Appointment, *, status: str, counselor_note: Optional[str] = None
    ) -> Appointment:
        appt.status = status
        if counselor_note:
            appt.counselor_note = counselor_note
        db.commit()
        db.refresh(appt)
        return appt


counselor = CRUDCounselor(Counselor)
appointment = CRUDAppointment(Appointment)
