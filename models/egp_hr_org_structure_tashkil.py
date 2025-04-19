from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Tashkil(models.Model):
    _name = 'egp.tashkil'
    _description = 'Tashkil Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "creation_year desc, sequence_number desc"

    name = fields.Char(string='Name', Tracking=True)
    creation_year = fields.Integer(string='Tashkil Year', placeholder='Enter Creation Year', Tracking=True)
    sequence_number = fields.Char(string='Sequence Number', readonly=True, required=True, copy=False, default=
    lambda self: _("New"))
    image = fields.Image(string='Image')
    description = fields.Text(string='Description', Tracking=True)
    job_position_ids = fields.One2many('tashkil.line', 'egp_tashkil_id', string='Job Details')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Under process'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', Tracking=True)

    # Add attachment of document
    attachment = fields.Binary(string='Attachment', attachment=True)
    filename = fields.Char(string='Filename')

    # Tashkil line fields
    department_new_ids = fields.One2many('tashkil.line', 'egp_tashkil_id', string='New departments')
    position_new_ids = fields.One2many('tashkil.line', 'egp_tashkil_position_id', string='Newly Created Positions')
    department_change_ids = fields.One2many('tashkil.line', 'change_department_id', string="Change Department")

    # for printing the display of tashkil activeness check value in xml report
    def get_tashkil_activeness_check_label(self):
        label_mapping = {
            'draft': 'Draft',
            'process': 'Under process',
            'active': 'Active',
            'archived': 'Archived'
        }
        return label_mapping.get(self.state, '')

    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = f"{self.name} -copy"
        # Duplicate the main record
        new_tashkil = super(Tashkil, self).copy(default=default)
        # Get the next sequence number and assign it to the duplicated record
        sequence_number = self.env['ir.sequence'].next_by_code('egp.tashkil')
        new_tashkil.sequence_number = sequence_number
        return new_tashkil

    @api.constrains('creation_year')
    def _check_creation_year(self):
        for record in self:
            if record.creation_year < 1300 or record.creation_year > 1500:
                raise ValidationError("Creation Year must be between 1300 and 1500.")

    @api.model
    def create(self, vals):
        vals['sequence_number'] = self.env['ir.sequence'].next_by_code('egp.tashkil')
        record = super(Tashkil, self).create(vals)
        # Change Tashkil state to 'process'
        record.state = 'process'
        return record

    # Add constraint for attachment to accept just PDF and DOCX file formats
    @api.constrains('attachment', 'filename')
    def _check_allowed_extensions(self):
        for record in self:
            if record.attachment and record.filename:
                extension = record.filename.split('.')[-1].lower()
                if extension not in ['pdf', 'docx']:
                    raise ValidationError(
                        f"Only PDF and Microsoft Word (DOCX) files are allowed. '{record.filename}' is not a valid file type.")

    active = fields.Boolean(default=True)

    changed_department_job_positions = fields.One2many(
        'tashkil.line', 'position_department_id',
        string='Changed Department')

    cancelled_job_positions = fields.One2many(
        'tashkil.line', 'cancel_position_id',
        string='Cancelled')

    cancelled_department_ids = fields.One2many(
        'tashkil.line', 'cancel_department',
        string="Cancel Department"
    )
    cancelled_department_name = fields.Char(related=cancelled_department_ids.name)

    def approve(self):
        for rec in self:
            # Set the state to 'active'
            rec.state = 'active'
            # Create new departments from `department_new_ids`
            for new_dep in rec.department_new_ids:
                # Check if a parent department exists in the current TashkilLine record
                parent_dep = new_dep.parent_department_id.department_id.id if new_dep.parent_department_id else False
                dep = {
                    'name': new_dep.name,
                    'code': new_dep.code,
                    'organization_year': new_dep.creation_year if new_dep.creation_year else False,
                    'parent_id': parent_dep
                }
                # Create the new department
                newly_created_department = self.env['hr.department'].create(dep)
                new_dep.department_id = newly_created_department.id

                print(
                    f"Creating department {new_dep.name} with parent department {new_dep.parent_department_id.name if new_dep.parent_department_id else 'None'}")

            # Create new positions from `position_new_ids`
            for new_position in rec.position_new_ids:
                department_to_assign = False

                # Check if parent_department_id exists in the current position's tashkil.line record
                if new_position.parent_department_id:
                    # Get the department assigned to the parent department in the tashkil.line record
                    department_to_assign = new_position.parent_department_id.department_id.id if new_position.parent_department_id.department_id else False

                position_vals = {
                    'name': new_position.name,
                    'code': new_position.code,
                    'position_rank': new_position.position_rank,
                    'work_location_id': new_position.position_work_location.id if new_position.position_work_location else False,
                    'department_id': department_to_assign,  # Assigning the department based on parent_department_id
                    'no_of_recruitment': new_position.position_no_of_recruit,
                    'creation_year': new_position.position_creation_year if new_position.position_creation_year else False,
                    'report_to_id': new_position.report_to.id if new_position.report_to else False,
                    'contract_type_id': new_position.employment_type.id if new_position.employment_type else False,
                    'custom_job_description': new_position.custom_job_description,
                }

                # Create the new position (hr.job)
                newly_created_position = self.env['hr.job'].create(position_vals)

            # Loop through department_job_positions change records
            for change in rec.changed_department_job_positions:
                job_position = self.env['hr.job'].browse(change.job_id.id)
                if job_position:
                    # Check if parent_department_id is set in the 'tashkil.line' model (from XML view)
                    if change.parent_department_id:
                        # Get the parent department from 'tashkil.line'
                        parent_dep = change.parent_department_id

                        if parent_dep:
                            # Get the department_id from parent department (tashkil.line)
                            department_id_to_assign = parent_dep.department_id.id if parent_dep.department_id else False

                            if department_id_to_assign:
                                # Check if the job position is already assigned to the same department
                                if job_position.department_id.id == department_id_to_assign:
                                    raise ValidationError(
                                        _("The position '%s' is already assigned to the department '%s'. No changes needed.") % (
                                            job_position.name, parent_dep.name)
                                    )

                                # Update the position's department_id if it is different
                                job_position.write({
                                    'department_id': department_id_to_assign,
                                })
                                print(f"Position {job_position.name} moved to department {parent_dep.name}")
                            else:
                                raise ValidationError(
                                    f"Invalid department for position {job_position.name}, skipping update.")
                        else:
                            raise ValidationError(f"No parent department set for position {job_position.name}")
                    else:
                        raise ValidationError(
                            f"New department (parent_department_id) not set for position {job_position.name}")

            # Update cancelled job positions to set position_check field to 'position_passive'
            for cancelled_job in rec.cancelled_job_positions:
                job_position = self.env['hr.job'].browse(cancelled_job.job_id.id)
                if job_position:
                    job_position.write({
                        'position_activeness_check': 'position_passive',
                    })

            # Archive cancelled departments if no active jobs exist
            for cancelled_dep in rec.cancelled_department_ids:
                department = self.env['hr.department'].browse(cancelled_dep.cancel_department_id.id)
                if department:
                    job_positions = self.env['hr.job'].search([
                        ('department_id', '=', department.id),
                        ('active', '=', True)
                    ])
                    if job_positions:
                        raise ValidationError(
                            f"Department {department.name} cannot be cancelled or archived because it is associated with active job positions."
                        )
                    department.active = False

            # Loop through department change records
            for changeDep in rec.department_change_ids:
                department = self.env['hr.department'].browse(changeDep.change_department.id)

                if department:
                    # Check for parent department from the 'tashkil.line' model
                    parent_dep = changeDep.parent_department_id.department_id.id if changeDep.parent_department_id else False

                    if parent_dep:
                        parent_department = self.env['hr.department'].browse(parent_dep)

                        # Check for circular references
                        visited = set()
                        while parent_department:
                            if parent_department.id == department.id:
                                raise ValidationError(
                                    _("Circular reference detected: department '%s' cannot be a descendant of itself (%s).") % (
                                        department.name, department.name)
                                )
                            if parent_department.id in visited:
                                raise ValidationError(
                                    _("Circular reference detected: department '%s' cannot be a descendant of itself (%s).") % (
                                        department.name, department.name)
                                )
                            visited.add(parent_department.id)
                            parent_department = parent_department.parent_id

                        # Update department's parent if no circular references are found
                        department.write({'parent_id': parent_dep})
                        print(
                            f"Department {department.name} parent updated to {parent_department.name if parent_dep else 'None'}")
                    else:
                        # No parent department provided, you can optionally set the department parent as False if necessary
                        department.write({'parent_id': False})
                        print(f"Department {department.name} parent removed")

    previous_tashkils = fields.One2many(
        'egp.tashkil', 'related_tashkil_id', string="Previous Tashkils", compute='_compute_previous_tashkils',
        store=False)

    related_tashkil_id = fields.Many2one('egp.tashkil', string="Related Tashkil")

    @api.depends('creation_year')
    def _compute_previous_tashkils(self):
        for record in self:
            previous_tashkils = self.env['egp.tashkil'].search([
                ('creation_year', '<', record.creation_year)
            ])
            record.previous_tashkils = previous_tashkils

    def archive(self):
        for rec in self:
            # Set the state to 'archived'
            rec.state = 'archived'

    @api.constrains('description')
    def _check_description_length(self):
        max_length = 1000
        for record in self:
            if record.description and len(record.description) > max_length:
                raise ValidationError(
                    f"The description field cannot exceed {max_length} characters. The current length is {len(record.description)} characters.")

    # prevent deletion when the state is activated
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'process']:
                raise ValidationError(_("WARNING....\n Deletion is possible only in Draft or Process State"))
            return super(Tashkil, self).unlink()
