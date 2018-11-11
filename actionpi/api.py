import logging
import os

from .app import name, version
from .camera import AbstractCamera
from .system import AbstractSystem
from flask import Flask, request, render_template, abort, jsonify
from flask.testing import FlaskClient
from werkzeug.routing import BaseConverter, ValidationError

class ActionPiAPI(object):

    def __init__(self, camera: AbstractCamera, system: AbstractSystem, host: str, port: int, debug=False):
        self._camera = camera
        self._system = system
        self._host = host
        self._port = port
        self._debug = debug

        self._api = Flask(__name__)

        #Setup routes
        self._api.add_url_rule('/api/start', '_start_recording', self._start_recording)
        self._api.add_url_rule('/api/stop', '_stop_recording', self._stop_recording)
        self._api.add_url_rule('/api/status', '_get_status', self._get_status)
        self._api.add_url_rule('/api/set', '_set', self._set)
        self._api.add_url_rule('/api/halt', '_halt', self._halt)
        self._api.add_url_rule('/api/hotspot', '_hotspot', self._hotspot)
        self._api.add_url_rule('/control', '_control', self._control)

    def _start_recording(self):
        self._camera.start_recording()
    
    def _stop_recording(self):
        self._camera.stop_recording()

    def _set(self, val: int):
        #TODO add more logic if needed in future
        self._camera.change_framerate(val)

    def _get_status(self) -> dict:
        return jsonify({
            'system': {
                'cpu_temperature': self._system.get_cpu_temp(),
                'cpu_load': self._system.get_cpu_percent(),
                'mem_usage': self._system.get_ram_usage(),
                'disk_usage': self._system.get_disk_usage()
            }, 
            'recording': self._camera.is_recording(),
            'framerate': self._camera.get_framerate()
        })

    def _control(self):
        return render_template('index.html', app={"name":name, "version":version})

    def _halt(self):
        self._system.halt_system()

    def _hotspot(self):
        enable = request.args.get('enable', False)
        if enable == True:
            logging.info('Enabling hotspot')
            if not self._system.enable_hotspot():
                abort(500)
        elif enable == False:
            logging.info('Disabling hotspot')
            if not self._system.disable_hotspot():
                abort(500)
        else:
            logging.error('enable must be true or false, received: %s', enable)
            return ('enable must be true or false', 400)

    """
    Only for test purpose
    """
    def get_test_client(self) -> FlaskClient:
        return self._api.test_client()

    """
    Only for test purpose
    """
    def get_context(self):
        return self._api.app_context()

    def serve(self):
        self._api.run()

    def close(self):
        pass

    

    