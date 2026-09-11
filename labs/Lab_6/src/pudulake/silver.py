"""Transformaciones y reglas críticas de las entidades Silver."""

from __future__ import annotations
from src.pudulake.contracts import ContractViolation
import polars as pl


def build_orders(orders: pl.DataFrame) -> pl.DataFrame:
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    allowed_status = [
        "approved",
        "canceled",
        "created",
        "delivered",
        "invoiced",
        "processing",
        "shipped",
        "unavailable",
    ]

    # Detectar valores presentes que no pueden convertirse
    invalid_dates = orders.select(
        pl.any_horizontal(
            [
                pl.col(col).is_not_null()
                & (
                    pl.col(col)
                    .cast(pl.String)
                    .str.to_datetime(strict=False)
                    .is_null()
                )
                for col in date_cols
            ]
        )
        .sum()
        .alias("invalid_dates")
    ).item()

    if invalid_dates > 0:
        raise ContractViolation(
            f"Se encontraron {invalid_dates} fechas no interpretables."
        )

    invalid_status = orders.filter(
        pl.col("order_status").is_null()
        | ~pl.col("order_status").is_in(allowed_status)
    )

    if invalid_status.height > 0:
        raise ContractViolation(
            f"Se encontraron {invalid_status.height} estados inválidos."
        )

    orders_silver = orders.with_columns(
        [
            pl.col(col)
            .cast(pl.String)
            .str.to_datetime(strict=False)
            .alias(col)
            for col in date_cols
        ]
    )

    orders_silver = orders_silver.with_columns(
        (
            (pl.col("order_status") == "delivered")
            & pl.col("order_delivered_customer_date").is_null()
        ).alias("delivery_timestamp_missing")
    )

    invalid_delivery_dates = orders_silver.filter(
        (pl.col("order_status") == "delivered")
        & pl.col("order_delivered_customer_date").is_not_null()
        & (
            pl.col("order_delivered_customer_date")
            < pl.col("order_purchase_timestamp")
        )
    )

    if invalid_delivery_dates.height > 0:
        raise ContractViolation(
            "Se encontraron órdenes entregadas antes de su fecha de compra."
        )

    return orders_silver


def build_customers(customers: pl.DataFrame) -> pl.DataFrame:
    """Conserva clientes y verifica la relación uno a uno con customer_id."""
    return customers.clone()


def build_order_items(items: pl.DataFrame) -> pl.DataFrame:
    non_finite = items.filter(
        ~pl.col("price").is_finite()
        | ~pl.col("freight_value").is_finite()
    )

    if non_finite.height > 0:
        raise ContractViolation(
            f"Se encontraron {non_finite.height} montos no finitos."
        )

    negative = items.filter(
        (pl.col("price") < 0)
        | (pl.col("freight_value") < 0)
    )

    if negative.height > 0:
        raise ContractViolation(
            f"Se encontraron {negative.height} montos negativos."
        )

    return items.clone()


def build_payments(payments: pl.DataFrame) -> pl.DataFrame:
    non_finite = payments.filter(
        ~pl.col("payment_value").is_finite()
    )

    if non_finite.height > 0:
        raise ContractViolation(
            f"Se encontraron {non_finite.height} pagos no finitos."
        )

    negative = payments.filter(
        pl.col("payment_value") < 0
    )

    if negative.height > 0:
        raise ContractViolation(
            f"Se encontraron {negative.height} pagos negativos."
        )

    return payments.clone()


def validate_relationships(
    orders: pl.DataFrame,
    customers: pl.DataFrame,
    items: pl.DataFrame,
    payments: pl.DataFrame,
) -> None:
    """Verifica las claves foráneas antes de construir productos Gold."""

    orphan_orders = orders.join(
        customers.select("customer_id"),
        on="customer_id",
        how="anti",
    )

    orphan_items = items.join(
        orders.select("order_id"),
        on="order_id",
        how="anti",
    )

    orphan_payments = payments.join(
        orders.select("order_id"),
        on="order_id",
        how="anti",
    )

    if orphan_orders.height > 0:
        raise ContractViolation(
            "Relación inválida: orders.customer_id -> customers.customer_id "
            f"({orphan_orders.height} filas huérfanas)."
        )

    if orphan_items.height > 0:
        raise ContractViolation(
            "Relación inválida: order_items.order_id -> orders.order_id "
            f"({orphan_items.height} filas huérfanas)."
        )

    if orphan_payments.height > 0:
        raise ContractViolation(
            "Relación inválida: payments.order_id -> orders.order_id "
            f"({orphan_payments.height} filas huérfanas)."
        )
