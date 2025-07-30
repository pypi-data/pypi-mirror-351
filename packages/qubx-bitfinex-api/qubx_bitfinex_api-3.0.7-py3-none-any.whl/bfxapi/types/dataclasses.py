from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

from .labeler import _Type, compose, partial

# region Dataclass definitions for types of public use


@dataclass
class PlatformStatus(_Type):
    status: int


@dataclass
class TradingPairTicker(_Type):
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    daily_change: float
    daily_change_relative: float
    last_price: float
    volume: float
    high: float
    low: float


@dataclass
class FundingCurrencyTicker(_Type):
    frr: float
    bid: float
    bid_period: int
    bid_size: float
    ask: float
    ask_period: int
    ask_size: float
    daily_change: float
    daily_change_relative: float
    last_price: float
    volume: float
    high: float
    low: float
    frr_amount_available: float


@dataclass
class TickersHistory(_Type):
    symbol: str
    bid: float
    ask: float
    mts: int


@dataclass
class TradingPairTrade(_Type):
    id: int
    mts: int
    amount: float
    price: float


@dataclass
class FundingCurrencyTrade(_Type):
    id: int
    mts: int
    amount: float
    rate: float
    period: int


@dataclass
class TradingPairBook(_Type):
    price: float
    count: int
    amount: float


@dataclass
class FundingCurrencyBook(_Type):
    rate: float
    period: int
    count: int
    amount: float


@dataclass
class TradingPairRawBook(_Type):
    order_id: int
    price: float
    amount: float


@dataclass
class FundingCurrencyRawBook(_Type):
    offer_id: int
    period: int
    rate: float
    amount: float


@dataclass
class Statistic(_Type):
    mts: int
    value: float


@dataclass
class Candle(_Type):
    mts: int
    open: int
    close: int
    high: int
    low: int
    volume: float


@dataclass
class DerivativesStatus(_Type):
    mts: int
    deriv_price: float
    spot_price: float
    insurance_fund_balance: float
    next_funding_evt_mts: int
    next_funding_accrued: float
    next_funding_step: int
    current_funding: float
    mark_price: float
    open_interest: float
    clamp_min: float
    clamp_max: float


@dataclass
class Liquidation(_Type):
    pos_id: int
    mts: int
    symbol: str
    amount: float
    base_price: float
    is_match: int
    is_market_sold: int
    liquidation_price: float


@dataclass
class Leaderboard(_Type):
    mts: int
    username: str
    ranking: int
    value: float
    twitter_handle: Optional[str]


@dataclass
class FundingStatistic(_Type):
    mts: int
    frr: float
    avg_period: float
    funding_amount: float
    funding_amount_used: float
    funding_below_threshold: float


@dataclass
class PulseProfile(_Type):
    puid: str
    mts: int
    nickname: str
    picture: str
    text: str
    twitter_handle: str
    followers: int
    following: int
    tipping_status: int


@dataclass
class PulseMessage(_Type):
    pid: str
    mts: int
    puid: str
    title: str
    content: str
    is_pin: int
    is_public: int
    comments_disabled: int
    tags: List[str]
    attachments: List[str]
    meta: List[Dict[str, Any]]
    likes: int
    profile: PulseProfile
    comments: int


@dataclass
class TradingMarketAveragePrice(_Type):
    price_avg: float
    amount: float


@dataclass
class FundingMarketAveragePrice(_Type):
    rate_avg: float
    amount: float


@dataclass
class FxRate(_Type):
    current_rate: float


# endregion

# region Dataclass definitions for types of auth use


@dataclass
class UserInfo(_Type):
    id: int
    email: str
    username: str
    mts_account_create: int
    verified: int
    verification_level: int
    timezone: str
    locale: str
    company: str
    email_verified: int
    mts_master_account_create: int
    group_id: int
    master_account_id: int
    inherit_master_account_verification: int
    is_group_master: int
    group_withdraw_enabled: int
    ppt_enabled: int
    merchant_enabled: int
    competition_enabled: int
    two_factors_authentication_modes: List[str]
    is_securities_master: int
    securities_enabled: int
    allow_disable_ctxswitch: int
    time_last_login: int
    ctxtswitch_disabled: int
    comp_countries: List[str]
    compl_countries_resid: List[str]
    is_merchant_enterprise: int


@dataclass
class LoginHistory(_Type):
    id: int
    time: int
    ip: str
    extra_info: Dict[str, Any]


@dataclass
class BalanceAvailable(_Type):
    amount: float


@dataclass
class Order(_Type):
    id: int
    gid: int
    cid: int
    symbol: str
    mts_create: int
    mts_update: int
    amount: float
    amount_orig: float
    order_type: str
    type_prev: str
    mts_tif: int
    flags: int
    order_status: str
    price: float
    price_avg: float
    price_trailing: float
    price_aux_limit: float
    notify: int
    hidden: int
    placed_id: int
    routing: str
    meta: Dict[str, Any]


@dataclass
class Position(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    margin_funding: float
    margin_funding_type: int
    pl: float
    pl_perc: float
    price_liq: float
    leverage: float
    position_id: int
    mts_create: int
    mts_update: int
    type: int
    collateral: float
    collateral_min: float
    meta: Dict[str, Any]


@dataclass
class Trade(_Type):
    id: int
    symbol: str
    mts_create: int
    order_id: int
    exec_amount: float
    exec_price: float
    order_type: str
    order_price: float
    maker: int
    fee: float
    fee_currency: str
    cid: int


@dataclass()
class FundingTrade(_Type):
    id: int
    currency: str
    mts_create: int
    offer_id: int
    amount: float
    rate: float
    period: int


@dataclass
class OrderTrade(_Type):
    id: int
    symbol: str
    mts_create: int
    order_id: int
    exec_amount: float
    exec_price: float
    maker: int
    fee: float
    fee_currency: str
    cid: int


@dataclass
class Ledger(_Type):
    id: int
    currency: str
    mts: int
    amount: float
    balance: float
    description: str


@dataclass
class FundingOffer(_Type):
    id: int
    symbol: str
    mts_create: int
    mts_update: int
    amount: float
    amount_orig: float
    offer_type: str
    flags: int
    offer_status: str
    rate: float
    period: int
    notify: int
    hidden: int
    renew: int


@dataclass
class FundingCredit(_Type):
    id: int
    symbol: str
    side: int
    mts_create: int
    mts_update: int
    amount: float
    flags: int
    status: str
    rate_type: str
    rate: float
    period: int
    mts_opening: int
    mts_last_payout: int
    notify: int
    hidden: int
    renew: int
    no_close: int
    position_pair: str


@dataclass
class FundingLoan(_Type):
    id: int
    symbol: str
    side: int
    mts_create: int
    mts_update: int
    amount: float
    flags: int
    status: str
    rate_type: str
    rate: float
    period: int
    mts_opening: int
    mts_last_payout: int
    notify: int
    hidden: int
    renew: int
    no_close: int


@dataclass
class FundingAutoRenew(_Type):
    currency: str
    period: int
    rate: float
    threshold: float


@dataclass()
class FundingInfo(_Type):
    symbol: str
    yield_loan: float
    yield_lend: float
    duration_loan: float
    duration_lend: float


@dataclass
class Wallet(_Type):
    wallet_type: str
    currency: str
    balance: float
    unsettled_interest: float
    available_balance: float
    last_change: str
    trade_details: Dict[str, Any]


@dataclass
class Transfer(_Type):
    mts: int
    wallet_from: str
    wallet_to: str
    currency: str
    currency_to: str
    amount: int


@dataclass
class Withdrawal(_Type):
    withdrawal_id: int
    method: str
    payment_id: str
    wallet: str
    amount: float
    withdrawal_fee: float


@dataclass
class DepositAddress(_Type):
    method: str
    currency_code: str
    address: str
    pool_address: str


@dataclass
class LightningNetworkInvoice(_Type):
    invoice_hash: str
    invoice: str
    amount: str


@dataclass
class Movement(_Type):
    id: str
    currency: str
    currency_name: str
    mts_start: int
    mts_update: int
    status: str
    amount: int
    fees: int
    destination_address: str
    transaction_id: str
    withdraw_transaction_note: str


@dataclass
class SymbolMarginInfo(_Type):
    symbol: str
    tradable_balance: float
    gross_balance: float
    buy: float
    sell: float


@dataclass
class BaseMarginInfo(_Type):
    user_pl: float
    user_swaps: float
    margin_balance: float
    margin_net: float
    margin_min: float


@dataclass
class PositionClaim(_Type):
    symbol: str
    position_status: str
    amount: float
    base_price: float
    margin_funding: float
    margin_funding_type: int
    position_id: int
    mts_create: int
    mts_update: int
    pos_type: int
    collateral: str
    min_collateral: str
    meta: Dict[str, Any]


@dataclass
class PositionIncreaseInfo(_Type):
    max_pos: int
    current_pos: float
    base_currency_balance: float
    tradable_balance_quote_currency: float
    tradable_balance_quote_total: float
    tradable_balance_base_currency: float
    tradable_balance_base_total: float
    funding_avail: float
    funding_value: float
    funding_required: float
    funding_value_currency: str
    funding_required_currency: str


@dataclass
class PositionIncrease(_Type):
    symbol: str
    amount: float
    base_price: float


@dataclass
class PositionHistory(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    funding: float
    funding_type: int
    position_id: int
    mts_create: int
    mts_update: int


@dataclass
class PositionSnapshot(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    funding: float
    funding_type: int
    position_id: int
    mts_create: int
    mts_update: int


@dataclass
class PositionAudit(_Type):
    symbol: str
    status: str
    amount: float
    base_price: float
    funding: float
    funding_type: int
    position_id: int
    mts_create: int
    mts_update: int
    type: int
    collateral: float
    collateral_min: float
    meta: Dict[str, Any]


@dataclass
class DerivativePositionCollateral(_Type):
    status: int


@dataclass
class DerivativePositionCollateralLimits(_Type):
    min_collateral: float
    max_collateral: float


@dataclass
class BalanceInfo(_Type):
    aum: float
    aum_net: float


# endregion

# region Dataclass definitions for types of merchant use


@compose(dataclass, partial)
class InvoiceSubmission(_Type):
    id: str
    t: int
    type: Literal["ECOMMERCE", "POS"]
    duration: int
    amount: float
    currency: str
    order_id: str
    pay_currencies: List[str]
    webhook: str
    redirect_url: str
    status: Literal["CREATED", "PENDING", "COMPLETED", "EXPIRED"]
    customer_info: "CustomerInfo"
    invoices: List["Invoice"]
    payment: "Payment"
    additional_payments: List["Payment"]
    merchant_name: str

    @classmethod
    def parse(cls, data: Dict[str, Any]) -> "InvoiceSubmission":
        if "customer_info" in data and data["customer_info"] is not None:
            data["customer_info"] = InvoiceSubmission.CustomerInfo(
                **data["customer_info"]
            )

        for index, invoice in enumerate(data["invoices"]):
            data["invoices"][index] = InvoiceSubmission.Invoice(**invoice)

        if "payment" in data and data["payment"] is not None:
            data["payment"] = InvoiceSubmission.Payment(**data["payment"])

        if "additional_payments" in data and data["additional_payments"] is not None:
            for index, additional_payment in enumerate(data["additional_payments"]):
                data["additional_payments"][index] = InvoiceSubmission.Payment(
                    **additional_payment
                )

        return InvoiceSubmission(**data)

    @compose(dataclass, partial)
    class CustomerInfo:
        nationality: str
        resid_country: str
        resid_state: str
        resid_city: str
        resid_zip_code: str
        resid_street: str
        resid_building_no: str
        full_name: str
        email: str
        tos_accepted: bool

    @compose(dataclass, partial)
    class Invoice:
        amount: float
        currency: str
        pay_currency: str
        pool_currency: str
        address: str
        ext: Dict[str, Any]

    @compose(dataclass, partial)
    class Payment:
        txid: str
        amount: float
        currency: str
        method: str
        status: Literal["CREATED", "COMPLETED", "PROCESSING"]
        confirmations: int
        created_at: str
        updated_at: str
        deposit_id: int
        ledger_id: int
        force_completed: bool
        amount_diff: str


@dataclass
class InvoicePage(_Type):
    page: int
    page_size: int
    sort: Literal["asc", "desc"]
    sort_field: Literal["t", "amount", "status"]
    total_pages: int
    total_items: int
    items: List[InvoiceSubmission]

    @classmethod
    def parse(cls, data: Dict[str, Any]) -> "InvoicePage":
        for index, item in enumerate(data["items"]):
            data["items"][index] = InvoiceSubmission.parse(item)

        return InvoicePage(**data)


@dataclass
class InvoiceStats(_Type):
    time: str
    count: float


@dataclass
class CurrencyConversion(_Type):
    base_ccy: str
    convert_ccy: str
    created: int


@dataclass
class MerchantDeposit(_Type):
    id: int
    invoice_id: Optional[str]
    order_id: Optional[str]
    type: Literal["ledger", "deposit"]
    amount: float
    t: int
    txid: str
    currency: str
    method: str
    pay_method: str


@dataclass
class MerchantUnlinkedDeposit(_Type):
    id: int
    method: str
    currency: str
    created_at: int
    updated_at: int
    amount: float
    fee: float
    txid: str
    address: str
    payment_id: Optional[int]
    status: str
    note: Optional[str]


# endregion
