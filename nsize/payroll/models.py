from django.db import models

from sl_profile.models import Grid, Resident
from delivery.models import Garment, BodyPart


class GarmentDistribution(models.Model):
    garment = models.ForeignKey(Garment, on_delete=models.CASCADE)
    collaborator = models.ForeignKey(Resident, on_delete=models.CASCADE)
    percentage = models.PositiveSmallIntegerField()


class Transaction(models.Model):
    """
    A transaction, downloaded from the SL Transaction History
    https://accounts.secondlife.com/transaction_history/
    """
    ### SL Transaction Log Fields ###
    id = models.UUIDField(primary_key=True)
    type = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    debit = models.PositiveIntegerField()
    credit = models.PositiveIntegerField()
    time = models.DateTimeField()
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    end_balance = models.PositiveIntegerField()
    region = models.CharField(max_length=32)
    order_id = models.BigIntegerField(null=True)
    ### End SL Transaction Log Fields ###

    INCOME = 'I'
    EXPENSE = 'E'
    TRANSFER = 'T'
    CLASSIFICATION_CHOICES = (
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
        (TRANSFER, 'Transfer'),
    )
    classification = models.CharField(max_length=1, choices=CLASSIFICATION_CHOICES)

    # Income
    SALE = 'SaleI'
    RENT_INCOME = 'RentI'
    STIPEND = 'StipI'
    OTHER_INCOME = 'I'

    # Expenses
    TIER_PAYMENT = 'TierE'
    RENT_EXPENSE = 'RentE'
    UPLOAD_FEE = 'UpE'
    OTHER_EXPENSE = 'E'

    # Transfers
    DIVIDEND = 'Div'
    CAPITAL_INCREASE = 'CapI'
    CAPITAL_DECREASE = 'CapD'

    CATEGORY_CHOICES = (
        # Income
        (SALE, 'Sale'),
        (RENT_INCOME, 'Rental Income'),
        (STIPEND, 'Stipend'),
        (OTHER_INCOME, 'Other Income'),
        # Expenses
        (TIER_PAYMENT, 'Tier Payment'),
        (RENT_EXPENSE, 'Rental Expense'),
        (UPLOAD_FEE, 'Upload Fee'),
        (OTHER_EXPENSE, 'Other Expense'),
        # Transfers
        (DIVIDEND, 'Dividend'),
        (CAPITAL_INCREASE, 'Capital Increase'),
        (CAPITAL_DECREASE, 'Capital Decrease'),
    )
    category = models.CharField(max_length=5, choices=CATEGORY_CHOICES)

    grid = models.ForeignKey(Grid, on_delete=models.CASCADE)
    fiscal_day = models.DateField()

    class Meta:
        db_table = 'payroll_transaction_log'
        indexes = [
            models.Index(fields=['grid', 'fiscal_day', 'resident']),
        ]


class DayLedger(models.Model):
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE)
    fiscal_day = models.DateField()

    # Sales
    sale_count = models.PositiveIntegerField()
    sales_income = models.PositiveIntegerField()
    avg_sale_revenue = models.FloatField()
    budgeted_expense = models.IntegerField()
    withholding = models.PositiveIntegerField()
    total_profit = models.PositiveIntegerField()
    unique_seller_count = models.PositiveIntegerField()

    # Unpacks
    unpack_count = models.PositiveIntegerField()
    unique_outfit_count = models.PositiveIntegerField()

    # Dividends
    garment_count = models.PositiveIntegerField()
    dividend_per_garment = models.PositiveIntegerField()
    operator_dividend = models.PositiveIntegerField()

    # to date
    unique_outfits_to_date = models.PositiveIntegerField()
    garments_to_date = models.PositiveIntegerField()
    sales_to_date = models.PositiveIntegerField()
    creator_dividend_to_date = models.PositiveIntegerField()

    class Meta:
        unique_together = (("grid", "fiscal_day"),)


class MyDayLedger(DayLedger):
    """ Computed statistics for the logged in user """

    # My Sales
    my_sale_count = models.PositiveIntegerField(default=0)
    my_total_distribution = models.PositiveIntegerField(default=0)
    my_avg_distribution = models.FloatField(default=0)

    # My Unpacks
    my_total_unpack_count = models.PositiveIntegerField(default=0)
    # only count non-creator unpacks, and non-free unpacks, if data is available
    my_sales_unpack_count = models.PositiveIntegerField(default=0)
    my_unpack_sale_ratio = models.FloatField(default=0)

    # My Dividends
    my_garment_count = models.PositiveIntegerField(default=0)
    my_dividend = models.PositiveIntegerField(default=0)

    class Meta:
        managed = False


class MonthLedger(models.Model):
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE)
    first_day = models.DateField()
    last_day = models.DateField()

    # Income
    rent_income = models.PositiveIntegerField()
    stipend_income = models.PositiveIntegerField()
    other_income = models.PositiveIntegerField()
    total_income = models.PositiveIntegerField()

    # Expenses
    lindex_rate = models.PositiveIntegerField()
    server_expense_usd = models.DecimalField(max_digits=8, decimal_places=2)
    server_expense = models.PositiveIntegerField()
    tier_expense_usd = models.DecimalField(max_digits=8, decimal_places=2)
    tier_expense = models.PositiveIntegerField()
    rent_expense = models.PositiveIntegerField()
    upload_expense = models.PositiveIntegerField()
    other_expense = models.PositiveIntegerField()
    total_expense = models.PositiveIntegerField()

    # Budget
    last_month_budget = models.IntegerField()
    last_month_expense = models.IntegerField()
    last_month_shortfall = models.IntegerField()
    next_month_net_budget = models.IntegerField()
    next_month_gross_budget = models.IntegerField()
    days_in_next_month = models.PositiveSmallIntegerField()
    next_month_daily_budget = models.IntegerField()

    # Sales
    sale_count = models.PositiveIntegerField()
    sales_income = models.PositiveIntegerField()
    avg_sale_revenue = models.FloatField()
    unique_seller_count = models.PositiveIntegerField()

    # Unpacks
    unpack_count = models.PositiveIntegerField()
    unique_outfit_count = models.PositiveIntegerField()

    # Dividends
    total_dividend = models.IntegerField()
    dividend_per_garment = models.PositiveIntegerField()

    class Meta:
        unique_together = (("grid", "first_day"),)


class MyMonthLedger(MonthLedger):
    """ Computed statistics for the logged in user """

    # My Sales
    my_sale_count = models.PositiveIntegerField(default=0)
    my_total_distribution = models.PositiveIntegerField(default=0)
    my_avg_distribution = models.FloatField(default=0)

    # My Unpacks
    my_total_unpack_count = models.PositiveIntegerField(default=0)
    # only count non-creator unpacks, and non-free unpacks, if data is available
    my_sales_unpack_count = models.PositiveIntegerField(default=0)
    my_unpack_sale_ratio = models.FloatField(default=0)

    # My Dividends
    my_dividend = models.PositiveIntegerField(default=0)

    class Meta:
        managed = False
