from datetime import date, timedelta
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Invoice, Vendor


class InvoiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_invoice(
        self,
        *,
        user_id: str,
        vendor: str,
        amount: float,
        invoice_date: date,
        invoice_id: Optional[str],
        currency: Optional[str],
        raw_text: Optional[str],
    ) -> Invoice:
        invoice = Invoice(
            user_id=user_id,
            vendor=vendor,
            amount=amount,
            date=invoice_date,
            invoice_id=invoice_id,
            currency=currency,
            raw_text=raw_text,
        )
        self.session.add(invoice)
        self.session.flush()
        self._upsert_vendor_stats(user_id=user_id, vendor=vendor)
        return invoice

    def is_duplicate(
        self,
        *,
        user_id: str,
        vendor: str,
        amount: float,
        invoice_date: date,
        window_days: int = 30,
    ) -> bool:
        start_date = invoice_date - timedelta(days=window_days)
        end_date = invoice_date + timedelta(days=window_days)
        stmt = (
            select(Invoice.id)
            .where(Invoice.user_id == user_id)
            .where(Invoice.vendor == vendor)
            .where(Invoice.amount == amount)
            .where(Invoice.date >= start_date)
            .where(Invoice.date <= end_date)
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none() is not None

    def vendor_exists(self, *, user_id: str, vendor: str) -> bool:
        stmt = (
            select(Vendor.id)
            .where(Vendor.user_id == user_id)
            .where(Vendor.name == vendor)
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none() is not None

    def get_vendor_stats(self, *, user_id: str, vendor: str) -> Tuple[float, int]:
        stmt = (
            select(Vendor.avg_amount, Vendor.invoice_count)
            .where(Vendor.user_id == user_id)
            .where(Vendor.name == vendor)
            .limit(1)
        )
        row = self.session.execute(stmt).first()
        if not row:
            return (0.0, 0)
        return (float(row[0]), int(row[1]))

    def get_invoice_history(
        self,
        *,
        user_id: str,
        vendor: str,
    ) -> Tuple[float, int]:
        stmt = (
            select(func.avg(Invoice.amount), func.count(Invoice.id))
            .where(Invoice.user_id == user_id)
            .where(Invoice.vendor == vendor)
        )
        avg_amount, count = self.session.execute(stmt).one()
        return (float(avg_amount or 0.0), int(count or 0))

    def _upsert_vendor_stats(self, *, user_id: str, vendor: str) -> None:
        avg_amount, invoice_count = self.get_invoice_history(user_id=user_id, vendor=vendor)
        stmt = (
            select(Vendor)
            .where(Vendor.user_id == user_id)
            .where(Vendor.name == vendor)
            .limit(1)
        )
        vendor_row = self.session.execute(stmt).scalar_one_or_none()
        if vendor_row is None:
            vendor_row = Vendor(
                user_id=user_id,
                name=vendor,
                avg_amount=avg_amount,
                invoice_count=invoice_count,
            )
            self.session.add(vendor_row)
            self.session.flush()
            return

        vendor_row.avg_amount = avg_amount
        vendor_row.invoice_count = invoice_count
        self.session.flush()

