from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Propertyvaluation(models.TransientModel):
    _name = 'property.valuation'
    _description = 'Property valuation'

    Property_value_id = fields.Many2one('real.estate', string='Property Name')
    bedrooms = fields.Integer(related='Property_value_id.bedrooms', tracking=True, readonly=True)
    floors = fields.Char(related='Property_value_id.floors', tracking=True, readonly=True)
    deed_number = fields.Text(related='Property_value_id.deed_number', tracking=True, readonly=True)
    garden_area = fields.Integer(related='Property_value_id.garden_area', tracking=True, readonly=True)
    living_area = fields.Integer(related='Property_value_id.living_area', string="Living Area(sqm)", tracking=True,
                                 readonly=True)
    garden = fields.Boolean(related='Property_value_id.garden', string='Garden', readonly=True)
    garage = fields.Boolean(related='Property_value_id.garage', string='Garage', readonly=True)
    total_area = fields.Integer(related='Property_value_id.total_area', string="Total Area(sqm)", tracking=True,
                                readonly=True)

    property_type_id = fields.Many2one(related='Property_value_id.property_type_id', tracking=True,
                                       ondelete='cascade', readonly=True)
    property_type = fields.Many2many(related='Property_value_id.property_type', tracking=True,
                                     ondelete='cascade', readonly=True)

    building_type = fields.Selection(related='Property_value_id.building_type', readonly=True)
    property_area_type = fields.Selection(related='Property_value_id.property_area_type', readonly=True)

    expected_price = fields.Float(related='Property_value_id.expected_price', tracking=True, readonly=True)
    tag_ids = fields.Many2many(related='Property_value_id.tag_ids', tracking=True, ondelete='cascade')
    evaluate_price = fields.Float(string="Valuated Price()", readonly=True, tracking=True)
    # user enters price for automatic calculation of property price
    user_entered_price = fields.Float(string='User Entered Price')

    '''Price Evaluation in AFG Aghani currency  Code'''

    # def action_valuate_property(self):
    #     per_sqm_price = 6460
    #     if self.living_area:
    #         self.evaluate_price = per_sqm_price * self.living_area
    #
    #     else:
    #         self.evaluate_price = per_sqm_price * self.total_area
    #
    #     return {
    #         'name': _('Price Evaluation for Specific Property Based on Living area Size'),
    #         'view_mode': 'form',
    #         'type': 'ir.actions.act_window',
    #         'res_id': self.id,
    #         'res_model': 'property.valuation',
    #         'target': 'new',
    #         'effect': {
    #             'fadeout': 'medium',
    #             'message': f"{self.evaluate_price} is Evaluated Price for \n this Property based on Living Area!!! ",
    #             'type': 'rainbow_man',
    #         }
    #     }

    ''' my custom function Price Evaluation in AFG Aghani currency  Code '''

    @api.model
    def get_per_sqm_price(self):
        return float(self.env['ir.config_parameter'].sudo().get_param('property_valuation.per_sqm_price', default=6000))

    def action_valuate_property(self):
        per_sqm_price = self.get_per_sqm_price()

        # Use user_entered_price if available, else use default calculation
        if self.user_entered_price:
            self.evaluate_price = self.user_entered_price * self.total_area
        elif self.living_area:
            self.evaluate_price = per_sqm_price * self.living_area
        else:
            self.evaluate_price = per_sqm_price * self.total_area

        return {
            'name': _('Price Evaluation for Specific Property Based on Living area Size'),
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'res_model': 'property.valuation',
            'target': 'new',
            'effect': {
                'fadeout': 'medium',
                'message': f"{self.evaluate_price} is Evaluated Price for \n this Property based on Living Area!!! ",
                'type': 'rainbow_man',
            }
        }

    '''Price Evaluation in USD Dollor $ - Code'''

    @api.model
    def get_per_sqm_price_dollor(self):
        return float(self.env['ir.config_parameter'].sudo().get_param('property_valuation.per_sqm_price', default=88))

    def action_valuate_property_dollor(self):
        per_sqm_price = self.get_per_sqm_price_dollor()

        # Use user_entered_price if available, else use default calculation
        if self.user_entered_price:
            self.evaluate_price = self.user_entered_price * self.total_area
        elif self.living_area:
            self.evaluate_price = per_sqm_price * self.living_area
        else:
            self.evaluate_price = per_sqm_price * self.total_area

        return {
            'name': _('Price Evaluation for Specific Property Based on Living area Size'),
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'res_model': 'property.valuation',
            'target': 'new',
            'effect': {
                'fadeout': 'medium',
                'message': f"\n\n\n {self.evaluate_price} $ is Evaluated Price for \n this Property based on Living "
                           f"Area!!! ",
                'type': 'rainbow_man',
            }
        }

    def action_close(self):
        return True
