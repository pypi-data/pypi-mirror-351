"""Position model for tracking trading positions."""

from datetime import datetime
from decimal import Decimal
from decimal import Decimal
from typing import Optional
from uuid import UUID as PythonUUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel
from hyperflow_py_models.hyperflow.core.v1.models import MarketType


class Position(BaseModel):
    """Model for tracking trading positions."""

    __abstract__ = False

    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "wallet_address",
            "is_buy",
            "market_type",
            name="uix_position_symbol_wallet_address_is_buy_market_type",
        ),
        Index(
            "ix_position_wallet_address",
            "wallet_address",
            postgresql_using="btree",
        ),
        Index(
            "ix_position_wallet_address_symbol",
            "wallet_address",
            "symbol",
            postgresql_using="btree",
        ),
        Index(
            "ix_position_wallet_address_symbol_market_type",
            "wallet_address",
            "symbol",
            "market_type",
            postgresql_using="btree",
        ),
    )

    # Primary key fields
    id: Mapped[PythonUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, nullable=False
    )
    # Blockchain identifiers
    wallet_address: Mapped[str] = mapped_column(
        String(length=42), nullable=False, index=True
    )

    is_buy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    average_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    # Trade amounts
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    quote_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )

    # Token information
    symbol: Mapped[str] = mapped_column(
        String(length=20), nullable=False, index=True
    )

    # Market type
    market_type: Mapped[MarketType] = mapped_column(
        SQLEnum("PERP", "SPOT", name="market_type", create_type=False), nullable=False, index=True
    )


    def __repr__(self) -> str:
        """String representation of the Position."""
        return (
            f"<Position(id={self.id}, "
            f"wallet_address={self.wallet_address[:8]}..., "
            f"symbol={self.symbol}, "
            f"is_buy={self.is_buy}, "
            f"average_price={self.average_price})>"
        )