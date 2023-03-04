# -*- coding: utf-8 -*-
{
    'name': 'Sensor',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'A module for reading sensor data',
    'description': 'This module allows you to read temperature and humidity data from a sensor and display it in a chart.',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/error_view.xml',
        'views/sensor_controller_view.xml',
        #'data/sensor_controller_data.xml',
        'data/ir_cron.xml',
    ],
    'qweb': [
        # 'static/src/xml/temperature_template.xml',
        # 'static/src/xml/sensor_template.xml',
    ],
    'css': [
        'static/src/css/my_style.css',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
