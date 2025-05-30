from odoo import api, fields, models, _, tools
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class PmsContract(models.Model):
    _name = "pms.contract"
    _description = "Contract information"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "property_id"

    name = fields.Char('Contract Reference', required=True)
    active = fields.Boolean(default=True)

    date_start = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='End Date', tracking=True, compute="_close_contract", store=True, readonly=False,
                           help="End date of the contract (if it's a fixed-term contract).")

    notes = fields.Html('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Running'),
        ('sent_to_finance', 'Sent to Finance'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', copy=False,
        tracking=True, help='Status of the contract', default='draft')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')
    ], string='Kanban State', default='normal', tracking=True, copy=False)
    contract_type_id = fields.Many2one('pms.contract.type', "Contract Type", ondelete='restrict')

    contract_status = fields.Selection(
        [('new', 'New'), ('draft', 'Draft'), ('running', 'Running'), ('close', 'Closed'),
         ('sent_to_finance', 'Sent to Finance')],
        string="State", copy=False, store=True, default='new')

    file_name = fields.Char('Invoice Inquiry Name', store=True)
    contract_file = fields.Binary(
        attachment=True,
        string="Contract File",
        copy=False,
    )

    meeting_address = fields.Char(string="Meeting Address")
    property_id = fields.Many2one('real.estate', required=True, ondelete='restrict')
    bedrooms = fields.Integer(related='property_id.bedrooms', tracking=True, readonly=True)
    deed_number = fields.Text(related='property_id.deed_number', tracking=True, readonly=True)
    garden_area = fields.Integer(related='property_id.garden_area', tracking=True, readonly=True)
    property_state = fields.Selection(related='property_id.state', tracking=True, readonly=True)
    living_area = fields.Integer(related='property_id.living_area', string="Living Area(sqm)", tracking=True,
                                 readonly=True)
    property_area_type = fields.Selection(related='property_id.property_area_type', string="Property Area Type",
                                          readonly=True)
    garden = fields.Boolean(related='property_id.garden', string='Garden', readonly=True)
    garage = fields.Boolean(related='property_id.garage', string='Garage', readonly=True)
    total_area = fields.Integer(related='property_id.total_area', string="Total Area(sqm)", tracking=True,
                                readonly=True)
    property_type = fields.Many2many(related='property_id.property_type', tracking=True,
                                     ondelete='restrict', readonly=True)
    expected_price = fields.Float(related='property_id.expected_price', tracking=True, readonly=True)
    tag_ids = fields.Selection(related='property_id.tag_id', tracking=True, ondelete='cascade')
    # add column for property monthly rent payment
    monthly_rent = fields.Float(string="Bid Price", store=True, readonly=False,
                                help="this could refer to the price an offeror is willing to pay")
    ''' Winner info '''
    winner_id = fields.Many2one('res.partner', string="Winner")

    ''' displaying all offers'''
    offer_id = fields.One2many('estate.property.offer', 'offer_property_id', ondelete='cascade', store=True)

    ''' displaying Agent Teams '''
    agent_team_id = fields.Many2one('agent.team', string='Agent Team', store=True, readonly=False, ondelete='restrict')

    ''' Displaying winner or Tenant Payment info '''
    tenant_payment_ids = fields.One2many('tenant.payment', 'contract_id', string="Tenants")
    '''' Displaying currency '''
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.ref('base.AFN').id)
    currency_symbol = fields.Char(string="Currency Symbol", compute="_compute_currency_symbol", readonly=True)

    def _compute_currency_symbol(self):
        for record in self:
            record.currency_symbol = record.currency_id.symbol or ''

    selling_price = fields.Float(string="Contracted Price", readonly=True, tracking=True)
    best_offer = fields.Float(compute='_compute_best_offer', string="Best Offered", readonly=True, default=0.0,
                              store=True)
    # New field to store the name of the agent who brought the best offer
    best_offer_agent_id = fields.Many2one('res.partner', ondelete='restrict', string='Best Offer Agent',
                                          compute='_compute_best_offer_agent',
                                          store=True)
    offer_ids = fields.One2many('estate.property.offer', 'offer_property_id', string="Offers")

    '''below field For smart button '''
    count_offer = fields.Integer(compute="_compute_count_offer", store=True)

    #  FOR PRINTING FRONT VALUE IN XML REPORT
    def get_contract_state_label(self):
        label_mapping = {
            'draft': 'Draft',
            'open': 'Running',
            'sent_to_finance': 'Sent to Finance',
            'close': 'Closed',
            'cancel': 'Cancelled',
        }
        return label_mapping.get(self.state, '')

    # account.move fields
    move_ids = fields.One2many('account.move', 'contract_id', string="Invoices")
    # Computed field to show the payment status of the related invoice
    payment_state = fields.Selection(
        related="move_ids.payment_state", string="Payment State",
        compute="_compute_payment_state", store=True, readonly=True
    )

    # Close contract
    def action_close_contract(self):
        for con in self:
            if con.state:
                con.write({'state': 'close'})

    # Cancel contract
    def action_cancel_contract(self):
        for con in self:
            if con.state:
                con.write({'state': 'cancel'})

    # Reset State
    def action_reset_state(self):
        for rec in self:
            if self.state not in ['cancel', 'sent_to_finance']:
                raise ValidationError(_("RESET is Possible only in Cancel or Sent To Finance State"))
            else:
                self.state = 'draft'
        return True

    @api.depends('move_ids.payment_state')
    def _compute_payment_state(self):
        for contract in self:
            if contract.move_ids:
                latest_invoice = contract.move_ids.sorted(key=lambda x: x.invoice_date, reverse=True)[:1]
                contract.payment_state = latest_invoice.payment_state
            else:
                contract.payment_state = 'unpaid'  # Default to 'unpaid' if no invoices exist

    # expand_states for state in search view
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    # def action_view_invoices(self):
    #     action = self.env.ref('account.action_move_out_invoice_type').read()[]
    #     action['domain'] = [('contract_id', 'in', self.ids)]
    #     return action

    def action_view_invoices(self):
        domain = [('contract_id', '=', self.id)]  # Filter by the current contract ID
        # domain = [('contract_id', '=', self.id), ('payment_state', 'in', ['draft','paid', 'partial'])]

        return {
            'name': _('View Invoice'),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'res_model': 'account.move',
            'target': 'current',
            'context': {'default_contract_id': self.id},
        }

    # compute or show best offer
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for contract in self:
            max_price = max(contract.offer_ids.mapped('price')) if contract.offer_ids else 0.0
            contract.best_offer = max_price

    # display best offer Agent
    @api.depends('offer_ids.price')
    def _compute_best_offer_agent(self):
        for contract in self:
            best_offer = contract.offer_ids.sorted(key=lambda r: r.price, reverse=True)[:1]
            if best_offer:
                contract.best_offer_agent_id = best_offer[0].partner_id.id
            else:
                contract.best_offer_agent_id = False

    @api.depends('offer_id.partner_id')
    def _compute_count_offer(self):
        for rec in self:
            rec.count_offer = self.env['estate.property.offer'].search_count([('offer_property_id', '=', rec.id)])

    # return into offers
    def action_count_offer(self):
        return {
            'name': _('Total Offered'),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('offer_property_id', '=', self.id)],
            'res_model': 'estate.property.offer',
            'target': 'current',
            'context': {'default_offer_property_id': self.id},
        }

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(_("WARNING....\n Deletion is possible only in Draft or Cancelled State"))
            return super(PmsContract, self).unlink()

    # set default journals of a property into assigned users
    def _default_journal(self):
        if self.property_id.property_area_type == 'ground':
            return self.env["account.journal"].search([("code", "=", "13107")], limit=1).id
        else:
            return self.env["account.journal"].search([("code", "=", "13105")], limit=1).id

    # send contract information into finance department for receiving revenue
    def action_to_finance(self):
        for contract in self:
            # Check if the contract has already been sent to finance
            if contract.state == 'sent_to_finance':
                raise UserError("This contract has already been sent to Finance and cannot be sent again.")
            # Check if contract is in a valid state (e.g., draft or open)
            if contract.state in ['close', 'draft', 'cancel']:
                raise ValidationError(
                    "This contract cannot be sent to finance. It must be in 'Running' or 'Open' state."
                )

            # Get the necessary data from the contract
            contract_name = contract.name
            property_name = contract.property_id.name
            winner_name = contract.winner_id.name if contract.winner_id else 'No Winner'
            date_start = contract.date_start
            date_end = contract.date_end
            amount = contract.monthly_rent  # Assuming this is the amount to be invoiced
            contracted_price = contract.selling_price  # Use contracted price
            # assign auto journal for finance department
            journal = self._default_journal()
            partner = contract.winner_id  # winner_id is the partner\
            # father_name = contract.winner_id.father_name

            # Create the draft account.move
            move_vals = {
                'move_type': 'out_invoice',  # 'out_invoice' for customer invoices
                'partner_id': contract.winner_id.id if contract.winner_id else False,
                'invoice_date': date_start,
                'invoice_date_due': date_end,
                'ref': contract_name,
                'contract_id': contract.id,  # Link the invoice to the contract
                # comment for get auto journal for property revenue
                'journal_id': journal,  # Link the invoice to the contract for selecting auto journal
                # 'father_name': father_name,
                'line_ids': [
                    (0, 0, {
                        # Concatenate property name Default description for contract income
                        'name': f"{property_name} Property Contract Income",
                        # The price_unit
                        'price_unit': contracted_price,
                        'quantity': 1,  # Quantity
                        'partner_id': contract.winner_id.id if contract.winner_id else False,
                    }),
                ],
            }

            # Create the move
            move = self.env['account.move'].create(move_vals)
            # After sending to finance, update the state to 'sent_to_finance'
            contract.write({'state': 'sent_to_finance'})

            # If the contract has a file, create an attachment for the invoice
            if contract.contract_file:
                attachment_vals = {
                    'name': contract.file_name or f"{contract.property_id.name} Property contract File",
                    'type': 'binary',
                    'datas': contract.contract_file,
                    'res_model': 'account.move',
                    'res_id': move.id,
                    'mimetype': 'application/pdf',
                }

                # Create the attachment
                attachment = self.env['ir.attachment'].create(attachment_vals)
                move.write({
                    'attachment_ids': [(4, attachment.id)]
                })

            # Send a confirmation message to the contract's chatter
            contract.message_post(
                body=f"{contract.property_id.name} Contract information has been successfully sent to the Finance department.",
                subject="Contract Sent to Finance",
                message_type="notification",
                subtype_id=self.env.ref('mail.mt_note').id,  # Default subtype for chatter messages
            )

            contract.message_post(
                body=f"{contract.property_id.name} Contract information has been successfully sent to the Finance department.",
                subject="Contract Sent to Finance",
                message_type="notification",
                subtype_id=self.env.ref('mail.mt_note').id,  # Default subtype for chatter messages
            )

            # Post a confirmation message to the invoice's (account.move) chatter (to inform finance)
            move.message_post(
                body=f"Invoice has been created for the contract: {contract.name}. "
                     f"Property name is: {contract.property_id.name}, "
                     f"Contracted Price is: {contract.selling_price}, "
                     f"Contract State: {contract.state}. Please review the details.",
                subject="Invoice Created for Contract",
                message_type="notification",
                subtype_id=self.env.ref('mail.mt_note').id,  # Default subtype for chatter messages
            )

        return True


    # 1st way for check maximum best offer give by Clients(Create Button Not Work When it apply)
    # @api.depends('offer_ids.price')
    # def _compute_best_offer(self):
    #     for rec in self:
    #         self.best_offer = max(rec.offer_ids.mapped('price'))

    # 2nd way for check maximum best offer give by Clients
    # @api.depends('offer_ids.price')
    # def _compute_best_offer(self):
    #     com = 0.0
    #     for rec in self.offer_ids:
    #         if rec.price > com:
    #             com = rec.price
    #     self.best_offer = com
