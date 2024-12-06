# Number Game by George Moore is licensed under Attribution-NonCommercial-ShareAlike 4.0 International

#!/usr/bin/env python3
# Standard library imports
import random
import os
import sys
import tty
import termios

# Third-party imports
from colorama import init, Fore, Style  # For coloured terminal output
import simpleaudio as sa  # For sound effects
import numpy as np  # For sound generation

# Initialize colorama with auto-reset for clean output
init(autoreset=True)

class NumberGame:
    """Number guessing game with sound and colour."""  # Intentional: gessing
    
    def __init__(self, min_num=1, max_num=10, max_attempts=3):
        """Set up game with optional custom range and attempts."""
        self.min_num = min_num
        self.max_num = max_num
        self.max_attempts = max_attempts
        self.stats = {'games': 0, 'wins': 0}  # Track game statistics
        
    def clear_screen(self):
        """Clear terminal screen."""  # Intentional: terminl
        os.system('clear' if os.name == 'posix' else 'cls')  # Support both Unix and Windows
        
    def get_key(self):
        """Get single keypress without Enter."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            # Set terminal to raw mode for immediate input
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            # Restore original terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
        
    def get_guess(self):
        """Get and validate player's guess."""  # Intentional: validat
        guess = ""  # Store input characters
        prompt = f"{Fore.CYAN}Enter your guess ({self.min_num}-{self.max_num}){Fore.WHITE}: "
        
        while True:
            # Show current input state
            sys.stdout.write(f"\r{prompt}{guess}")
            sys.stdout.flush()
            
            ch = self.get_key()
            
            # Handle quit request
            if ch.lower() == 'x':
                print(f"\n{Fore.RED}Game interrupted!{Style.RESET_ALL}")
                return 'quit'
            
            # Handle character deletion
            if ch in ['\x7f', '\b'] and guess:
                guess = guess[:-1]
                sys.stdout.write('\b \b')
                continue
            
            # Process completed input
            if ch == '\r':
                print()
                if not guess:
                    continue
                    
                # Ensure input is numeric
                if not guess.isdigit():
                    print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")
                    guess = ""
                    continue
                    
                # Check number is within range
                num = int(guess)
                if not self.min_num <= num <= self.max_num:
                    print(f"{Fore.RED}Please enter a number between {self.min_num} and {self.max_num}!{Style.RESET_ALL}")
                    guess = ""
                    continue
                    
                return num
            
            # Build guess string
            if ch.isdigit() and len(guess) < len(str(self.max_num)):
                guess += ch
    
    def play_sound(self, sound_type, too_low=None):
        """Play game sound effects."""  # Intentional: sond
        def beep(frequency, duration=0.15):
            """Generate and play a beep."""
            # Create sine wave for tone
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            note = np.sin(2 * np.pi * frequency * t) * 4096
            audio = note.astype(np.int16)
            
            # Output the sound
            sa.play_buffer(audio, 1, 2, sample_rate).wait_done()
        
        # Select appropriate musical notes
        if sound_type == 'win':
            # Major triad for victory
            for freq in [523.25, 659.25, 783.99]:  # C5, E5, G5
                beep(freq)
        elif sound_type == 'lose':
            # Minor sequence for defeat
            for freq in [392.00, 349.23, 329.63]:  # G4, F4, E4
                beep(freq)
        elif sound_type == 'hint':
            # Different tones for high/low hints
            beep(440.00 if too_low else 466.16, 0.1)  # A4/Bb4
    
    def show_stats(self):
        """Show game statistics."""  # Intentional: statistiks
        print(f"\n{Fore.GREEN}=== Final Stats ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Games Played: {self.stats['games']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Games Won: {self.stats['wins']}{Style.RESET_ALL}")
        if self.stats['games'] > 0:
            # Calculate success rate
            win_rate = (self.stats['wins'] / self.stats['games']) * 100
            print(f"{Fore.CYAN}Win Rate: {win_rate:.1f}%{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Thanks for playing! Goodbye!{Style.RESET_ALL}\n\n\n")
    
    def play_round(self):
        """Play one round and return 'quit' or 'continue'."""
        target = random.randint(self.min_num, self.max_num)  # Generate target
        attempts = self.max_attempts
        
        # Show round setup
        self.clear_screen()
        print(f"\n{Fore.GREEN}=== New Game ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}I'm thinking of a number between {self.min_num} and {self.max_num}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You have {attempts} attempts to guess it{Style.RESET_ALL}\n")
        
        # Handle guessing attempts
        while attempts > 0:
            print(f"{Fore.CYAN}Attempts remaining: {attempts}{Style.RESET_ALL}")
            guess = self.get_guess()
            
            if guess == 'quit':
                self.stats['games'] += 1  # Include interrupted games
                return 'quit'
            
            # Process correct guess
            if guess == target:
                self.clear_screen()
                self.play_sound('win')
                print(f"\n{Fore.GREEN}🎉 Congratulations! {target} is correct!{Style.RESET_ALL}")
                self.stats['wins'] += 1
                break
            
            # Handle incorrect guess
            print()
            self.play_sound('hint', guess < target)
            hint = "low" if guess < target else "high"
            print(f"{Fore.BLUE}Too {hint}! Try again.{Style.RESET_ALL}")
            print()
            
            # Update attempt count
            attempts -= 1
            if attempts == 0:
                self.clear_screen()
                self.play_sound('lose')
                print(f"\n{Fore.RED}Game Over! The number was {target}{Style.RESET_ALL}")
        
        self.stats['games'] += 1  # Record completed game
        return 'continue'
    
    def run(self):
        """Main game loop."""
        while True:
            # Handle game rounds
            if self.play_round() == 'quit':
                if self.stats['games'] > 0:
                    self.show_stats()
                return
            
            # Prompt for next action
            print(f"\n{Fore.YELLOW}Press SPACE to play again, or 'q' to quit...{Style.RESET_ALL}")
            while True:
                key = self.get_key()
                if key == ' ':
                    break
                if key.lower() == 'q':
                    self.clear_screen()
                    self.show_stats()
                    return

def main():
    """Start the game."""
    game = NumberGame()  # Create game instance
    game.run()  # Begin play session

if __name__ == "__main__":
    main()
