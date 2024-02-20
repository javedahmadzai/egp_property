from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = "price desc"
    _rec_name = 'property_id'
    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], string="State", copy=False,
                              store=True)
    validity = fields.Integer(string="Validity", default=7)
    deadline = fields.Date(string="Date Deadline", compute='_compute_deadline', inverse='_inverse_deadline', store=True)
    '''Relational Fields'''
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    # email_id=fields.Many2one('res.partner',ondelete='cascade')
    property_id = fields.Many2one('real.estate', required=True, ondelete='cascade')
    property_type_id = fields.Many2one('estate.property.type', string="Properties",
                                       related='property_id.property_type_id', store=True, ondelete='cascade')

    # offer_agent_id = fields.Many2one('agent.view', string="Agent")

    ''' Offer Ghoshai Offer for property '''
    offer_property_id = fields.Many2one('pms.offerghoshai', string="Property", ondelete='cascade')

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
            checks = rec.property_id.offer_ids.mapped('status')
            if 'accepted' in checks:
                raise ValidationError("Sorry ! not Possible to Accept Multiple Offer🚫")
            else:
                self.status = 'accepted'
                self.property_id.selling_price = rec.price
                self.property_id.sale_buyer = rec.partner_id
                self.property_id.sale_buyer_email = rec.partner_id.email
                self.property_id.state = 'offer_accepted'
            if rec.price < (self.property_id.monthly_rent * 90) / 100:
                raise ValidationError(_("WARNING....\n Price Must be at Least 90% of Monthly Rent Price!!🚫"))
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "hooray!!! \n Your Offer has been Accepted  !",
                'type': 'rainbow_man',
            }
        }

    def action_refused(self):
        for rec in self:
            self.status = 'refused'
            self.property_id.selling_price = 0
            self.property_id.sale_buyer = False
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

    # @api.model
    # def create(self, vals):
    #     res = super(EstatePropertyOffer, self).create(vals)
    #     for rec in res.property_id.offer_ids:
    #         if vals.get('price') < rec.price:
    #             raise ValidationError(_("WARNING...\n Added Price must me Larger than Higher Offered Price🚫"))
    #     return res

    # Preventing delete action if offer status is accepted
    def unlink(self):
        for offer in self:
            if offer.status == 'accepted':
                raise ValidationError("Cannot delete an offer that has been accepted.")
        return super(EstatePropertyOffer, self).unlink()



