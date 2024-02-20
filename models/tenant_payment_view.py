from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from datetime import date


class TenantPayment(models.Model):
    _name = "tenant.payment"
    _description = "Tenant Payment"
    _rec_name = "months"

    tenant_id = fields.Many2one('res.partner', string="Tenant", required=True)
    tenant_phone_number = fields.Char(string="Phone Number", size=20)
    email_id = fields.Char(string="Email")
    property_id = fields.Many2one('real.estate', string="Property", required=True)
    payment_date = fields.Date(string="Payment Date", default=fields.Date.today())
    amount = fields.Float(string="Amount")
    monthly_rent = fields.Float(string="Monthly Rent", related="property_id.monthly_rent", store=True, readonly=True)
    is_paid = fields.Boolean(string="Is Paid", compute="_compute_is_paid", store=True, readonly=False)
    months = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December'),
    ], string='Paid Months')
    total_rent_received = fields.Float(string="Total Rent Received", compute="_compute_total_rent_received", store=True)
    # months_paid = fields.Integer(string="Months Paid", compute="_compute_months_paid", store=True)
    months_paid = fields.Integer(string="Months Paid", compute="_compute_months_paid", store=True)
    # showing the remaining amount in days
    remaining_amount = fields.Float(string="Remaining Amount", compute="_compute_remaining_amount", store=True)

    total_rent_received_sum = fields.Float(string="Total Rent Received (Sum)",
                                           compute="_compute_total_rent_received_sum", store=True)
    account_number = fields.Char(string="Account Number", default=3310209213321)
    OwaisBank = fields.Char(string="Owais Bank")
    description = fields.Text(string="Description")

    # Define a Many2many field to store attachments/files for each Tenant Payment
    tenant_attachments = fields.Many2many('ir.attachment', string='ضميمه اسناد',
                                          domain="[('res_model', '=', 'tenant.payment')]")

    @api.depends('payment_date')
    def _compute_is_paid(self):
        for payment in self:
            payment_date = fields.Date.from_string(payment.payment_date)
            current_date = fields.Date.today()
            payment.is_paid = payment_date.month == current_date.month and payment_date.year == current_date.year

    # checking which month rent is paid or which is not paid
    # @api.onchange('is_paid')
    # def onchange_is_paid(self):
    #     if self.is_paid:
    #         # If payment is made, set the current month as paid
    #         current_month = fields.Date.today().strftime('%B').lower()
    #         self.months = current_month
    #     else:
    #         # If payment is not made, clear the paid months
    #         self.months = False

    # check if the amount is Zero (0)
    @api.constrains('amount')
    def _check_amount(self):
        for payment in self:
            if payment.amount <= 0:
                raise ValidationError("WARNING....Amount Price Must be Positive Number & greater than 0 !!!🚫")

    # if amount is not zero
    @api.depends('amount')
    def _compute_is_paid(self):
        for record in self:
            record.is_paid = record.amount > 0

    @api.depends('amount', 'is_paid', 'monthly_rent', 'months_paid')
    def _compute_remaining_amount(self):
        for payment in self:
            remaining_amount = payment.amount - (payment.monthly_rent * payment.months_paid)
            remaining_days = remaining_amount / payment.monthly_rent * 30 if payment.monthly_rent > 0 else 0
            payment.remaining_amount = remaining_days

    @api.depends('amount', 'is_paid')
    def _compute_total_rent_received(self):
        for payment in self:
            if payment.is_paid:
                payment.total_rent_received = payment.amount
            else:
                payment.total_rent_received = 0.0

    @api.depends('total_rent_received')
    def _compute_total_rent_received_sum(self):
        for record in self:
            record.total_rent_received_sum = sum(
                payment.total_rent_received for payment in record.property_id.tenant_ids)

    @api.depends('amount', 'is_paid', 'monthly_rent')
    def _compute_months_paid(self):
        for payment in self:
            if payment.is_paid and payment.monthly_rent > 0:
                payment.months_paid = int(payment.total_rent_received / payment.monthly_rent)
            else:
                payment.months_paid = 0

    @api.depends('amount', 'is_paid')
    def _compute_is_paid(self):
        for payment in self:
            payment.is_paid = payment.amount > 0 and payment.total_rent_received >= payment.amount
