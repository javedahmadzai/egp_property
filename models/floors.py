from odoo import fields, models, api, _


class FloorMCIT(models.Model):
    _name = "floor.mcit.pms"
    _description = "This floor model is for MCIT Property Management System"

    name = fields.Char(String="Floor Name")
    details = fields.Html(string="Details")
    room_ids = fields.One2many('room.mcit.pms', 'floor_id', string="Room name")

    # Define a Many2many field for products
    product_ids = fields.Many2many('product.mcit.pms', string="Products")


class RoomMCIT(models.Model):
    _name = "room.mcit.pms"
    _description = "This room model is for MCIT Property " \
                   "Management System which will store the related floor rooms " \
                   "data"

    name = fields.Char(String="Room Name")
    details = fields.Text(string="Details")
    floor_id = fields.Many2one('floor.mcit.pms', string="Floor Name")

    # Define a Many2many field for products
    product_ids = fields.Many2many('product.mcit.pms', string="Products")
