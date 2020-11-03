# -*- coding: utf-8 -*-
{
    'name': "sinc_bigcommerce",

    'summary': """Sincronizacion entre BigCommerce y Odoo""",

    'description': """
        Sincronizacion entre BigCommerce y Odoo
    """,

    'author': "aquíH",
    'website': "http://www.aquih.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'contacts', 'product', 'sale'],

    'data': [
        'views/res_config_settings_views.xml',
        'views/product_template_views.xml',
        'wizard/sincronizacion_views.xml',
        'security/ir.model.access.csv',
    ],
}
