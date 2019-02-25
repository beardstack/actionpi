import io
import random
import argparse
import logging

from actionpi import (
    ActionPiFactory,
    ActionPiAPI, 
    ActionPiWhatchdog, 
    AbstractCamera, 
    AbstractIO, 
    AbstractSystem,
    name, version
)

#Parsing arguments
parser = argparse.ArgumentParser('{} - v.{}'.format(name, version))
parser.add_argument('host',
                    help='host')
parser.add_argument('port',
                    type=int,
                    help='host')
parser.add_argument('gpio',
                    type=int,
                    help='gpio')
parser.add_argument('-x', '--width',
                    type=int,
                    default=1920,
                    help='width')
parser.add_argument('-y', '--heigth',
                    type=int,
                    default=1080,
                    help='heigth')
parser.add_argument('-f', '--fps',
                    type=int,
                    default=20,
                    help='fps')
parser.add_argument('-b', '--bps',
                    type=int,
                    default=1200000,
                    help='bitrate')
parser.add_argument('-o', '--output_dir',
                    default='video.h264',
                    help='video.h264')
parser.add_argument('-p', '--platform',
                    default='raspberrypi',
                    help='platform')
parser.add_argument('-l', '--log_level',
                    metavar='log_level',
                    default='WARN',
                    choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                    help='file containing the configuration for autobot istance')

args = parser.parse_args()

# Set log level
logging.basicConfig(level=args.log_level)

# Instatiate all dependencies
camera = ActionPiFactory.get_camera(args.platform, args.width, args.heigth, args.fps, args.output_dir)
system = ActionPiFactory.get_system(args.platform)
io = ActionPiFactory.get_io(args.platform, camera, system, args.gpio)
api = ActionPiAPI(camera, system, args.host, args.port, args.log_level=='DEBUG')
watchdog = ActionPiWhatchdog(system, camera)

# Run background tasks
watchdog.watch()
io.start_monitoring()

logging.info('Starting REST server...')
# Let's go!
api.serve()

# Stopping all services
api.close()
io.close()
watchdog.unwatch()

# Ensuring all data are written on disk