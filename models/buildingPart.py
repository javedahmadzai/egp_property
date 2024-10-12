from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class BuildingPart(models.Model):
    _name = "building.part"
    _description = "This is for MCIT Property"
    _rec_name = 'complete_name'
    # _parent_store = True

    name = fields.Char(String="Part Name", required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True, recursive=True)
    details = fields.Text(string="Details")
    parent_id = fields.Many2one('building.part', string="Parent Part", ondelete='cascade')
    # child_ids = fields.One2many('building.part', 'parent_id', string='Child Part')
    # parent_path = fields.Char(index=True, unaccent=False)
    # master_part_id = fields.Many2one(
    #     'building.part', 'Master Part', compute='_compute_master_department_id', store=True)
    property_id = fields.Many2one('real.estate', required=True, ondelete='cascade')
    part_type = fields.Selection([
        ('floor', 'Floor'),
        ('room', 'Room'),
        ('hall', 'Hall'),
        ('kitchen', 'Kitchen'),
        ('toilet', 'Bathroom')
    ], required=True)

    @api.depends_context('hierarchical_naming')
    def _compute_display_name(self):
        if self.env.context.get('hierarchical_naming', True):
            return super()._compute_display_name()
        for record in self:
            record.display_name = record.name

    @api.model
    def name_create(self, name):
        record = self.create({'name': name})
        return record.id, record.display_name

    @api.depends('name', 'parent_id.complete_name', 'part_type', 'details')
    def _compute_complete_name(self):
        for part in self:
            if part.parent_id:
                parent_name = part.parent_id.complete_name or ''
                if part.name:
                    if part.details:
                        part.complete_name = '%s / %s - %s' % (parent_name, part.name, part.details)
                    else:
                        part.complete_name = '%s / %s' % (parent_name, part.name)
                else:
                    part.complete_name = parent_name
            else:
                part.complete_name = part.name

    @api.model
    def create(self, vals):
        if 'name' in vals and 'parent_id' not in vals:
            vals['parent_id'] = self._get_parent_id_from_name(vals['name'])
        return super(BuildingPart, self).create(vals)

    def write(self, vals):
        if 'name' in vals and 'parent_id' not in vals:
            vals['parent_id'] = self._get_parent_id_from_name(vals['name'])
        return super(BuildingPart, self).write(vals)

    def _get_parent_id_from_name(self, name):
        parent = self.search([('name', '=', name)], limit=1)
        return parent.id if parent else False

    # @api.depends('name', 'parent_id.complete_name', 'part_type', 'details')
    # def _compute_complete_name(self):
    #     for part in self:
    #         if part.parent_id:
    #             parent_name = part.parent_id.complete_name or ''
    #             if part.details:
    #                 part.complete_name = '%s / %s - %s' % (parent_name, part.name, part.details)
    #             else:
    #                 part.complete_name = '%s / %s' % (parent_name, part.name)
    #         else:
    #             part.complete_name = part.name
    # @api.depends('name', 'parent_id.complete_name', 'details', 'part_type')
    # def _compute_complete_name(self):
    #     for department in self:
    #         if department.part_type:
    #             parent_name = department.part_type or ''
    #             if department.details:
    #                 department.complete_name = '%s / %s - %s' % (parent_name, department.name, department.details)
    #             else:
    #                 department.complete_name = '%s / %s' % (parent_name, department.name)
    #         else:
    #             department.complete_name = department.name

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive part.'))

    def get_children_department_ids(self):
        return self.env['building.part'].search([('id', 'child_of', self.ids)])

    def get_department_hierarchy(self):
        if not self:
            return {}

        hierarchy = {
            'parent': {
                'id': self.parent_id.id,
                'name': self.parent_id.name,
                # 'employees': self.parent_id.total_employee,
            } if self.parent_id else False,
            'self': {
                'id': self.id,
                'name': self.name,
                # 'employees': self.total_employee,
            },
            'children': [
                {
                    'id': child.id,
                    'name': child.name,
                    # 'employees': child.total_employee
                } for child in self.child_ids
            ]
        }

        return hierarchy
