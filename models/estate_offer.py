from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = "price desc"
    _rec_name = 'property_id'
    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], string="State", copy=False,
                              store=True)
    offer_number = fields.Char(string="Offer Number", required=True)
    validity = fields.Integer(string="Validity", default=7)
    deadline = fields.Date(string="Date Deadline", compute='_compute_deadline', inverse='_inverse_deadline', store=True)
    '''Relational Fields'''
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    property_id = fields.Many2one('real.estate', ondelete='cascade')
    property_type_id = fields.Many2one('estate.property.type', string="Properties",
                                       related='property_id.property_type_id', store=True, ondelete='cascade')
    property_name = fields.Char(string="Property Name", related='property_id.name', store=True, readonly=True)

    ''' Contract Offers for property '''
    offer_property_id = fields.Many2one('pms.contract', string="Property", ondelete='cascade')

    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for rec in self:
            today = fields.Date.today()
            if rec.create_date:
                rec.deadline = today + timedelta(rec.validity)
            else:
                # rec.deadline = today + timedelta(days=7)
                self.write({'deadline': today + timedelta(rec.validity)})

    @api.depends('deadline')
    def _inverse_deadline(self):
        today = fields.Date.today()
        for rec in self:
            numday = rec.deadline - today
            rec.validity = numday.days

    def action_accept(self):
        for rec in self:
            accepted_offers = rec.offer_property_id.offer_id.filtered(lambda offer: offer.status == 'accepted')
            if accepted_offers:
                raise ValidationError("Sorry! It's not possible to accept multiple offers.")
            else:
                rec.status = 'accepted'
                rec.offer_property_id.contract_status = 'running'
                rec.offer_property_id.selling_price = rec.price
                rec.offer_property_id.winner_id = rec.partner_id.id
                rec.offer_property_id.state = 'open'  # Set contract state to 'running' or 'open' when offer is accepted
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Hooray! Your offer has been accepted!",
                'type': 'rainbow_man',
            }
        }

    def action_refused(self):
        for rec in self:
            self.status = 'refused'
            self.offer_property_id.contract_status = 'draft'
            self.offer_property_id.selling_price = 0
            self.offer_property_id.winner_id = False  # Set winner_id to False or None to clear it
            self.offer_property_id.state = 'draft'
        return {
            'effect': {
                'fadeout': 'fast',
                'message': "Oops!!!  Offer Rejected",
                'type': 'rainbow_man',
            }
        }

    @api.constrains('price')
    def check_offer_price(self):
        for rec in self:
            if rec.price < 0:
                raise ValidationError(_("Warning....\n Offered Price should Never Non Positive!!!!"))

    # Preventing delete action if offer status is accepted
    def unlink(self):
        for offer in self:
            if offer.status == 'accepted':
                raise ValidationError("Cannot delete an offer that has been accepted.")
        return super(EstatePropertyOffer, self).unlink()


