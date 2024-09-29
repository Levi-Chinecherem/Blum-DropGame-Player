import sys
import time
import dxcam
import mouse
import datetime

from prepare_app import prepare_app
from constants import (
	APPLICATION_TRIGGER,
	COLOR_TRIGGERS,
	PIXELS_PER_ITERATION,
)

__author__ = "SemanticDev"

def check_running(frame, application_bbox) -> bool:
	""" Check if the game is running by scanning color on timer positions """
	for x, y in APPLICATION_TRIGGER['positions']:
		x *= application_bbox[2] - application_bbox[0]
		y *= application_bbox[3] - application_bbox[1]
		x = int(x)
		y = int(y)
		x += application_bbox[0]
		y += application_bbox[1]
		if frame[y][x][0] == APPLICATION_TRIGGER['color'][0]:
			if frame[y][x][1] == APPLICATION_TRIGGER['color'][1]:
				if frame[y][x][2] == APPLICATION_TRIGGER['color'][2]:
					return True
	return False


def check_object(pixel: tuple[int]) -> bool:
	""" Detecting dropping objects by color """
	if COLOR_TRIGGERS['red']['min'] <= pixel[0] <= COLOR_TRIGGERS['red']['max']:
		if COLOR_TRIGGERS['green']['min'] <= pixel[1] <= COLOR_TRIGGERS['green']['max']:
			if COLOR_TRIGGERS['blue']['min'] <= pixel[2] <= COLOR_TRIGGERS['blue']['max']:
				return True
	return False


def wait_running_game(camera) -> None:
	application_bbox = prepare_app()
	frame = camera.get_latest_frame()

	# Loop until the game is detected as running
	while not check_running(frame, application_bbox):
		application_bbox = prepare_app()
		frame = camera.get_latest_frame()


def main():
	""" Autoclicker implementation """
	# Ask user for the number of games
	amount_of_games = int(input("Enter the number of games to play: "))

	camera = dxcam.create()
	camera.start(target_fps=60)

	print('Waiting for the game to start...')
	wait_running_game(camera)

	game_counter = 0

	while game_counter < amount_of_games:
		game_counter += 1
		print(f'Game {game_counter} detected!')

		# Capture the bounding box of the game window again
		application_bbox = prepare_app()

		# Frame processing loop until the game ends
		while check_running(camera.get_latest_frame(), application_bbox):
			frame = camera.get_latest_frame()
			height, width, _ = frame.shape

			for y in range(0, height, PIXELS_PER_ITERATION):
				for x in range(0, width, PIXELS_PER_ITERATION):
					if check_object(frame[y][x]):
						mouse.move(x, y, absolute=True)
						mouse.click(button='left')

		print(f"Game {game_counter} finished")

		# If there are more games to play, manually prompt the user
		if game_counter < amount_of_games:
			print("Please click 'Play Again' to continue...")
			wait_running_game(camera)  # Wait for the user to start the next game

	camera.stop()


if __name__ == "__main__":
	main()
