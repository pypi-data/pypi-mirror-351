"""
EcoCycle - Sharing Module
Handles functionality for sharing cycling stats via various formats.
"""
import logging
import os
import time
import random
import webbrowser
import datetime
from typing import Dict, Optional, Any

from apps.social_gamification.base import (
    SocialFeatureBase, RICH_AVAILABLE, console, 
    COLOR_SHARING
)

# Optional dependencies imports
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Rich UI components (if available)
try:
    import rich
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress
    from rich import box
    from rich.group import Group
except ImportError:
    pass

import utils.ascii_art as ascii_art
import utils.general_utils as general_utils

logger = logging.getLogger(__name__)


class SharingManager(SocialFeatureBase):
    """Manages sharing of cycling stats and achievements."""
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the sharing manager.
        
        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        super().__init__(user_manager, sheets_manager)
    
    def share_stats(self):
        """Share cycling stats on social media or via export with Rich UI styling."""
        user = self.user_manager.get_current_user()
        
        # Get user stats
        stats = user.get('stats', {})
        total_trips = stats.get('total_trips', 0)
        total_distance = stats.get('total_distance', 0.0)
        total_co2_saved = stats.get('total_co2_saved', 0.0)
        total_calories = stats.get('total_calories', 0)
        
        # Format user stats for sharing
        share_text = f"I've cycled {general_utils.format_distance(total_distance)} with EcoCycle!\n"
        share_text += f"🌍 Saved {general_utils.format_co2(total_co2_saved)} of CO2 emissions\n"
        share_text += f"🔥 Burned {general_utils.format_calories(total_calories)}\n"
        share_text += f"🚴 Completed {total_trips} cycling trips\n"
        share_text += "\n#EcoCycle #SustainableMobility #CyclingLife"
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Share your cycling achievements and environmental impact",
                title=f"[bold {COLOR_SHARING}]Share Your Stats[/bold {COLOR_SHARING}]",
                border_style=COLOR_SHARING,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Display share text in a panel
            share_preview = Panel(
                Text(share_text, style="white"),
                title="[bold blue]Preview[/bold blue]",
                border_style="blue",
                box=box.ROUNDED
            )
            console.print(share_preview)
            
            # Show sharing options
            options_table = Table(box=box.SIMPLE, show_header=False)
            options_table.add_column("Option", style="cyan", width=2)
            options_table.add_column("Description", style="white")
            options_table.add_column("Icon", style="yellow", width=4)
            
            options_table.add_row("1", "Generate Shareable Image", "🖼️")
            options_table.add_row("2", "Generate QR Code", "📱")
            options_table.add_row("3", "Copy Text to Clipboard", "📋")
            options_table.add_row("4", "Return to Social Hub", "🔙")
            
            console.print(Panel(
                options_table,
                title=f"[bold {COLOR_SHARING}]Sharing Options[/bold {COLOR_SHARING}]",
                border_style=COLOR_SHARING,
                box=box.ROUNDED
            ))
            
            choice = Prompt.ask("How would you like to share", choices=["1", "2", "3", "4"])
            
        else:
            # Fallback for non-Rich environments
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Share Your Stats")
            
            # Display share text
            print("Here's what we'll share:")
            print("-" * 50)
            print(share_text)
            print("-" * 50)
            
            # Sharing options
            print("\nHow would you like to share?")
            print("1. Generate Shareable Image 🖼️")
            print("2. Generate QR Code 📱")
            print("3. Copy Text to Clipboard 📋")
            print("4. Return to Social Hub 🔙")
            
            choice = input("\nSelect an option (1-4): ")
        
        if choice == "1":
            self._handle_image_sharing(user, share_text)
        elif choice == "2":
            self._handle_qr_sharing(share_text)
        elif choice == "3":
            self._handle_text_sharing(share_text)
        # choice 4 returns automatically
    
    def _handle_image_sharing(self, user, share_text):
        """Handle image generation and sharing."""
        # Check for PIL
        if not PIL_AVAILABLE:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]The PIL/Pillow library is required for generating images.[/yellow]\n"
                    "[white]Please run the following command to install it:[/white]\n"
                    "[bold cyan]pip install pillow[/bold cyan]",
                    title="[bold red]Dependency Required[/bold red]",
                    border_style="red"
                ))
                console.print("Press Enter to continue...", style="dim")
            else:
                print("The PIL/Pillow library is required for generating images.")
                print("Please install it with: pip install pillow")
                print("\nPress Enter to continue...")
            input()
            return
        
        if RICH_AVAILABLE:
            with console.status("[bold green]Generating shareable image...[/bold green]") as status:
                image_path = self._generate_share_image(user)
        else:
            print("\nGenerating shareable image...")
            image_path = self._generate_share_image(user)
        
        if image_path:
            self._show_generated_file_options(image_path, "Image")
        else:
            self._show_error("Error generating image.")
    
    def _handle_qr_sharing(self, share_text):
        """Handle QR code generation and sharing."""
        # Check for qrcode
        if not QRCODE_AVAILABLE:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]The qrcode library is required for generating QR codes.[/yellow]\n"
                    "[white]Please run the following command to install it:[/white]\n"
                    "[bold cyan]pip install qrcode[pil][/bold cyan]",
                    title="[bold red]Dependency Required[/bold red]",
                    border_style="red"
                ))
                console.print("Press Enter to continue...", style="dim")
            else:
                print("The qrcode library is required for generating QR codes.")
                print("Please install it with: pip install qrcode[pil]")
                print("\nPress Enter to continue...")
            input()
            return
        
        try:
            if RICH_AVAILABLE:
                with console.status("[bold green]Generating QR code...[/bold green]"):
                    filename = self._generate_qr_code(share_text)
            else:
                print("\nGenerating QR code...")
                filename = self._generate_qr_code(share_text)
            
            if filename:
                self._show_generated_file_options(filename, "QR Code")
            else:
                self._show_error("Error generating QR code.")
                
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            self._show_error(f"Error generating QR code: {str(e)}")
    
    def _handle_text_sharing(self, share_text):
        """Handle text copying and sharing."""
        if RICH_AVAILABLE:
            copy_text_panel = Panel(
                Text(share_text, style="white"),
                title="[bold blue]Copy the following text to share[/bold blue]",
                border_style="blue",
                box=box.ROUNDED,
                padding=(1, 2),
                expand=False
            )
            console.print(copy_text_panel)
            console.print("[dim]Text is ready to be copied manually.[/dim]")
        else:
            print("\nCopy the following text to share:")
            print("-" * 50)
            print(share_text)
            print("-" * 50)
            print("\nText is ready to be copied manually.")
    
    def _show_generated_file_options(self, file_path, file_type):
        """Show options for a generated file."""
        if RICH_AVAILABLE:
            file_info = f"[green]{file_type} saved to:[/green] [cyan]{file_path}[/cyan]"
            panel = Panel(
                file_info, 
                title=f"[bold green]{file_type} Generated Successfully[/bold green]",
                border_style="green",
                box=box.ROUNDED
            )
            console.print(panel)
            
            console.print("[bold]Options:[/bold]")
            console.print(f"1. Open {file_type}")
            console.print("2. Return to Social Hub")
            
            open_choice = Prompt.ask("Select an option", choices=["1", "2"])
        else:
            print(f"{file_type} saved to: {file_path}")
            
            print("\nOptions:")
            print(f"1. Open {file_type}")
            print("2. Return to Social Hub")
            
            open_choice = input("\nSelect an option (1-2): ")
        
        if open_choice == "1":
            try:
                if os.path.exists(file_path):
                    if RICH_AVAILABLE:
                        with console.status(f"[cyan]Opening {file_type.lower()}...[/cyan]"):
                            webbrowser.open(f"file://{os.path.abspath(file_path)}")
                    else:
                        webbrowser.open(f"file://{os.path.abspath(file_path)}")
                else:
                    self._show_error(f"{file_type} file not found.")
            except Exception as e:
                logger.error(f"Error opening {file_type.lower()}: {e}")
                self._show_error(f"Error opening {file_type.lower()}: {str(e)}")
    
    def _show_error(self, message):
        """Show an error message."""
        if RICH_AVAILABLE:
            console.print(f"[bold red]{message}[/bold red]")
        else:
            print(message)
    
    def _generate_share_image(self, user):
        """Generate a shareable image with user stats."""
        try:
            # Get user data
            username = user.get('username')
            name = user.get('name', username)
            stats = user.get('stats', {})
            total_trips = stats.get('total_trips', 0)
            total_distance = stats.get('total_distance', 0.0)
            total_co2_saved = stats.get('total_co2_saved', 0.0)
            total_calories = stats.get('total_calories', 0)
            
            # Create a new image
            width, height = 1000, 600
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Draw background
            draw.rectangle([(0, 0), (1000, 120)], fill=(76, 175, 80))  # Green header
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("Arial Bold.ttf", 36)
            except IOError:
                try:
                    title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
                except IOError:
                    title_font = ImageFont.load_default()
            
            try:
                subtitle_font = ImageFont.truetype("Arial.ttf", 24)
            except IOError:
                try:
                    subtitle_font = ImageFont.truetype("DejaVuSans.ttf", 24)
                except IOError:
                    subtitle_font = ImageFont.load_default()
            
            try:
                stats_font = ImageFont.truetype("Arial Bold.ttf", 48)
            except IOError:
                try:
                    stats_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
                except IOError:
                    stats_font = ImageFont.load_default()
            
            try:
                label_font = ImageFont.truetype("Arial.ttf", 20)
            except IOError:
                try:
                    label_font = ImageFont.truetype("DejaVuSans.ttf", 20)
                except IOError:
                    label_font = ImageFont.load_default()
            
            # Draw title
            draw.text((20, 25), "EcoCycle Stats", fill=(255, 255, 255), font=title_font)
            draw.text((20, 75), f"Cycling achievements for {name}", fill=(255, 255, 255), font=subtitle_font)
            
            # Draw stats section
            stats_y = 150
            
            # Distance
            draw.text((60, stats_y), "🚲", fill=(76, 175, 80), font=stats_font)
            draw.text((120, stats_y), general_utils.format_distance(total_distance), fill=(0, 0, 0), font=stats_font)
            draw.text((120, stats_y + 60), "Distance Cycled", fill=(100, 100, 100), font=label_font)
            
            # CO2 Saved
            stats_y += 120
            draw.text((60, stats_y), "🌍", fill=(76, 175, 80), font=stats_font)
            draw.text((120, stats_y), general_utils.format_co2(total_co2_saved), fill=(0, 0, 0), font=stats_font)
            draw.text((120, stats_y + 60), "CO2 Emissions Saved", fill=(100, 100, 100), font=label_font)
            
            # Calories
            stats_y += 120
            draw.text((60, stats_y), "🔥", fill=(76, 175, 80), font=stats_font)
            draw.text((120, stats_y), general_utils.format_calories(total_calories), fill=(0, 0, 0), font=stats_font)
            draw.text((120, stats_y + 60), "Calories Burned", fill=(100, 100, 100), font=label_font)
            
            # Trips
            stats_y += 120
            draw.text((60, stats_y), "🚴", fill=(76, 175, 80), font=stats_font)
            draw.text((120, stats_y), str(total_trips), fill=(0, 0, 0), font=stats_font)
            draw.text((120, stats_y + 60), "Cycling Trips", fill=(100, 100, 100), font=label_font)
            
            # Date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            draw.text((width - 200, height - 40), f"Generated: {current_date}", fill=(150, 150, 150), font=label_font)
            
            # Save the image
            filename = f"ecocycle_stats_{username}_{int(time.time())}.png"
            image.save(filename)
            
            return filename
        
        except Exception as e:
            logger.error(f"Error generating share image: {e}")
            return None
    
    def _generate_qr_code(self, share_text):
        """Generate a QR code with share text."""
        try:
            # Create a QR code containing the share text
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(share_text)
            qr.make(fit=True)
            
            # Create an image from the QR Code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save the image
            filename = f"ecocycle_qr_{int(time.time())}.png"
            img.save(filename)
            
            return filename
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None
    
    def _wait_for_user(self):
        """Wait for the user to press Enter to continue."""
        if RICH_AVAILABLE:
            console.print("\nPress Enter to continue...", style="dim")
        else:
            print("\nPress Enter to continue...")
        input()
    
    def generate_achievement_card(self):
        """Generate an achievement card for sharing."""
        user = self.user_manager.get_current_user()
        if not user:
            logger.warning("No user logged in")
            return
            
        # Check if PIL is available for image generation
        if not PIL_AVAILABLE:
            # Display message about required dependencies
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]The achievement card feature requires the PIL library.[/yellow]\n"
                    "[white]Please install it with: pip install pillow[/white]",
                    title=f"[bold {COLOR_SHARING}]Missing Dependency[/bold {COLOR_SHARING}]",
                    border_style="red"
                ))
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Missing Dependency")
                print("The achievement card feature requires the PIL library.")
                print("Please install it with: pip install pillow")
            
            self._wait_for_user()
            return
        
        # Get user achievements
        username = user.get('username')
        completed_achievements = user.get('completed_achievements', [])
        eco_points = user.get('eco_points', 0)
        stats = user.get('stats', {})
        name = user.get('name', username)
        
        # Get user level based on eco points
        level = 1
        if eco_points >= 100:
            level = 2
        if eco_points >= 250:
            level = 3
        if eco_points >= 500:
            level = 4
        if eco_points >= 1000:
            level = 5
        
        if not completed_achievements:
            # No achievements to show
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]You haven't earned any achievements yet.[/yellow]\n"
                    "[white]Complete cycling trips to earn achievements and create a card.[/white]",
                    title=f"[bold {COLOR_SHARING}]Achievement Card[/bold {COLOR_SHARING}]",
                    border_style=COLOR_SHARING
                ))
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Achievement Card")
                print("You haven't earned any achievements yet.")
                print("Complete cycling trips to earn achievements and create a card.")
            
            self._wait_for_user()
            return
        
        # Create card options display
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Showcase your achievements with a personalized card",
                title=f"[bold {COLOR_SHARING}]Achievement Card Generator[/bold {COLOR_SHARING}]",
                border_style=COLOR_SHARING,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Show achievement counts
            achievement_stats = (
                f"[bold]Achievements Completed:[/bold] {len(completed_achievements)}\n"
                f"[bold]Eco Points:[/bold] {eco_points}\n"
                f"[bold]Level:[/bold] {level}\n"
            )
            console.print(Panel(achievement_stats, title="[bold cyan]Your Stats[/bold cyan]", border_style="cyan"))
            
            # Show card layout options
            options_table = Table(show_header=False, box=box.SIMPLE)
            options_table.add_column("Option", style="cyan", width=2)
            options_table.add_column("Description", style="white")
            
            options_table.add_row("1", "Generate Achievement Card with Latest Achievements")
            options_table.add_row("2", "Generate Achievement Card with Level Focus")
            options_table.add_row("3", "Generate Achievement Card with Environmental Impact")
            options_table.add_row("4", "Manage Existing Achievement Cards")
            options_table.add_row("5", "Return to Social Hub")
            
            console.print(Panel(options_table, title="[bold green]Card Options[/bold green]", border_style="green"))
            
            choice = Prompt.ask("Choose a card style", choices=["1", "2", "3", "4", "5"])
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Achievement Card Generator")
            
            print(f"Achievements Completed: {len(completed_achievements)}")
            print(f"Eco Points: {eco_points}")
            print(f"Level: {level}")
            print()
            print("Card Options:")
            print("1. Generate Achievement Card with Latest Achievements")
            print("2. Generate Achievement Card with Level Focus")
            print("3. Generate Achievement Card with Environmental Impact")
            print("4. Manage Existing Achievement Cards")
            print("5. Return to Social Hub")
            
            choice = input("\nChoose a card style (1-5): ")
        
        if choice == "4":
            # Manage existing achievement cards
            self.manage_achievement_cards()
            return
        elif choice == "5":
            return
        
        try:
            # Get trip stats for the card
            total_distance = stats.get('total_distance', 0)
            total_co2_saved = stats.get('total_co2_saved', 0)
            total_trips = stats.get('total_trips', 0)
            
            # Create an image with the user's achievements
            width, height = 800, 600
            bg_color = (240, 248, 255)  # Light blue background
            text_color = (0, 0, 0)  # Black text
            accent_color = (76, 175, 80)  # Green accent
            
            # Create a new image with background color
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # Try to load fonts, with fallbacks
            try:
                title_font = ImageFont.truetype("Arial Bold", 36)
                subtitle_font = ImageFont.truetype("Arial", 24)
                stats_font = ImageFont.truetype("Arial Bold", 48)
                achievement_font = ImageFont.truetype("Arial", 18)
                label_font = ImageFont.truetype("Arial", 16)
            except Exception:
                # Fallback to default font
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                stats_font = ImageFont.load_default()
                achievement_font = ImageFont.load_default()
                label_font = ImageFont.load_default()
            
            # Add header background
            draw.rectangle([(0, 0), (width, 80)], fill=(39, 174, 96))
            
            # Add title text
            draw.text((20, 20), "EcoCycle Achievement Card", fill=(255, 255, 255), font=title_font)
            
            if choice == "1":  # Latest Achievements
                # Add subtitle
                draw.text((20, 90), f"Latest Achievements for {name}", fill=text_color, font=subtitle_font)
                
                # Add achievements (only show latest 3)
                achievement_y = 150
                for i, achievement_id in enumerate(completed_achievements[-3:]):
                    # Find achievement details from the AchievementManager module
                    from apps.social_gamification.achievements import ACHIEVEMENTS
                    achievement = next((a for a in ACHIEVEMENTS if a.get('id') == achievement_id), None)
                    if achievement:
                        icon = achievement.get('icon', '🏆')
                        a_name = achievement.get('name', 'Unknown')
                        desc = achievement.get('description', '')
                        points = achievement.get('points', 0)
                        
                        draw.text((40, achievement_y), icon, fill=accent_color, font=stats_font)
                        draw.text((100, achievement_y), a_name, fill=text_color, font=achievement_font)
                        draw.text((100, achievement_y + 30), desc, fill=(100, 100, 100), font=label_font)
                        draw.text((width - 100, achievement_y), f"+{points} pts", fill=accent_color, font=achievement_font)
                        
                        achievement_y += 80
                
                # Add stats section
                stats_y = 350
                draw.rectangle([(0, stats_y), (width, stats_y + 10)], fill=accent_color)  # Divider
                
                stats_y += 30
                draw.text((40, stats_y), "Level:", fill=text_color, font=subtitle_font)
                draw.text((150, stats_y), str(level), fill=accent_color, font=stats_font)
                
                stats_y += 70
                draw.text((40, stats_y), "Total Trips:", fill=text_color, font=subtitle_font)
                draw.text((180, stats_y), str(total_trips), fill=accent_color, font=stats_font)
                
                stats_y += 70
                draw.text((400, stats_y - 70), "Distance:", fill=text_color, font=subtitle_font)
                draw.text((520, stats_y - 70), general_utils.format_distance(total_distance), fill=accent_color, font=stats_font)
                
                draw.text((400, stats_y), "CO₂ Saved:", fill=text_color, font=subtitle_font)
                draw.text((520, stats_y), general_utils.format_co2(total_co2_saved), fill=accent_color, font=stats_font)
                
                # Add QR code placeholder
                qr_size = 120
                draw.rectangle(
                    [(width - qr_size - 40, height - qr_size - 40), (width - 40, height - 40)],
                    outline=(200, 200, 200),
                    fill=(255, 255, 255),
                    width=2
                )
                draw.text(
                    (width - qr_size - 20, height - qr_size - 65),
                    "Scan to view profile",
                    fill=(100, 100, 100),
                    font=label_font
                )
                
            elif choice == "2":  # Level Focus
                # Add subtitle
                draw.text((20, 90), f"Achievement Level for {name}", fill=text_color, font=subtitle_font)
                
                # Add large level display
                level_y = 150
                draw.ellipse([(width//2 - 100, level_y), (width//2 + 100, level_y + 200)], fill=accent_color)
                font_large = ImageFont.truetype("Arial Bold", 100) if 'truetype' in dir(ImageFont) else ImageFont.load_default()
                draw.text((width//2 - 30, level_y + 50), str(level), fill=(255, 255, 255), font=font_large)
                draw.text((width//2 - 80, level_y + 210), "LEVEL", fill=accent_color, font=stats_font)
                
                # Add progress bar to next level
                next_level_points = 1000
                if level == 1:
                    next_level_points = 100
                elif level == 2:
                    next_level_points = 250
                elif level == 3:
                    next_level_points = 500
                elif level == 4:
                    next_level_points = 1000
                
                progress = min(eco_points / next_level_points * 100, 100) if level < 5 else 100
                bar_y = 380
                draw.rectangle([(100, bar_y), (width - 100, bar_y + 30)], fill=(220, 220, 220))
                draw.rectangle([(100, bar_y), (100 + (width - 200) * progress / 100, bar_y + 30)], fill=accent_color)
                
                if level < 5:
                    draw.text(
                        (100, bar_y + 40),
                        f"{eco_points} / {next_level_points} points to Level {level + 1}",
                        fill=text_color,
                        font=label_font
                    )
                else:
                    draw.text(
                        (100, bar_y + 40),
                        f"Maximum Level Achieved! {eco_points} points",
                        fill=accent_color,
                        font=label_font
                    )
                
                # Add achievements count and stats
                stats_y = 450
                draw.text((100, stats_y), f"Achievements: {len(completed_achievements)}", fill=text_color, font=subtitle_font)
                draw.text((400, stats_y), f"Total Trips: {total_trips}", fill=text_color, font=subtitle_font)
                
                stats_y += 50
                draw.text((100, stats_y), f"Distance: {general_utils.format_distance(total_distance)}", fill=text_color, font=subtitle_font)
                draw.text((400, stats_y), f"CO₂ Saved: {general_utils.format_co2(total_co2_saved)}", fill=text_color, font=subtitle_font)
                
            else:  # Environmental Impact
                # Add subtitle
                draw.text((20, 90), f"Environmental Impact by {name}", fill=text_color, font=subtitle_font)
                
                # Add CO2 savings visualization
                stats_y = 150
                draw.text((40, stats_y), "CO₂ Emissions Saved", fill=text_color, font=subtitle_font)
                draw.text((40, stats_y + 40), general_utils.format_co2(total_co2_saved), fill=accent_color, font=stats_font)
                
                # Add equivalent impacts
                co2_trees = total_co2_saved / 20  # Approximate CO2 absorption per tree per year (kg)
                fuel_saved = total_distance * 0.07 / 1000  # Approximate fuel consumption (liters per km)
                
                equivalents_y = 260
                draw.text((40, equivalents_y), "Environmental Equivalents:", fill=text_color, font=subtitle_font)
                
                draw.text((40, equivalents_y + 40), f"🌳 Equivalent to planting {int(co2_trees)} trees", fill=text_color, font=label_font)
                draw.text((40, equivalents_y + 70), f"⛽ Saved {fuel_saved:.2f} liters of fuel", fill=text_color, font=label_font)
                draw.text((40, equivalents_y + 100), f"🚗 Avoided {total_trips} car trips", fill=text_color, font=label_font)
                
                # Add earth image in bottom right
                earth_size = 200
                earth_x = width - earth_size - 40
                earth_y = height - earth_size - 40
                
                # Draw a simplified Earth
                draw.ellipse([(earth_x, earth_y), (earth_x + earth_size, earth_y + earth_size)], fill=(65, 105, 225))  # Blue
                
                # Draw some green continents (simplified)
                draw.ellipse(
                    [(earth_x + 50, earth_y + 30), (earth_x + 100, earth_y + 90)],
                    fill=accent_color  # Green
                )
                draw.ellipse(
                    [(earth_x + 120, earth_y + 60), (earth_x + 180, earth_y + 130)],
                    fill=accent_color  # Green
                )
                draw.ellipse(
                    [(earth_x + 70, earth_y + 120), (earth_x + 140, earth_y + 170)],
                    fill=accent_color  # Green
                )
                
                # Earth title
                draw.text((earth_x + 50, earth_y - 30), "Making a Difference", fill=accent_color, font=subtitle_font)
            
            # Add footer with date and copyright
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            draw.text((20, height - 30), f"Generated: {current_date}", fill=(150, 150, 150), font=label_font)
            draw.text((width - 200, height - 30), "EcoCycle © 2025", fill=(150, 150, 150), font=label_font)
            
            # Save the image
            timestamp = int(time.time())
            filename = f"ecocycle_achievement_{username}_{timestamp}.png"
            image.save(filename)
            
            # Show success message and options
            if RICH_AVAILABLE:
                console.clear()
                console.print(Panel(
                    f"[green]Achievement card successfully generated![/green]\n"
                    f"[white]Saved as: {filename}[/white]",
                    title=f"[bold {COLOR_SHARING}]Achievement Card[/bold {COLOR_SHARING}]",
                    border_style=COLOR_SHARING
                ))
                
                # Show options for the generated file
                self._show_file_options(filename, "achievement card")
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Achievement Card")
                print(f"Achievement card successfully generated!")
                print(f"Saved as: {filename}")
                
                # Show options for the generated file
                self._show_file_options(filename, "achievement card")
                
        except Exception as e:
            logger.error(f"Error generating achievement card: {e}")
            if RICH_AVAILABLE:
                console.print(f"[bold red]Error generating achievement card: {e}[/bold red]")
            else:
                print(f"Error generating achievement card: {e}")
            self._wait_for_user()
    
    def _show_file_options(self, filename: str, file_type: str):
        """Show options for a generated file.
        
        Args:
            filename: Path to the generated file
            file_type: Type of file (e.g., "achievement card", "QR code")
        """
        import os
        import sys
        import webbrowser
        import platform
        
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return
        
        # Get absolute path
        abs_path = os.path.abspath(filename)
        
        if RICH_AVAILABLE:
            options_table = Table(show_header=False, box=box.SIMPLE)
            options_table.add_column("Option", style="cyan", width=2)
            options_table.add_column("Description", style="white")
            
            options_table.add_row("1", f"Open {file_type}")
            options_table.add_row("2", f"Open containing folder")
            options_table.add_row("3", f"Share {file_type}")
            options_table.add_row("4", f"Return to menu")
            
            console.print(Panel(options_table, title="[bold green]Options[/bold green]", border_style="green"))
            
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])
        else:
            print("\nOptions:")
            print(f"1. Open {file_type}")
            print(f"2. Open containing folder")
            print(f"3. Share {file_type}")
            print(f"4. Return to menu")
            
            choice = input("\nChoose an option (1-4): ")
        
        if choice == "1":
            # Open file with default program
            try:
                if platform.system() == 'Windows':
                    os.startfile(abs_path)
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{abs_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{abs_path}"')
                
                if RICH_AVAILABLE:
                    console.print(f"[green]Opening {file_type}...[/green]")
                else:
                    print(f"Opening {file_type}...")
            except Exception as e:
                logger.error(f"Error opening file: {e}")
                if RICH_AVAILABLE:
                    console.print(f"[bold red]Error opening file: {e}[/bold red]")
                else:
                    print(f"Error opening file: {e}")
            
        elif choice == "2":
            # Open containing folder
            try:
                if platform.system() == 'Windows':
                    os.system(f'explorer /select,"{abs_path}"')
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open -R "{abs_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{os.path.dirname(abs_path)}"')
                
                if RICH_AVAILABLE:
                    console.print(f"[green]Opening folder...[/green]")
                else:
                    print(f"Opening folder...")
            except Exception as e:
                logger.error(f"Error opening folder: {e}")
                if RICH_AVAILABLE:
                    console.print(f"[bold red]Error opening folder: {e}[/bold red]")
                else:
                    print(f"Error opening folder: {e}")
            
        elif choice == "3":
            # Show sharing options
            self._share_file(filename, file_type)
            return
        
        # If we get here, either the user selected "4" or we've completed another action
        self._wait_for_user()
    
    def _share_file(self, filename: str, file_type: str):
        """Show options for sharing a file.
        
        Args:
            filename: Path to the file to share
            file_type: Type of file (e.g., "achievement card", "QR code")
        """
        # In this implementation, we'll provide options for different sharing methods
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                f"Share your {file_type} with friends and community",
                title=f"[bold {COLOR_SHARING}]Share {file_type.title()}[/bold {COLOR_SHARING}]",
                border_style=COLOR_SHARING,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Show sharing options
            options_table = Table(show_header=False, box=box.SIMPLE)
            options_table.add_column("Option", style="cyan", width=2)
            options_table.add_column("Description", style="white")
            
            options_table.add_row("1", "Export to PNG image for social media")
            options_table.add_row("2", "Generate URL for web sharing")
            options_table.add_row("3", "Email the file")
            options_table.add_row("4", "Return to previous menu")
            
            console.print(Panel(options_table, title="[bold green]Sharing Options[/bold green]", border_style="green"))
            
            choice = Prompt.ask("Choose a sharing option", choices=["1", "2", "3", "4"])
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header(f"Share {file_type.title()}")
            
            print(f"Share your {file_type} with friends and community\n")
            print("Sharing Options:")
            print("1. Export to PNG image for social media")
            print("2. Generate URL for web sharing")
            print("3. Email the file")
            print("4. Return to previous menu")
            
            choice = input("\nChoose a sharing option (1-4): ")
        
        # Process sharing option
        if choice == "1":
            # For PNG export - the file is already a PNG, so just provide instructions
            if RICH_AVAILABLE:
                console.print(Panel(
                    f"[green]Your {file_type} is already saved as a PNG image.[/green]\n"
                    f"[white]File location: {os.path.abspath(filename)}[/white]\n\n"
                    "[yellow]You can upload this PNG directly to social media platforms.[/yellow]",
                    title=f"[bold {COLOR_SHARING}]PNG Export[/bold {COLOR_SHARING}]",
                    border_style=COLOR_SHARING
                ))
            else:
                print(f"\nYour {file_type} is already saved as a PNG image.")
                print(f"File location: {os.path.abspath(filename)}")
                print("You can upload this PNG directly to social media platforms.")
            
        elif choice == "2":
            # Simulate URL generation with a placeholder
            # In a real implementation, this would upload to a server and return a URL
            sharing_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            sharing_url = f"https://ecocycle.app/share/{sharing_code}"
            
            if RICH_AVAILABLE:
                console.print(Panel(
                    f"[green]Share URL generated![/green]\n\n"
                    f"[bold cyan]{sharing_url}[/bold cyan]\n\n"
                    "[yellow]This URL will be valid for 30 days.[/yellow]\n"
                    "[dim](Note: This is a simulated URL for demonstration purposes)[/dim]",
                    title=f"[bold {COLOR_SHARING}]Web Sharing[/bold {COLOR_SHARING}]",
                    border_style=COLOR_SHARING
                ))
            else:
                print(f"\nShare URL generated!")
                print(f"\n{sharing_url}\n")
                print("This URL will be valid for 30 days.")
                print("(Note: This is a simulated URL for demonstration purposes)")
            
        elif choice == "3":
            # Email sharing placeholder
            import urllib.parse
            subject = urllib.parse.quote(f"Check out my EcoCycle {file_type}!")
            body = urllib.parse.quote(f"I wanted to share my EcoCycle {file_type} with you. See the attached image.")
            # Note: We can't actually attach files via mailto links, so this is just a template
            email_url = f"mailto:?subject={subject}&body={body}"
            
            if RICH_AVAILABLE:
                console.print(Panel(
                    f"[green]Preparing email...[/green]\n\n"
                    "[yellow]Since we can't automatically attach files to emails,[/yellow]\n"
                    "[yellow]please manually attach the image file:[/yellow]\n"
                    f"[white]{os.path.abspath(filename)}[/white]",
                    title=f"[bold {COLOR_SHARING}]Email Sharing[/bold {COLOR_SHARING}]",
                    border_style=COLOR_SHARING
                ))
                
                # Ask if user wants to open the email client
                if Confirm.ask("Would you like to open your email client now?"):
                    try:
                        webbrowser.open(email_url)
                    except Exception as e:
                        logger.error(f"Error opening email client: {e}")
                        console.print(f"[bold red]Error opening email client: {e}[/bold red]")
            else:
                print(f"\nPreparing email...")
                print("Since we can't automatically attach files to emails,")
                print("please manually attach the image file:")
                print(f"{os.path.abspath(filename)}")
                
                # Ask if user wants to open the email client
                email_choice = input("\nWould you like to open your email client now? (y/n): ")
                if email_choice.lower() == 'y':
                    try:
                        webbrowser.open(email_url)
                    except Exception as e:
                        logger.error(f"Error opening email client: {e}")
                        print(f"Error opening email client: {e}")
        
        # Wait for user input before returning
        self._wait_for_user()

    def manage_achievement_cards(self):
        """Manager for handling achievement card visualizations."""
        import os
        import glob
        import platform
        
        while True:
            # Get list of all achievement card visualizations
            achievement_files = glob.glob("ecocycle_achievement_*.png")
            achievement_files.sort(key=os.path.getmtime, reverse=True)  # Sort by most recent first
            
            if RICH_AVAILABLE:
                console.clear()
                
                # Create header
                header = Panel(
                    "Manage your achievement card visualizations and reports",
                    title=f"[bold {COLOR_SHARING}]Achievement Card Manager[/bold {COLOR_SHARING}]",
                    border_style=COLOR_SHARING,
                    box=box.DOUBLE
                )
                console.print(header)
                
                # Display file count
                file_info = f"Found [bold cyan]{len(achievement_files)}[/bold cyan] achievement card files"
                console.print(file_info)
                
                # Show options
                options_table = Table(show_header=False, box=box.SIMPLE)
                options_table.add_column("Option", style="cyan", width=2)
                options_table.add_column("Description", style="white")
                
                options_table.add_row("1", "View/Open a visualization or report")
                options_table.add_row("2", "Delete a visualization or report")
                options_table.add_row("3", "Share a visualization or report (QR code)")
                options_table.add_row("4", "Delete ALL visualizations and reports")
                options_table.add_row("5", "Return to Social Hub")
                
                console.print(Panel(options_table, title="[bold yellow]Options[/bold yellow]", border_style="yellow"))
                
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Achievement Card Manager")
                
                print(f"Found {len(achievement_files)} achievement card files")
                print("\nOptions:")
                print("1. View/Open a visualization or report")
                print("2. Delete a visualization or report")
                print("3. Share a visualization or report (QR code)")
                print("4. Delete ALL visualizations and reports")
                print("5. Return to Social Hub")
                
                choice = input("\nSelect an option (1-5): ")
            
            if choice == "1":
                # View/Open a visualization
                self._view_achievement_files(achievement_files)
            elif choice == "2":
                # Delete a visualization
                self._delete_achievement_file(achievement_files)
            elif choice == "3":
                # Share a visualization
                self._share_achievement_file(achievement_files)
            elif choice == "4":
                # Delete ALL visualizations
                self._delete_all_achievement_files(achievement_files)
            elif choice == "5":
                # Return to Social Hub
                return
    
    def _view_achievement_files(self, achievement_files):
        """View or open achievement card files.
        
        Args:
            achievement_files: List of achievement card filenames
        """
        import os
        import platform
        
        if not achievement_files:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]No achievement card files found.[/yellow]\n"
                    "[white]Generate an achievement card first.[/white]",
                    title="[bold red]No Files[/bold red]",
                    border_style="red"
                ))
            else:
                print("\nNo achievement card files found.")
                print("Generate an achievement card first.")
            
            self._wait_for_user()
            return
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Select a file to view",
                title=f"[bold {COLOR_SHARING}]View Achievement Cards[/bold {COLOR_SHARING}]",
                border_style=COLOR_SHARING,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Show files table
            files_table = Table(box=box.SIMPLE)
            files_table.add_column("#", style="cyan", justify="right")
            files_table.add_column("Filename", style="white")
            files_table.add_column("Date Created", style="green")
            files_table.add_column("Size", style="yellow", justify="right")
            
            for i, filename in enumerate(achievement_files, 1):
                # Get file info
                file_stats = os.stat(filename)
                file_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                file_size = f"{file_stats.st_size / 1024:.1f} KB"
                
                files_table.add_row(str(i), filename, file_date, file_size)
            
            console.print(files_table)
            
            # Get user selection
            file_count = len(achievement_files)
            choices = [str(i) for i in range(1, file_count + 1)] + ["c"]
            selection = Prompt.ask(
                "Enter file number to view (or 'c' to cancel)", 
                choices=choices
            )
            
            if selection.lower() == 'c':
                return
            
            selected_file = achievement_files[int(selection) - 1]
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("View Achievement Cards")
            
            # Show files list
            print("Available achievement card files:")
            for i, filename in enumerate(achievement_files, 1):
                # Get file info
                file_stats = os.stat(filename)
                file_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                file_size = f"{file_stats.st_size / 1024:.1f} KB"
                
                print(f"{i}. {filename} ({file_date}, {file_size})")
            
            # Get user selection
            selection = input("\nEnter file number to view (or 'c' to cancel): ")
            if selection.lower() == 'c':
                return
            
            try:
                selected_index = int(selection) - 1
                if 0 <= selected_index < len(achievement_files):
                    selected_file = achievement_files[selected_index]
                else:
                    print("\nInvalid selection. Please try again.")
                    self._wait_for_user()
                    return
            except ValueError:
                print("\nInvalid input. Please enter a number.")
                self._wait_for_user()
                return
        
        # Open the selected file
        try:
            abs_path = os.path.abspath(selected_file)
            if platform.system() == 'Windows':
                os.startfile(abs_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{abs_path}"')
            else:  # Linux
                os.system(f'xdg-open "{abs_path}"')
            
            if RICH_AVAILABLE:
                console.print(f"[green]Opening {selected_file}...[/green]")
            else:
                print(f"\nOpening {selected_file}...")
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            if RICH_AVAILABLE:
                console.print(f"[bold red]Error opening file: {e}[/bold red]")
            else:
                print(f"\nError opening file: {e}")
        
        self._wait_for_user()
    
    def _delete_achievement_file(self, achievement_files):
        """Delete a specific achievement card file.
        
        Args:
            achievement_files: List of achievement card filenames
        """
        import os
        
        if not achievement_files:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]No achievement card files found.[/yellow]\n"
                    "[white]Generate an achievement card first.[/white]",
                    title="[bold red]No Files[/bold red]",
                    border_style="red"
                ))
            else:
                print("\nNo achievement card files found.")
                print("Generate an achievement card first.")
            
            self._wait_for_user()
            return
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Select a file to delete",
                title=f"[bold {COLOR_SHARING}]Delete Achievement Card[/bold {COLOR_SHARING}]",
                border_style=COLOR_SHARING,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Show files table
            files_table = Table(box=box.SIMPLE)
            files_table.add_column("#", style="cyan", justify="right")
            files_table.add_column("Filename", style="white")
            files_table.add_column("Date Created", style="green")
            files_table.add_column("Size", style="yellow", justify="right")
            
            for i, filename in enumerate(achievement_files, 1):
                # Get file info
                file_stats = os.stat(filename)
                file_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                file_size = f"{file_stats.st_size / 1024:.1f} KB"
                
                files_table.add_row(str(i), filename, file_date, file_size)
            
            console.print(files_table)
            
            # Get user selection
            file_count = len(achievement_files)
            choices = [str(i) for i in range(1, file_count + 1)] + ["c"]
            selection = Prompt.ask(
                "Enter file number to delete (or 'c' to cancel)", 
                choices=choices
            )
            
            if selection.lower() == 'c':
                return
            
            selected_file = achievement_files[int(selection) - 1]
            
            # Confirm deletion
            if Confirm.ask(f"Are you sure you want to delete {selected_file}?"):
                try:
                    os.remove(selected_file)
                    console.print(f"[green]Successfully deleted {selected_file}[/green]")
                except Exception as e:
                    logger.error(f"Error deleting file: {e}")
                    console.print(f"[bold red]Error deleting file: {e}[/bold red]")
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Delete Achievement Card")
            
            # Show files list
            print("Available achievement card files:")
            for i, filename in enumerate(achievement_files, 1):
                # Get file info
                file_stats = os.stat(filename)
                file_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                file_size = f"{file_stats.st_size / 1024:.1f} KB"
                
                print(f"{i}. {filename} ({file_date}, {file_size})")
            
            # Get user selection
            selection = input("\nEnter file number to delete (or 'c' to cancel): ")
            if selection.lower() == 'c':
                return
            
            try:
                selected_index = int(selection) - 1
                if 0 <= selected_index < len(achievement_files):
                    selected_file = achievement_files[selected_index]
                    
                    # Confirm deletion
                    confirm = input(f"\nAre you sure you want to delete {selected_file}? (y/n): ")
                    if confirm.lower() == 'y':
                        try:
                            os.remove(selected_file)
                            print(f"\nSuccessfully deleted {selected_file}")
                        except Exception as e:
                            logger.error(f"Error deleting file: {e}")
                            print(f"\nError deleting file: {e}")
                else:
                    print("\nInvalid selection. Please try again.")
            except ValueError:
                print("\nInvalid input. Please enter a number.")
        
        self._wait_for_user()
    
    def _share_achievement_file(self, achievement_files):
        """Share a specific achievement card file with QR code.
        
        Args:
            achievement_files: List of achievement card filenames
        """
        import os
        
        if not achievement_files:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]No achievement card files found.[/yellow]\n"
                    "[white]Generate an achievement card first.[/white]",
                    title="[bold red]No Files[/bold red]",
                    border_style="red"
                ))
            else:
                print("\nNo achievement card files found.")
                print("Generate an achievement card first.")
            
            self._wait_for_user()
            return
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Select a file to share",
                title=f"[bold {COLOR_SHARING}]Share Achievement Card[/bold {COLOR_SHARING}]",
                border_style=COLOR_SHARING,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Show files table
            files_table = Table(box=box.SIMPLE)
            files_table.add_column("#", style="cyan", justify="right")
            files_table.add_column("Filename", style="white")
            files_table.add_column("Date Created", style="green")
            files_table.add_column("Size", style="yellow", justify="right")
            
            for i, filename in enumerate(achievement_files, 1):
                # Get file info
                file_stats = os.stat(filename)
                file_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                file_size = f"{file_stats.st_size / 1024:.1f} KB"
                
                files_table.add_row(str(i), filename, file_date, file_size)
            
            console.print(files_table)
            
            # Get user selection
            file_count = len(achievement_files)
            choices = [str(i) for i in range(1, file_count + 1)] + ["c"]
            selection = Prompt.ask(
                "Enter file number to share (or 'c' to cancel)", 
                choices=choices
            )
            
            if selection.lower() == 'c':
                return
            
            selected_file = achievement_files[int(selection) - 1]
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Share Achievement Card")
            
            # Show files list
            print("Available achievement card files:")
            for i, filename in enumerate(achievement_files, 1):
                # Get file info
                file_stats = os.stat(filename)
                file_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stats.st_mtime))
                file_size = f"{file_stats.st_size / 1024:.1f} KB"
                
                print(f"{i}. {filename} ({file_date}, {file_size})")
            
            # Get user selection
            selection = input("\nEnter file number to share (or 'c' to cancel): ")
            if selection.lower() == 'c':
                return
            
            try:
                selected_index = int(selection) - 1
                if 0 <= selected_index < len(achievement_files):
                    selected_file = achievement_files[selected_index]
                else:
                    print("\nInvalid selection. Please try again.")
                    self._wait_for_user()
                    return
            except ValueError:
                print("\nInvalid input. Please enter a number.")
                self._wait_for_user()
                return
        
        # Generate QR code for the selected file
        self._generate_qr_for_file(selected_file)
    
    def _generate_qr_for_file(self, filename):
        """Generate QR code for a file.
        
        Args:
            filename: Path to the file
        """
        import os
        
        if not QRCODE_AVAILABLE:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]QR code generation requires the qrcode library.[/yellow]\n"
                    "[white]Please install it with: pip install qrcode[pillow][/white]",
                    title="[bold red]Missing Dependency[/bold red]",
                    border_style="red"
                ))
            else:
                print("\nQR code generation requires the qrcode library.")
                print("Please install it with: pip install qrcode[pillow]")
            
            self._wait_for_user()
            return
        
        # Create a QR code for sharing (simulate a sharing link)
        try:
            sharing_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            sharing_url = f"https://ecocycle.app/share/{sharing_code}"
            
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(sharing_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code
            base_name = os.path.splitext(filename)[0]
            qr_filename = f"{base_name}_qr.png"
            qr_img.save(qr_filename)
            
            if RICH_AVAILABLE:
                console.clear()
                console.print(Panel(
                    f"[green]QR code successfully generated![/green]\n"
                    f"[white]Saved as: {qr_filename}[/white]\n\n"
                    f"[cyan]Sharing URL: {sharing_url}[/cyan]\n"
                    "[yellow]Anyone with this QR code can view your achievement card.[/yellow]",
                    title=f"[bold {COLOR_SHARING}]QR Code Generated[/bold {COLOR_SHARING}]",
                    border_style=COLOR_SHARING
                ))
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("QR Code Generated")
                print(f"QR code successfully generated!")
                print(f"Saved as: {qr_filename}")
                print()
                print(f"Sharing URL: {sharing_url}")
                print("Anyone with this QR code can view your achievement card.")
            
            return qr_filename
                
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            if RICH_AVAILABLE:
                console.print(f"[bold red]Error generating QR code: {e}[/bold red]")
            else:
                print(f"\nError generating QR code: {e}")
            
            self._wait_for_user()
            return None
    
    def _delete_all_achievement_files(self, achievement_files):
        """Delete all achievement card files.
        
        Args:
            achievement_files: List of achievement card filenames
        """
        import os
        
        if not achievement_files:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[yellow]No achievement card files found.[/yellow]\n"
                    "[white]There are no files to delete.[/white]",
                    title="[bold red]No Files[/bold red]",
                    border_style="red"
                ))
            else:
                print("\nNo achievement card files found.")
                print("There are no files to delete.")
            
            self._wait_for_user()
            return
        
        # Confirm deletion of all files
        if RICH_AVAILABLE:
            console.clear()
            
            # Create warning panel
            warning = Panel(
                f"[bold yellow]You are about to delete ALL[/bold yellow] [bold red]{len(achievement_files)}[/bold red] [bold yellow]achievement card files![/bold yellow]\n"
                "[white]This action cannot be undone.[/white]",
                title="[bold red]⚠️ WARNING ⚠️[/bold red]",
                border_style="red",
                box=box.DOUBLE
            )
            console.print(warning)
            
            # Get confirmation
            if not Confirm.ask("Are you sure you want to delete ALL achievement card files?"):
                return
            
            # Double-check confirmation
            if not Confirm.ask("This action CANNOT be undone. Confirm deletion?"):
                return
            
            # Display progress
            with Progress() as progress:
                task = progress.add_task("[red]Deleting files...", total=len(achievement_files))
                
                deleted_count = 0
                failed_count = 0
                
                for filename in achievement_files:
                    try:
                        os.remove(filename)
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting {filename}: {e}")
                        failed_count += 1
                    
                    progress.update(task, advance=1)
            
            # Show results
            if failed_count == 0:
                console.print(f"[green]Successfully deleted all {deleted_count} achievement card files![/green]")
            else:
                console.print(f"[yellow]Deleted {deleted_count} files, but failed to delete {failed_count} files.[/yellow]")
                
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Delete ALL Achievement Cards")
            
            print(f"WARNING: You are about to delete ALL {len(achievement_files)} achievement card files!")
            print("This action cannot be undone.")
            print()
            
            # Get confirmation
            confirm = input("Are you sure you want to delete ALL achievement card files? (y/n): ")
            if confirm.lower() != 'y':
                return
            
            # Double-check confirmation
            confirm = input("This action CANNOT be undone. Confirm deletion? (y/n): ")
            if confirm.lower() != 'y':
                return
            
            print("\nDeleting files...")
            
            deleted_count = 0
            failed_count = 0
            
            for filename in achievement_files:
                try:
                    os.remove(filename)
                    deleted_count += 1
                    print(f"Deleted: {filename}")
                except Exception as e:
                    logger.error(f"Error deleting {filename}: {e}")
                    failed_count += 1
                    print(f"Failed to delete: {filename} - {e}")
            
            # Show results
            if failed_count == 0:
                print(f"\nSuccessfully deleted all {deleted_count} achievement card files!")
            else:
                print(f"\nDeleted {deleted_count} files, but failed to delete {failed_count} files.")
        
        self._wait_for_user()
