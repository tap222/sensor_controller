import json
import socket
from odoo import http, models, fields, _
from odoo import api

class Sensor(models.Model):
    _name = 'my_sensor_module.sensor'

    name = fields.Char(string='Name', required=True)
    address = fields.Char(string='Address', required=True)
    port = fields.Integer(string='Port', required=True)
    controller_id = fields.Many2one(comodel_name='my_sensor_module.sensor_controller', string='Controller', ondelete='cascade')

class SensorController(models.Model):
    _name = 'my_sensor_module.sensor_controller'

    sensor_data = fields.Text(string='Sensor Data')
    temperature = fields.Float(string='Temperature')
    humidity = fields.Float(string='Humidity')
    date = fields.Datetime(string='Date', default=lambda self: fields.datetime.now())
    sensors = fields.One2many(comodel_name='my_sensor_module.sensor', inverse_name='controller_id', string='Sensors')
    current_sensor_id = fields.Many2one(comodel_name='my_sensor_module.sensor', string='Current Sensor')
    sensor_name = fields.Char(string='Sensor Name')
    sensor_address = fields.Char(string='Sensor Address')
    sensor_port = fields.Integer(string='Sensor Port')
    test_connection_status = fields.Char(string='Test Connection Status', readonly=True)
    status = fields.Char(compute='_compute_status', store=True, readonly=True)

    @api.depends('test_connection_status')
    def _compute_status(self):
        for record in self:
            # logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
            # logging.info(record.id)
            if record.test_connection_status == 'Connected':
                record.status = 'connected'
            else:
                record.status = 'not_connected'

    @api.model
    def test_connection(self, _context=None):
        for record in self:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    # Set a timeout of 5 seconds
                    sock.settimeout(5)
                    sock.connect((record.sensor_address, record.sensor_port))
                    # Send a test message to the server
                    message = 'Test Connection'
                    sock.sendall(message.encode())
                    record.test_connection_status = 'Connected'
                    self.env.cr.commit()
                # Refresh the current form view to display the updated status
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
            except (socket.timeout, ConnectionRefusedError, OSError) as error:
                record.test_connection_status = f"Connection failed: {error}"
                self.env.cr.commit()
                # Refresh the current form view to display the updated status
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }

    @http.route('/my_sensor_module/get_sensor_data', auth='public', type='json')
    def get_sensor_data(self):
        # Define the TCP/IP server address and port number
        SERVER_ADDRESS = self.current_sensor_id.address
        SERVER_PORT = self.current_sensor_id.port

        # Test the connection before fetching the sensor data
        if self.test_connection_status != 'Connected':
            self.status = 'Error updating sensor data: not connected'
            return
        else:
            try:
                # Create a socket object and connect to the server
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SERVER_ADDRESS, SERVER_PORT))

                # Send a request for sensor data to the server
                request = {
                    'command': 'get_data'
                }
                sock.sendall(json.dumps(request).encode())

                # Receive the sensor data from the server
                data = sock.recv(1024)

                # Close the socket connection to the server
                sock.close()
                try:
                    # Parse the JSON data
                    sensor_data = json.loads(data.decode())

                except json.JSONDecodeError as e:
                    self.status = 'Error parsing sensor data: %s' % str(e)
                    return

                # Update the temperature and humidity models in Odoo
                self.temperature = sensor_data['temperature']
                self.humidity = sensor_data['humidity']
                self.sensor_data = json.dumps(sensor_data)

                # Set the status message
                self.status = 'Sensor data updated successfully.'
            except Exception as e:
                # Set the status message to indicate the connection failed
                self.status = 'Error updating sensor data: %s' % str(e)

    @http.route('/my_sensor_module/update_sensor_data', auth='public', type='http')
    def update_sensor_data(self, **post):
        self.get_sensor_data()

        sensor_data = {
            'temperature': self.temperature,
            'humidity': self.humidity,
            'date': fields.datetime.now(),
            'current_sensor_id': self.current_sensor_id.id,
        }

        # Update the sensor data on the current sensor
        request = {
            'command': 'update_data',
            'data': sensor_data,
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.current_sensor_id.address, self.current_sensor_id.port))
        sock.sendall(json.dumps(request).encode())
        response = sock.recv(1024)
        sock.close()

        # Create a new sensor controller record with the updated data
        http.request.env['my_sensor_module.sensor_controller'].create({
            'name': self.name,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'date': fields.datetime.now(),
            'current_sensor_id': self.current_sensor_id.id,
        })

        # Redirect to the sensor controller page
        return http.redirect_with_hash('/web#menu_id=%d&action=%d&id=%d&view_type=form' % (
            http.request.env.ref('my_sensor_module.menu_sensor_controller').id,
            http.request.env.ref('my_sensor_module.action_sensor_controller').id, self.id))

# @http.route('/my_sensor_module/add_sensor', auth='user', website=True, csrf=False)
#     def add_sensor(self, **post):
#         # Get the sensor data from the form submission
#         sensor_name = post.get('sensor_name')
#         server_address = post.get('server_address')
#         server_port = post.get('server_port')
#
#         # Create a new sensor record without testing the connection first
#         sensor = http.request.env['my_sensor_module.sensor'].sudo().create({
#             'name': sensor_name,
#             'address': server_address,
#             'port': int(server_port),
#             'controller_id': http.request.env['my_sensor_module.sensor_controller'].search([], limit=1).id,
#         })
#
#         # Test the connection to the server after creating the new sensor record
#         connection_success = self.test_connection()
#
#         if not connection_success:
#             # Connection test failed, delete the new sensor record and return an error message
#             sensor.sudo().unlink()
#             return http.request.render('my_sensor_module.connection_test_error', {
#                 'error_message': _('Connection test failed.'),
#             })
#
#         # Connection test successful, redirect to the sensor controller page
#         return http.redirect_with_hash('/web#menu_id=%d&action=%d&id=%d' % (
#         http.request.env.ref('my_sensor_module.menu_sensor_controller').id,
#         http.request.env.ref('my_sensor_module.action_sensor_controller').id, sensor.controller_id.id))
