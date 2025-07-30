"""Enriched trade model extending TradeBase with PnL information."""

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import Index, Interval, Numeric, UniqueConstraint, desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .trade_base import TradeBase


class EnrichedTrade(TradeBase):
    """Model for storing enriched trade data with PnL calculations."""

    __abstract__ = False

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "symbol",
            "event_at",
            "is_buy",
            name="uix_enriched_trade_txn_coin_event_at_is_buy",
        ),
        Index(
            "ix_enriched_trade_event_at",
            "event_at",
            postgresql_using="btree",
        ),
        Index(
            "ix_enriched_trade_wallet_address",
            "wallet_address",
            postgresql_using="btree",
        ))

    # PnL (Profit and Loss) information
    pnl_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Profit/Loss in USD for this trade (if part of a matched pair)",
    )

    pnl: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Profit/Loss in quote token amount for this trade (if part of a matched pair)",
    )

    holding_duration: Mapped[Optional[timedelta]] = mapped_column(
        Interval, nullable=True, comment="Holding duration as a time interval"
    )

    def __repr__(self) -> str:
        """String representation of the EnrichedTrade."""
        return (
            f"<EnrichedTrade(id={self.id}, "
            f"wallet={self.wallet_address[:8]}..., "
            f"pair={self.token_symbol_pair}, "
            f"is_buy={self.is_buy}, "
            f"pnl_usd={self.pnl_usd if self.pnl_usd is not None else 'None'})>"
        )
