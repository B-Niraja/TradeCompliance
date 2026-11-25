import csv

# Models


class Trade:
    def __init__(
        self,
        portfolio_id,
        security_id,
        action,
        quantity,
        price,
        security_type,
    ):
        self.portfolio_id = portfolio_id
        self.security_id = security_id
        self.action = action
        self.quantity = quantity
        self.price = price
        self.security_type = security_type


class Holding:
    def __init__(self, security_id, quantity, market_price):
        self.security_id = security_id
        self.quantity = quantity
        self.market_price = market_price


class Portfolio:
    def __init__(
        self,
        portfolio_id,
        cash_balance,
        restricted_securities,
        max_position_pct,
        current_holdings,
    ):
        self.portfolio_id = portfolio_id
        self.cash_balance = cash_balance
        self.restricted_securities = restricted_securities
        self.max_position_pct = max_position_pct
        self.current_holdings = current_holdings


def get_holding(portfolio, security_id):
    for holding in portfolio.current_holdings:
        if holding.security_id == security_id:
            return holding
    return None

# Step 1 - Validate

def validate_trade(trade):

    if trade.quantity <= 0:
        return "Rejected", "Invalid trade data."

    if trade.price <= 0:
        return "Rejected", "Invalid trade data."

    if trade.action not in ("Buy", "Sell"):
        return "Rejected", "Invalid trade data."

    return None

# Step 2 - Restricted Security Check

def check_restricted_security(trade, portfolio):

    if trade.security_id in portfolio.restricted_securities:
        return (
            "Rejected",
            "Security is restricted for this portfolio."
        )

    return None

# Step 3 - Sell Check

def check_sell_quantity(trade, portfolio):

    if trade.action != "Sell":
        return None

    holding = get_holding(portfolio, trade.security_id)

    available_quantity = (
        holding.quantity
        if holding
        else 0
    )

    if available_quantity < trade.quantity:
        return (
            "Rejected",
            "Insufficient holdings to sell."
        )

    return (
        "Approved",
        "Trade passed all checks."
    )

# Step 4 - Buy Affordability Check

def check_buy_affordability(trade, portfolio):

    if trade.action != "Buy":
        return None

    trade_cost = trade.quantity * trade.price

    if trade_cost > portfolio.cash_balance:
        return (
            "Rejected",
            "Insufficient cash for this buy order."
        )

    return None

# Step 5 - Position Concentration Check

def check_concentration(trade, portfolio):

    if trade.action != "Buy":
        return None

    holding = get_holding(portfolio, trade.security_id)

    trade_cost = trade.quantity * trade.price

    existing_quantity = (
        holding.quantity
        if holding
        else 0
    )

    post_trade_cash = portfolio.cash_balance - trade_cost

    post_trade_quantity = (
        existing_quantity + trade.quantity
    )

    post_trade_security_value = (
        post_trade_quantity * trade.price
    )

    value_of_other_holdings = 0

    for current_holding in portfolio.current_holdings:

        if current_holding.security_id == trade.security_id:
            continue

        value_of_other_holdings += (
            current_holding.quantity
            * current_holding.market_price
        )

    total_portfolio_value_after = (
        post_trade_cash
        + post_trade_security_value
        + value_of_other_holdings
    )

    position_pct = (
        post_trade_security_value
        / total_portfolio_value_after
    )

    if position_pct > portfolio.max_position_pct:
        return (
            "Needs Manual Sign-off",
            "Exceeds maximum position concentration — requires approval."
        )

    return None

# Main Compliance Engine

def check_trade(trade, portfolio):

    result = validate_trade(trade)
    if result:
        return result

    result = check_restricted_security(
        trade,
        portfolio
    )
    if result:
        return result

    result = check_sell_quantity(
        trade,
        portfolio
    )
    if result:
        return result

    result = check_buy_affordability(
        trade,
        portfolio
    )
    if result:
        return result

    result = check_concentration(
        trade,
        portfolio
    )
    if result:
        return result

    return (
        "Approved",
        "Trade passed all checks."
    )

# Portfolio Reference Data

portfolios = {

    "POR001": Portfolio(
        "POR001",
        25000,
        ["XYZCORP"],
        0.30,
        [
            Holding("AAPL", 50, 145),
            Holding("TCS", 50, 300),
            Holding("INFY", 10, 1400),
        ]
    ),

    "POR002": Portfolio(
        "POR002",
        15000,
        [],
        0.40,
        [
            Holding("GOOGL", 5, 2000),
        ]
    ),

    "POR003": Portfolio(
        "POR003",
        100000,
        ["BADCO"],
        0.35,
        [
            Holding("RELIANCE", 30, 2400),
            Holding("TCS", 20, 300),
        ]
    ),

    "POR004": Portfolio(
        "POR004",
        50000,
        [],
        0.20,
        []
    ),

    "POR005": Portfolio(
        "POR005",
        5000,
        ["PENNY1"],
        0.25,
        []
    )
}

# Read Trades CSV

results = []

with open("trades_test.csv", "r") as csv_file:

    reader = csv.DictReader(csv_file)

    for row in reader:

        trade = Trade(
            row["portfolio_id"],
            row["security_id"],
            row["action"],
            float(row["quantity"]),
            float(row["price"]),
            row["security_type"]
        )

        portfolio = portfolios.get(
            trade.portfolio_id
        )

        if portfolio is None:

            decision = "Rejected"
            reason = "Portfolio not found."

        else:

            decision, reason = check_trade(
                trade,
                portfolio
            )

        results.append(
            {
                "portfolio_id": trade.portfolio_id,
                "security_id": trade.security_id,
                "action": trade.action,
                "decision": decision,
                "reason": reason,
            }
        )

# Write Results CSV

with open(
    "output.csv",
    "w",
    newline=""
) as output_file:

    writer = csv.DictWriter(
        output_file,
        fieldnames=[
            "portfolio_id",
            "security_id",
            "action",
            "decision",
            "reason",
        ]
    )

    writer.writeheader()
    writer.writerows(results)

print("output.csv generated successfully.")