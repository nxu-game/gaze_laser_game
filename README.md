# Eye Laser Game

An eye-tracking based laser shooting game using MediaPipe for eye position detection and gesture recognition.

[中文文档](README_CN.md)

## Game Features

- Continuous laser beams from your eyes
- Fire powerful lasers by touching your nose
- Targets approaching from all directions
- Normal targets and bomb targets
- Level system and lives system
- Cool visual effects and sound effects
- Performance-optimized physics engine

## Requirements

1. Python 3.7+
2. Webcam

## Dependencies

```
pip install -r requirements.txt
```

Main dependencies:
- OpenCV
- MediaPipe
- Pygame
- NumPy

## How to Run

1. Install all dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the game (two ways):
   ```
   python run.py
   ```
   or
   ```
   python -m gaze_laser_game
   ```

## Sounds and Background

The game supports the following sounds and background image:

1. Sound files (place in `gaze_laser_game/assets/sounds` directory):
   - `laser.wav` - Laser firing sound
   - `bomb0.mp3` - Normal target explosion sound
   - `bomb1.mp3` - Bomb explosion sound
   - `game_over.mp3` - Game over sound
   - `background.mp3` - Background music

2. Background image (place in `gaze_laser_game/assets` directory):
   - `background.jpg` - Game background image

If these files don't exist, the game will still run, just without sounds and background image.

## Game Controls

- **Eye Movement**: Aim with your eyes (thin continuous laser beams)
- **Touch Nose**: Fire powerful lasers
- **SPACE**: Pause/resume game, restart after game over
- **ESC**: Exit game
- **M**: Mute/unmute background music
- **F**: Manually fire lasers in debug mode

## Game Rules

1. Aim at targets with your eyes, touch your nose to fire powerful lasers
2. Hit normal targets (colored) to score points
3. Avoid bomb targets (red) hitting your eyes, or you'll lose lives
4. Game over when lives reach zero
5. Difficulty increases as your score goes up

## Technical Features

- Uses MediaPipe's Face Mesh model for facial feature detection
- Real-time eye position tracking and gesture recognition
- Optimized collision detection algorithms
- Multi-threaded processing for improved performance
- Adaptive difficulty system

## Tips

- Ensure good lighting for best eye tracking results
- Maintain an appropriate distance, typically 30-60 cm
- If eye tracking is inaccurate, try adjusting camera position or lighting conditions

## Troubleshooting

- If the game doesn't start, make sure your camera is connected and working
- If eye tracking is inaccurate, try playing in better lighting conditions
- If the game has low FPS, try reducing camera resolution or turning off some visual effects

## Developer Information

This game is developed using MediaPipe and Pygame, utilizing MediaPipe's Face Mesh model for eye position detection and gesture recognition. The game includes an optimized physics engine, supports targets approaching from all directions, and features cool visual effects.

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3). See the LICENSE file for details. 