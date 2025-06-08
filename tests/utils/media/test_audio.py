import unittest
from unittest.mock import Mock, patch, MagicMock

from tests.shared_annotations import StandardTestCase, mock_test_module
from src.utils.media.audio import PygameMixerSoundSingleton


class TestPygameMixerSound(StandardTestCase):
    def setUp(self):
        super().setUp()
        # Reset singleton state for each test
        PygameMixerSoundSingleton._instances = {}
        
    @mock_test_module('pygame.mixer', 
                     init=Mock(return_value=True),
                     get_init=Mock(return_value=(22050, -16, 2)),
                     Sound=Mock(return_value=Mock()),
                     get_busy=Mock(return_value=False))
    def test_setup(self):
        mixer = PygameMixerSoundSingleton()
        self.assertIsNotNone(mixer)
        
        # Test that attempting to create another instance with setup raises error
        with self.assertRaises(RuntimeError):
            mixer2 = PygameMixerSoundSingleton()
            mixer2.setup()  # This should raise the error
    
    @mock_test_module('pygame.mixer',
                     init=Mock(return_value=True),
                     get_init=Mock(return_value=(22050, -16, 2)),
                     Sound=Mock(return_value=Mock()),
                     get_busy=Mock(return_value=False))
    def test_load_sound(self):
        mixer = PygameMixerSoundSingleton()
        
        # Mock the Sound constructor to return a mock sound object
        mock_sound = Mock()
        with patch('pygame.mixer.Sound', return_value=mock_sound):
            mixer.load_sound("Fake_sound.wav")
            self.assertEqual(mixer._sound, mock_sound)
    
    @mock_test_module('pygame.mixer',
                     init=Mock(return_value=True),
                     get_init=Mock(return_value=(22050, -16, 2)),
                     Sound=Mock(return_value=Mock()),
                     get_busy=Mock(return_value=False))
    def test_play_sound(self):
        mixer = PygameMixerSoundSingleton()
        
        # Mock the Sound constructor and play method
        mock_sound = Mock()
        with patch('pygame.mixer.Sound', return_value=mock_sound):
            mixer.load_sound("Fake_sound.wav")
            mixer.play_sound()
            mock_sound.play.assert_called_once()
    
    @mock_test_module('pygame.mixer',
                     init=Mock(return_value=True),
                     get_init=Mock(return_value=(22050, -16, 2)),
                     Sound=Mock(return_value=Mock()),
                     get_busy=Mock(return_value=False))
    def test_is_sound_playing(self):
        mixer = PygameMixerSoundSingleton()
        
        # Mock the Sound constructor and configure get_num_channels
        mock_sound = Mock()
        mock_sound.get_num_channels.return_value = 0  # Configure return value
        with patch('pygame.mixer.Sound', return_value=mock_sound):
            mixer.load_sound("Fake_sound.wav")
            
            # Test when sound is not playing
            mock_sound.get_num_channels.return_value = 0
            self.assertFalse(mixer.is_sound_playing())
            
            # Test when sound is playing  
            mock_sound.get_num_channels.return_value = 1
            self.assertTrue(mixer.is_sound_playing())
