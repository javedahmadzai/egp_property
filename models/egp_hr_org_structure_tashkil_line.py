from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class TashkilLine(models.Model):
    _name = "tashkil.line"
    _description = 'Tashkil line Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name")
    department_id = fields.Many2one('hr.department', string='Department', store=True)
    position_work_location = fields.Many2one('hr.work.location', string='Work Location')
    position_no_of_recruit = fields.Integer(string="Target", default=1,
                                            help='Number of new employees you expect to recruit.')
    code = fields.Char(string='Code')
    position_rank = fields.Selection([
        ('out_of_rank', 'خارج رتبه'),
        ('superior_rank', 'مافوق رتبه'),
        ('1st_batch', '1'),
        ('2nd_batch', '2'),
        ('3rd_batch', '3'),
        ('4th_batch', '4'),
        ('5th_batch', '5'),
        ('6th_batch', '6'),
        ('7th_batch', '7'),
        ('8th_batch', '8'),
    ], string='Position Rank')

    position_status = fields.Selection([
        ('newly_created', 'Newly Created Department'),
        ('newly_created_position', 'Newly Created Position'),
        ('department_changed', 'Department changed'),
        ('cancelled', 'Cancelled'),
    ], string='Status')

    no_to_recruit = fields.Integer(string="No of vacancies", default=1)
    change_department_id = fields.Many2one('egp.tashkil', string='New Department')
    egp_tashkil_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    egp_tashkil_position_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    creation_year = fields.Integer(string='Creation Year', related='egp_tashkil_id.creation_year')

    position_creation_year = fields.Integer(string='Creation Year', related='egp_tashkil_position_id.creation_year')
    report_to = fields.Many2one('hr.job', string="Report To")
    custom_job_description = fields.Html(string="Layiha Wazayif")
    employment_type = fields.Many2one('hr.contract.type', string="Employment Type")
    parent_department_id = fields.Many2one('tashkil.line', string="Parent")

    change_department = fields.Many2one('hr.department', string="Department")
    change_department_code = fields.Char(string="Code", related='change_department.code')

    # for change position
    job_id = fields.Many2one('hr.job', string='Job Position')
    position_department_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    # position_change_department = fields.Many2one('hr.department', string='New Department')
    change_position_department_id = fields.Many2one('hr.department', string='Current Department',
                                                    related='job_id.department_id', store=True)

    change_position_code = fields.Char(related='job_id.code', string='Code')
    change_position_rank = fields.Selection(related='job_id.position_rank', string='Position Rank', store=True)

    # for Cancel position
    cancel_position_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    position_check = fields.Selection([
        ('position_active', 'Active'),
        ('position_passive', 'In-Active'),
        ('position_under_process', 'In-Progress'),
    ], string='Status', required=True, default='position_passive')

    # for Cancel departments
    cancel_department = fields.Many2one('egp.tashkil', string="Cancel Department", invisible=True)
    cancel_department_id = fields.Many2one('hr.department', string="Cancel Department", invisible=True)
    cancel_dep_code = fields.Char(related='cancel_department_id.code', string='Code')
    department_active = fields.Boolean(string="Active", default=False)

    def get_position_status_label(self):
        label_mapping = {
            'newly_created': 'Newly Created Department',
            'newly_created_position': 'Newly Created Position',
            'department_changed': 'Department changed',
            'cancelled': 'Cancelled'
        }
        return label_mapping.get(self.position_status, '')

    # for printing the display of position activeness value in xml report
    def get_position_activeness_check_label(self):
        label_mapping = {
            'position_active': 'Active',
            'position_passive': 'In-Active',
            'position_under_process': 'In-Progress'
        }
        return label_mapping.get(self.position_activeness_check, '')

    def get_position_rank_label(self):
        label_mapping = {
            'out_of_rank': 'خارج رتبه',
            'superior_rank': 'مافوق رتبه',
            '1st_batch': '1',
            '2nd_batch': '2',
            '3rd_batch': '3',
            '4th_batch': '4',
            '5th_batch': '5',
            '6th_batch': '6',
            '7th_batch': '7',
            '8th_batch': '8',
        }
        return label_mapping.get(self.position_rank, '')
