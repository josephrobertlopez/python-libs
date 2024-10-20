import pygame
import sys
import time
import logging
from src.utils.get_resource_path import get_resource_path

def play_alarm_sound(sound_file: str) -> None:
    """Play an alarm sound from the provided file.

    Args:
        sound_file (str): The path to the sound file to play.
    """
    pygame.mixer.init()
    if not pygame.mixer.get_init():
        logging.error("Mixer not initialized.")
        sys.exit(1)

    logging.info(f"Attempting to load sound file from: {sound_file}")
    try:
        alarm_sound = pygame.mixer.Sound(get_resource_path(sound_file))
        alarm_sound.play()
        while pygame.mixer.get_busy():
            time.sleep(0.1)
    except pygame.error as e:
        logging.error(f"Error playing sound: {e}")  
        sys.exit(1)

    pygame.mixer.quit()

    logging.info("Alarm sound played successfully.")