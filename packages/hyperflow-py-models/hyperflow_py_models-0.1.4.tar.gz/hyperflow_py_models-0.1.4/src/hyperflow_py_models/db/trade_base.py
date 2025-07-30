"""Abstract base model for trade data with common fields."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel
from hyperflow_py_models.hyperflow.core.v1.models import MarketType


class TradeBase(BaseModel):
    """Abstract base model for trade data with common fields."""

    __abstract__ = True

    # Primary key fields
    id: Mapped[PythonUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, nullable=False
    )
    event_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, nullable=False, index=True
    )

    # Transaction ID
    transaction_id: Mapped[str] = mapped_column(String(length=128), nullable=False, index=True)

    # Blockchain identifiers
    wallet_address: Mapped[str] = mapped_column(
        String(length=42), nullable=False, index=True
    )

    is_buy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_taker: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    # Token information
    symbol: Mapped[str] = mapped_column(
        String(length=20), nullable=False, index=True
    )
    # Trade amounts
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    quote_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )

    # Market type
    market_type: Mapped[MarketType] = mapped_column(
        SQLEnum("PERP", "SPOT", name="market_type"), nullable=False, index=True
    )

    # Additional metadata
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Additional metadata including flags like is_twap"
    )
