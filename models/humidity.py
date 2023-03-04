from odoo import fields, models, api

class Humidity(models.Model):
    _name = 'my_sensor_module.humidity'
    _description = 'Humidity Model'

    sensor_name = fields.Char(string='Sensor Name', required=True)
    humidity = fields.Float(string='Humidity', required=True)
    created_date = fields.Datetime(string='Created Date', default=fields.Datetime.now())
    updated_date = fields.Datetime(string='Updated Date', default=fields.Datetime.now())
    sensor_status = fields.Selection([('OK', 'OK'), ('Warning', 'Warning'), ('Error', 'Error')], default='OK')

    # @api.model
    # def create(self, vals):
    #     if not vals.get('date'):
    #         vals['date'] = fields.Datetime.now()
    #     return super(Humidity, self).create(vals)


