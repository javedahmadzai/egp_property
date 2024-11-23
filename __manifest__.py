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
    'depends': ['mail', 'board', 'maintenance', 'account', 'hr'],
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
        'reports/egp_property_paper_format.xml',
        'reports/egp_property_report_action.xml',
        'reports/egp_property_details.xml',
        'reports/egp_property_details _copy.xml',
        'reports/equipment_template.xml',
        'reports/pms_contract_template.xml',
        # 'reports/mail_template.xml',
        'data/rent_received_mail_template.xml',
        'data/default_egp_property_users.xml',
        'views/res_user_view.xml',
        'wizard/wizard_validation_form.xml',
        'wizard/valuation_view.xml',
        'views/agent_view.xml',
        'views/tenant_payment_views.xml',
        # 'views/sales_dashboard.xml',
        'views/pms_contract.xml',
        'views/pms_contract_type.xml',
        'views/view_department.xml',
        'views/maintenance_equipment_view.xml',
        'views/agent_team_views.xml',
        'views/building_part_view.xml',
    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         'owl/static/src/components/**/*.js',
    #         'owl/static/src/components/**/*.xml',
    #         # 'owl/static/src/components/**/*.scss',
    #     ],
    # },
    'currency': 'AF',
    # demo data files containing optionally loaded demonstration data
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto-install': False,
    'live_test_url': '',

}
