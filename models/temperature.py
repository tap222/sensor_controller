from odoo import fields, models, api

class Temperature(models.Model):
    _name = 'my_sensor_module.temperature'
    _description = 'Temperature Model'

    update_date = fields.Datetime(string='Update Date', required=True)
    temperature = fields.Float(string='Temperature', required=True)
    created_date = fields.Datetime(string='Created Date', required=True, default=fields.Datetime.now)
    sensor_name = fields.Char(string='Sensor Name', required=True)
    # sensor_status = fields.Selection([('OK', 'OK'), ('Warning', 'Warning'), ('Error', 'Error')], default='OK')


    @api.model
    def create(self, vals):
        if not vals.get('date'):
            vals['date'] = fields.Datetime.now()
        return super(Humidity, self).create(vals)

