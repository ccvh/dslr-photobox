#!/usr/bin/env python
#from __future__ import division
import os
import sys
import re
import time
import datetime
from glob import glob

import RPi.GPIO as GPIO 

import piggyphoto
import pygame
from pygame.locals import *
from PIL import Image

import cups

__version__ = '1.3'

GPIO.setmode(GPIO.BCM)
RFIN = 20 # GPIO port of 433mhz receivers data port
GPIO.setup(RFIN, GPIO.IN)

PRINTIN = 21
GPIO.setup(PRINTIN, GPIO.IN)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

TOP_LEFT = (0, 0)
SECOND_LINE = (0, 20)

DISPLAY_SIZE = (800, 480)

THEME = 'themes/standard/'

IMAGES_PATH = 'images'
IMAGE_NAME_TEMPLATE = 'DSC_{0}.jpg'
CREATE_THUMBNAIL = True
THUMBNAIL_PATH = 'images/thumbs'
THUMBNAIL_NAME_TEMPLATE = 'DSC_{0}.jpg'
THUMBNAIL_WIDTH = '800'

TIME_FORMAT ='%Y-%m-%d %H:%M'
LOGFILE = 'logfile.txt'

IDLE = True


def get_next_image_number(path):
	try:
		last_path = max(
						glob(os.path.join(path, IMAGE_NAME_TEMPLATE.format('*')))
						)
	except ValueError:
		return 0  # No matching filenames found.
	else:
		last_filename = os.path.basename(last_path)
		match = re.search(r'\d+', last_filename)
		return int(match.group()) + 1 if match else 0


def play_sequence(surface, images):
	surface.fill(BLACK)

	for image, duration in images:
		
		start_image = pygame.image.load(THEME + 'logo.png').convert_alpha()
		start_image = pygame.transform.scale(start_image, DISPLAY_SIZE)
		surface.blit(start_image, TOP_LEFT)

		if image:
			image = pygame.transform.scale(image, DISPLAY_SIZE)
			surface.blit(image, TOP_LEFT)
		pygame.display.update()
		pygame.time.delay(duration)

		blank_image = pygame.image.load(THEME + 'logo.png').convert_alpha()
		blank_image = pygame.transform.scale(start_image, DISPLAY_SIZE)
		surface.blit(blank_image, TOP_LEFT)

		surface.fill(BLACK)


def load_images():
	background_image_1 = pygame.image.load(THEME + '1.png').convert_alpha()
	background_image_2 = pygame.image.load(THEME + '2.png').convert_alpha()
	background_image_3 = pygame.image.load(THEME + '3.png').convert_alpha()
	smile_image = pygame.image.load(THEME + 'smile.png').convert_alpha()
	processed_image = pygame.image.load(THEME + 'proc.png').convert_alpha()
	return {
		'sequence': [
					 (background_image_1, 500),
					 (None, 500),
					 (background_image_2, 500),
					 (None, 500),
					 (background_image_3, 500),
					 (smile_image, 50),
					 ],'processed_image': processed_image,
}


def take_photo(surface, images):
	global IDLE

	if IDLE:
		IDLE = False

		play_sequence(surface, images['sequence'])
		
		try:
			camera = piggyphoto.camera()
		except piggyphoto.libgphoto2error, errormessage:
			error_handling(surface, str(errormessage))
			
		if not os.path.exists(IMAGES_PATH):
			os.makedirs(IMAGES_PATH, 0777)
		filename = os.path.join(IMAGES_PATH, IMAGE_NAME_TEMPLATE.format(format(get_next_image_number(IMAGES_PATH), '04d')))
		
		try:
			camera.capture_image(filename)
			
			images['processed_image'] = pygame.transform.scale(images['processed_image'], DISPLAY_SIZE)

			surface.blit(images['processed_image'], TOP_LEFT)
			pygame.display.update()
			#pygame.time.delay(500)

			if CREATE_THUMBNAIL:
				thumbnail_file = create_thumbnail(filename, THUMBNAIL_PATH, THUMBNAIL_WIDTH)

				photo = pygame.transform.scale(pygame.image.load(thumbnail_file).convert_alpha(), surface.get_size())
				surface.blit(photo, TOP_LEFT)
				pygame.display.update()
				pygame.time.delay(5000)
				surface.fill(BLACK)
				pygame.time.delay(500)

			else:
				photo = pygame.transform.scale(pygame.image.load(filename).convert_alpha(), surface.get_size())
				surface.blit(photo, TOP_LEFT)
				pygame.display.update()
				pygame.time.delay(5000)
				surface.fill(BLACK)
				pygame.time.delay(500)	
		
			

		except piggyphoto.libgphoto2error, errormessage:
			error_handling(surface, str(errormessage))

		IDLE = True

	else:
		print "Already in action ..."


def create_thumbnail(taken_photo_filename, path, thumb_x_size):
	if not os.path.exists(THUMBNAIL_PATH):
		os.makedirs(THUMBNAIL_PATH, 0777)

	thumb_filename = os.path.join(THUMBNAIL_PATH, THUMBNAIL_NAME_TEMPLATE.format(format(get_next_image_number(IMAGES_PATH) - 1, '04d')))

	thumb = Image.open(taken_photo_filename)

	image_x = thumb.size[0]
	image_y = thumb.size[1]
	image_ratio = image_y * 1.0  / image_x
	thumb_x_size = int(thumb_x_size)
	thumb_y_size = thumb_x_size * image_ratio

	thumb.thumbnail((thumb_x_size, thumb_y_size), Image.ANTIALIAS)
	thumb.save(thumb_filename, "JPEG")

	return thumb_filename

def current_timestamp():
	current_time = datetime.datetime.fromtimestamp(time.time()).strftime(TIME_FORMAT)

	return current_time


def error_handling(surface, errormessage):
	surface.fill(BLACK)
	error_image = pygame.image.load(THEME + "error.png").convert_alpha()
	error_image = pygame.transform.scale(error_image, DISPLAY_SIZE)

	surface.blit(error_image, TOP_LEFT)

	with open(LOGFILE, "a") as error_file:
		error_file.write(current_timestamp() + " # " + errormessage + "\n")

	error_font = pygame.font.SysFont("Monospace", 18)
	error_font.set_bold(True)
	error_message_display = error_font.render(errormessage, 1, WHITE)
	restart_message = error_font.render("Restarting in 3s", 1, WHITE)
	surface.blit(error_message_display, TOP_LEFT)
	surface.blit(restart_message, SECOND_LINE)

	pygame.display.update()
	pygame.time.delay(3000)


def print_image(path):
	connection = cups.Connection()
	printers = connection.getPrinters()
	printer = printers.keys()[0]
	cups.setUser('pi')

	img_to_print = os.path.join(IMAGES_PATH, IMAGE_NAME_TEMPLATE.format(format(get_next_image_number(IMAGES_PATH)-1, '04d')))

	print "Sending "+img_to_print+" to printer ..."

	connection.printFile(printer, img_to_print, "PhotoboxImage", {})


def print_callback_helper(PRINTIN):
	print_image(IMAGES_PATH)


def rf_callback_helper(RFIN):
	if IDLE:
		take_photo(surface, images)

		start_image = pygame.image.load(THEME + 'start.png').convert_alpha()
		start_image = pygame.transform.scale(start_image, DISPLAY_SIZE)
		surface.blit(start_image, TOP_LEFT)
		pygame.display.update()
	else:
		pass


def main():
	global surface
	global images
	global start_image

	print "............................................................"
	print ".........................MMM....MMMM........................"
	print "......................MMMMMMMMMMMMMMMMM....................."
	print "............M.......MMMMMMMMMMMMMMMMMMMM ......M............"
	print "...........MM.....MMMMMMMMMMMMMMMMMMMMMMMM .....M..........."
	print "...........MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM..........."
	print "............MMMMMMMMMMMMMMMMMM.MMMMMMMMMMMMMMMMM............"
	print "...............NMMMMMMMMMM........MMMMMMMMMMM..............."
	print "............................................................\n"
	print "#####################################################################\n"
	print "Welcome to OldGent's Photobox.\n"
	print "You are currently using Version " + __version__
	print "If you are experiencing any problems, or facing any bugs,"
	print "please feel free to contact me at chris@sirhc.name"
	print "Enjoy your Photobox. Photos freeze some of the best moments in life.\n"
	print "#####################################################################\n"
	time.sleep(0.5)

	print "Starting in 3 seconds ..."
	time.sleep(3)

	pygame.init()
	surface = pygame.display.set_mode(DISPLAY_SIZE, 0, 32)
	pygame.display.set_caption('PhotoBox v' + __version__)
	pygame.mouse.set_visible(False)
	
	surface.fill(BLACK)
	start_image = pygame.image.load(THEME + 'start.png').convert_alpha()
	start_image = pygame.transform.scale(start_image, DISPLAY_SIZE)
	surface.blit(start_image, TOP_LEFT)
	pygame.display.update()
	pygame.display.toggle_fullscreen()
	images = load_images()

	GPIO.add_event_detect(RFIN, GPIO.RISING, callback=rf_callback_helper, bouncetime=5000)
	GPIO.add_event_detect(PRINTIN, GPIO.RISING, callback=print_callback_helper, bouncetime=15000)

		
	while True:
		event = pygame.event.wait()

		if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
			pygame.display.toggle_fullscreen()
		elif (event.type == KEYDOWN and event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN):
			take_photo(surface, images)
			start_image = pygame.transform.scale(start_image, DISPLAY_SIZE)
			surface.blit(start_image, TOP_LEFT)
			pygame.display.update()
		elif (event.type == KEYDOWN and event.key == pygame.K_p):
			print_image(IMAGES_PATH)
		elif (event.type == KEYDOWN and event.key == pygame.K_q or event.type == QUIT):
			pygame.quit()
			GPIO.cleanup()
			return
			pygame.time.delay(50)


if __name__ == '__main__':
	main()