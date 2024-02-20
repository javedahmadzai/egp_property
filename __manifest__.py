# -*- coding: utf-8 -*-
{
    'name': "EGP Property",
    'description': """
        An Application for managing Real Estate Property!
        Manage your buildings, floors, properties and contract
    """,
    'version': '17.0.1.0',
    'summary': 'System with in-depth management of Projects, Buildings, Floors, Properties, Real Estate PMS - Odoo App',
    'author': 'Javed Ahmadzai , MCIT',
    'website': "https://mcit.gov.af/",
    'sequence': -100,
    'license': 'AGPL-3',
    'company': 'Ministry of Communication and IT Afghanistan - MCIT',
    'maintainer': 'Ministry of Communication and IT ',
    'support': 'Ministry of Communication and IT Afghanistan',
    'category': 'Real Estate/PMS MCIT',
    'depends': ['mail', 'board','maintenance', 'account', 'hr'],
    # data files always loaded at installation
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/estate_menu_view.xml',
        # 'views/dashboard.xml',
        'views/estate_views.xml',
        'views/view_property_type.xml',
        'views/view_property_type_tags.xml',
        'views/estate_offer_view.xml',
        'reports/estate_property_reports.xml',
        'reports/estate_offer.xml',
        'reports/property_details.xml',
        # 'reports/mail_template.xml',

        'views/res_user_view.xml',
        'wizard/wizard_validation_form.xml',
        'wizard/valuation_view.xml',
        'views/agent_view.xml',
        'views/agent_language.xml',
        'views/custom_ir_attachment_form_view.xml',
        'views/custom_ir_attachment_form_view_real_estate.xml',
        'views/tenant_payment_views.xml',
        # 'views/config_parameter_settings.xml'
        # 'views/sales_dashboard.xml'
        'views/pms_offer_ghoshai.xml',
        'views/view_department.xml',
        'views/maintenance_equipment_view.xml',
        'views/agent_team_views.xml',
        'views/building_part_view.xml',
    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         # '/egp_property/static/src/css/pmsCss.scss',
    #         'egp_property/static/src/components/**/*.js',
    #         'egp_property/static/src/components/**/*.xml',
    #         'egp_property/static/src/components/**/*.scss',
    #     ],
    # },

    'currency': 'AF',
    # data files containing optionally loaded demonstration data
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto-install': False,
    'live_test_url': '',

}
