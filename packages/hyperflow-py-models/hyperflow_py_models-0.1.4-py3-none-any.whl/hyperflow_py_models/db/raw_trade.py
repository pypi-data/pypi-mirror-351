"""Raw trade model for storing trade events from various exchanges."""

from sqlalchemy import Index, UniqueConstraint

from .trade_base import TradeBase


class RawTrade(TradeBase):
    """Model for storing raw trade data from various exchanges and chain_ids."""

    __abstract__ = False

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "symbol",
            "event_at",
            "is_buy",
            name="uix_raw_trade_txn_coin_event_at_is_buy",
        ),
        Index(
            "ix_raw_trade_event_at",
            "event_at",
            postgresql_using="btree",
        ),
        Index(
            "ix_raw_trade_wallet_address",
            "wallet_address",
            postgresql_using="btree",
        ))

    def __repr__(self) -> str:
        """String representation of the RawTrade."""
        return (
            f"<RawTrade(id={self.id}, "
            f"wallet={self.wallet_address[:8]}..., "
            f"pair={self.token_symbol_pair}, "
            f"is_buy={self.is_buy})"
        )
