"""
GUI Logger component for Modern Logger.

This module provides a Qt-based graphical user interface for logging.
"""

from PySide6.QtWidgets import QTextEdit, QLabel, QApplication, QWidget, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QSize, QPropertyAnimation, QPoint, QRectF, QEasingCurve, QEvent, QObject
from PySide6.QtGui import QTextCursor, QColor, QPainter, QPen, QFont, QPainterPath, QBrush, QLinearGradient, QIcon
import math
from datetime import datetime
import queue
import re
import traceback
import sys
import time


class ColorfulLineIndicator(QWidget):
    """A colorful line loading indicator that appears at the bottom of the ModernLogger"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(5)  # 5px height as requested
        self.hide()
        
        # Animation properties - increase speed
        self._segment_position = 0
        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(15)  # Faster updates (15ms instead of 30ms)
        self._animation_timer.timeout.connect(self._update_animation)
        
        # Enhanced color configuration - more vibrant and dominant pinks
        self._base_color = QColor(235, 100, 150)  # Saturated pink base color
        self._highlight_color = QColor(255, 240, 245)  # Softer, less intense white/pink highlight
        self._deep_color = QColor(215, 30, 150)  # Deeper, more intense pink
        self._ultra_soft_color = QColor(245, 235, 240, 0)  # Transparent color for edges
        self._mid_transition = QColor(230, 140, 165, 65)  # Stronger mid transition color with more opacity
        
        # Make widget fully transparent when not active
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAutoFillBackground(False)
        
        # Ensure widget has no focus effects and isn't part of tab order
        self.setFocusPolicy(Qt.NoFocus)
        
    def _update_animation(self):
        """Update animation state and repaint with faster movement"""
        # Faster movement for more dynamic animation
        self._segment_position = (self._segment_position + 0.7) % 100  # Much faster (0.7 instead of 0.3)
        
        # Repaint the widget
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event to draw the animated line"""
        # Skip painting when not visible
        if not self.isVisible():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Create full-width background with more pink tint
        bg_gradient = QLinearGradient(0, 0, width, 0)
        
        # Use gradient stops for ultra-smooth background but with more pink
        for i in range(51):
            pos = i / 50.0
            
            # Use sine-based weighting but with higher amplitude for more color
            weight = math.pow(math.sin(pos * math.pi), 2) * 0.3  # Increased amplitude (0.3 vs 0.25)
            
            # Create a pinker background with less transparency
            r = int(self._base_color.red() * 0.9 + self._highlight_color.red() * 0.1)
            g = int(self._base_color.green() * 0.9 + self._highlight_color.green() * 0.1)
            b = int(self._base_color.blue() * 0.9 + self._highlight_color.blue() * 0.1)
            
            # Alpha varies with higher minimum value for more opacity
            alpha = int(18 + 25 * weight)  # 18-43 alpha range for more visibility
            bg_gradient.setColorAt(pos, QColor(r, g, b, alpha))
            
        painter.fillRect(0, 0, width, height, bg_gradient)
        
        # Draw a segment that moves across the width
        segment_width = width * 0.9  # Wider segment for more pink coverage
        
        # Calculate segment's starting position
        segment_start_x = width * (self._segment_position / 100.0) - segment_width * 0.45
        
        # Use linear gradient for the animated segment
        segment_gradient = QLinearGradient(segment_start_x, 0, segment_start_x + segment_width, 0)
        
        # Modified color distribution - much more pink dominant portions
        for i in range(0, 101):  # Increased resolution for smoother gradient
            pos = i / 100.0
            
            # Use a modified curve for higher opacity in middle sections
            t_raw = (1 - math.cos(pos * 2 * math.pi)) / 2
            
            # Edge smoothing with higher minimum values
            if pos < 0.05:  # First 5% - soft start but more visible
                t = t_raw * math.pow(pos / 0.05, 2)  # Quadratic smoothing
            elif pos > 0.95:  # Last 5% - soft end but more visible
                t = t_raw * math.pow((1 - (pos - 0.95) / 0.05), 2)  # Quadratic smoothing
            else:
                # Enhanced curve in the middle for more color vibrancy
                t = t_raw * 1.25  # Amplify the middle values by 25% (increased from 1.2)
                t = min(t, 1.0)  # Cap at 1.0
                
            # Make the overall effect stronger
            weight = t * 0.8  # Increased from 0.7 to 0.8 for more intensity
            
            # REVISED COLOR ZONES - LONGER PINK, SHORTER WHITE
            if pos < 0.03:  # Ultra-short start transition (3% vs 5%)
                # Short ultra-soft start to base - quick transition
                blend = pos / 0.03
                r = int(self._ultra_soft_color.red() * (1 - blend) + self._base_color.red() * blend)
                g = int(self._ultra_soft_color.green() * (1 - blend) + self._base_color.green() * blend)
                b = int(self._ultra_soft_color.blue() * (1 - blend) + self._base_color.blue() * blend)
                alpha = int(blend * blend * 45)  # Slightly higher start alpha
            elif pos < 0.25:  # Extended base to mid-transition (25% vs 20%)
                # Base to mid-transition color - longer transition
                blend = (pos - 0.03) / 0.22
                r = int(self._base_color.red() * (1 - blend) + self._mid_transition.red() * blend)
                g = int(self._base_color.green() * (1 - blend) + self._mid_transition.green() * blend)
                b = int(self._base_color.blue() * (1 - blend) + self._mid_transition.blue() * blend)
                alpha = int(45 + blend * 35)  # 45-80 range - higher starting point
            elif pos < 0.45:  # Extended mid to deep transition (20% vs 15%)
                # Mid-transition to deep - longer deep pink section
                blend = (pos - 0.25) / 0.20
                r = int(self._mid_transition.red() * (1 - blend) + self._deep_color.red() * blend)
                g = int(self._mid_transition.green() * (1 - blend) + self._deep_color.green() * blend)
                b = int(self._mid_transition.blue() * (1 - blend) + self._deep_color.blue() * blend)
                alpha = int(80 + blend * 140)  # 80-220 range - higher opacity
            elif pos < 0.55:  # Shorter highlight section (10% vs 25%)
                # Deep to highlight (peak) - compressed highlight section 
                blend = (pos - 0.45) / 0.10
                r = int(self._deep_color.red() * (1 - blend) + self._highlight_color.red() * blend)
                g = int(self._deep_color.green() * (1 - blend) + self._highlight_color.green() * blend)
                b = int(self._deep_color.blue() * (1 - blend) + self._highlight_color.blue() * blend)
                alpha = int(220 + blend * 35)  # 220-255 range (peak)
            elif pos < 0.75:  # Extended highlight to mid section (20% vs 15%)
                # Highlight to mid-transition - longer section
                blend = (pos - 0.55) / 0.20
                r = int(self._highlight_color.red() * (1 - blend) + self._mid_transition.red() * blend)
                g = int(self._highlight_color.green() * (1 - blend) + self._mid_transition.green() * blend)
                b = int(self._highlight_color.blue() * (1 - blend) + self._mid_transition.blue() * blend)
                alpha = int(255 - blend * 175)  # 255-80 range
            elif pos < 0.97:  # Extended mid to base (22% vs 10%)
                # Mid-transition to base - longer fade out
                blend = (pos - 0.75) / 0.22
                r = int(self._mid_transition.red() * (1 - blend) + self._base_color.red() * blend)
                g = int(self._mid_transition.green() * (1 - blend) + self._base_color.green() * blend)
                b = int(self._mid_transition.blue() * (1 - blend) + self._base_color.blue() * blend)
                alpha = int(80 - blend * 35)  # 80-45 range
            else:  # Short ultra-soft end (3% vs 5%)
                # Base to ultra-soft end - quick transition
                blend = (pos - 0.97) / 0.03
                r = int(self._base_color.red() * (1 - blend) + self._ultra_soft_color.red() * blend)
                g = int(self._base_color.green() * (1 - blend) + self._ultra_soft_color.green() * blend)
                b = int(self._base_color.blue() * (1 - blend) + self._ultra_soft_color.blue() * blend)
                alpha = int(45 * (1 - blend * blend))  # Higher ending alpha
            
            # Extra safeguard for alpha bounds
            alpha = max(0, min(255, alpha))
            
            # Add color stop with the adjusted alpha value
            segment_gradient.setColorAt(pos, QColor(r, g, b, alpha))
        
        # Add edge stops to ensure no hard edges
        segment_gradient.setColorAt(0, QColor(self._ultra_soft_color.red(), 
                                           self._ultra_soft_color.green(), 
                                           self._ultra_soft_color.blue(), 0))
        segment_gradient.setColorAt(1, QColor(self._ultra_soft_color.red(), 
                                           self._ultra_soft_color.green(), 
                                           self._ultra_soft_color.blue(), 0))
        
        # Draw the segment with the enhanced gradient
        painter.fillRect(segment_start_x, 0, segment_width, height, segment_gradient)
    
    def start_animation(self):
        """Start the line animation"""
        self._segment_position = 0
        self.show()
        self._animation_timer.start()
    
    def stop_animation(self):
        """Stop the line animation"""
        self._animation_timer.stop()
        self.hide()
        
        # Force a repaint to ensure the widget becomes transparent
        self.update()


class ScrollToBottomButton(QPushButton):
    """A floating button that scrolls the logger to the bottom when clicked"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure button appearance
        self.setFixedSize(36, 36)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(235, 100, 150, 140);
                border-radius: 18px;
                border: none;
                color: white;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(235, 100, 150, 180);
            }
            QPushButton:pressed {
                background-color: rgba(215, 30, 150, 180);
            }
        """)
        
        # Use a down arrow character as the button text
        self.setText("↓")
        self.setFont(QFont("Arial", 16, QFont.Bold))
        
        # Add a drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 2)
        shadow.setBlurRadius(6)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        # Hide by default
        self.hide()
        
        # Animation for appearing/disappearing
        self._opacity = 0.0
        self._animation = QPropertyAnimation(self, b"windowOpacity")
        self._animation.setDuration(200)  # 200ms animation
        
        # Make sure button is above other content
        self.raise_()
        
        # Ensure button doesn't interfere with text selection
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
    def customize_appearance(self, size=None, background_color=None, hover_color=None, 
                            pressed_color=None, text=None, font=None, animation_duration=None,
                            shadow_enabled=True, shadow_color=None, shadow_blur=None, shadow_offset=None):
        """
        Customize the appearance of the scroll button
        
        Args:
            size (int, optional): Size of the button in pixels (button is square). Defaults to None.
            background_color (str, optional): Background color in CSS format. Defaults to None.
            hover_color (str, optional): Hover color in CSS format. Defaults to None.
            pressed_color (str, optional): Pressed color in CSS format. Defaults to None.
            text (str, optional): Button text. Defaults to None.
            font (QFont, optional): Button font. Defaults to None.
            animation_duration (int, optional): Duration of show/hide animations in ms. Defaults to None.
            shadow_enabled (bool, optional): Whether to show shadow. Defaults to True.
            shadow_color (QColor, optional): Shadow color. Defaults to None.
            shadow_blur (int, optional): Shadow blur radius. Defaults to None.
            shadow_offset (tuple, optional): Shadow offset (x, y). Defaults to None.
        """
        # Update size if specified
        if size is not None:
            self.setFixedSize(size, size)
            # Update border radius to half the size for a circular button
            border_radius = size // 2
        else:
            # Use current size
            border_radius = self.width() // 2
            
        # Prepare style sheet components
        bg_color = background_color or "rgba(235, 100, 150, 180)"
        h_color = hover_color or "rgba(235, 100, 150, 220)"
        p_color = pressed_color or "rgba(215, 30, 150, 220)"
        
        # Create and apply style sheet
        style_sheet = f"""
            QPushButton {{
                background-color: {bg_color};
                border-radius: {border_radius}px;
                border: none;
                color: white;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {h_color};
            }}
            QPushButton:pressed {{
                background-color: {p_color};
            }}
        """
        self.setStyleSheet(style_sheet)
        
        # Update text if specified
        if text is not None:
            self.setText(text)
            
        # Update font if specified
        if font is not None:
            self.setFont(font)
            
        # Update animation duration if specified
        if animation_duration is not None:
            self._animation.setDuration(animation_duration)
            
        # Update shadow effect
        if shadow_enabled:
            # Create new shadow or get existing one
            current_effect = self.graphicsEffect()
            shadow = current_effect if isinstance(current_effect, QGraphicsDropShadowEffect) else QGraphicsDropShadowEffect(self)
            
            # Update shadow properties if specified
            if shadow_offset is not None:
                shadow.setOffset(shadow_offset[0], shadow_offset[1])
            if shadow_blur is not None:
                shadow.setBlurRadius(shadow_blur)
            if shadow_color is not None:
                shadow.setColor(shadow_color)
                
            # Apply shadow if it's new
            if shadow != current_effect:
                self.setGraphicsEffect(shadow)
        else:
            # Remove shadow if disabled
            self.setGraphicsEffect(None)
        
    def show_animated(self):
        """Show the button with a fade-in animation"""
        if self.isVisible() and self.windowOpacity() > 0.9:
            return
            
        # Disconnect any existing connections to prevent memory leaks
        try:
            # Check if the signal has any connections before disconnecting
            if self._animation.receivers(self._animation.finished) > 0:
                self._animation.finished.disconnect()
        except (RuntimeError, TypeError):
            # No connections to disconnect or other error
            pass
            
        self._animation.stop()
        self.setWindowOpacity(self.windowOpacity())  # Ensure opacity property is set
        self._animation.setStartValue(self.windowOpacity())
        self._animation.setEndValue(1.0)
        self.show()
        self._animation.start()
        
    def hide_animated(self):
        """Hide the button with a fade-out animation"""
        if not self.isVisible() or self.windowOpacity() < 0.1:
            self.hide()
            return
            
        # Disconnect any existing connections to prevent memory leaks
        try:
            # Check if the signal has any connections before disconnecting
            if self._animation.receivers(self._animation.finished) > 0:
                self._animation.finished.disconnect()
        except (RuntimeError, TypeError):
            # No connections to disconnect or other error
            pass
            
        self._animation.stop()
        self.setWindowOpacity(self.windowOpacity())  # Ensure opacity property is set
        self._animation.setStartValue(self.windowOpacity())
        self._animation.setEndValue(0.0)
        
        # Connect to animation finished signal to hide the button
        self._animation.finished.connect(self._on_hide_animation_finished)
        self._animation.start()
        
    def _on_hide_animation_finished(self):
        """Handle animation finished event"""
        # Disconnect to prevent memory leaks
        try:
            # Check if the signal has any connections before disconnecting
            if self._animation.receivers(self._animation.finished) > 0:
                self._animation.finished.disconnect(self._on_hide_animation_finished)
        except (RuntimeError, TypeError):
            # No connections to disconnect or other error
            pass
        
        # Hide the button if opacity is near zero
        if self.windowOpacity() < 0.1:
            self.hide()


class ModernLogger(QTextEdit):
    """
    A QTextEdit-based modern logger that displays timestamped messages
    and supports a non-blocking loading indicator.
    """
    
    # Keep the signal for internal use, but we won't show the label anymore
    scroll_state_changed = Signal(bool)  # True when at bottom, False when scrolled up

    def __init__(self, parent=None, queue_messages=True, auto_process_events=True):
        super().__init__(parent)
        self.setReadOnly(True)
        
        # Document configuration
        doc = self.document()
        doc.setDocumentMargin(8)
        doc.setUndoRedoEnabled(False)
        doc.setMaximumBlockCount(5000)
        
        # Message queue settings
        self._queue_messages = queue_messages
        self._passthrough_messages = False
        self._message_queue = queue.Queue()
        
        # Timestamp format
        self._timestamp_format = "[%Y-%m-%d %H:%M:%S]"
        
        # Batch processing
        self._batch_timer = QTimer(self)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._process_batch)
        self._pending_batch = []
        
        # Scroll management
        self._auto_scroll_enabled = True
        self._user_has_scrolled = False
        self._last_known_position = 0
        self._was_at_bottom = True  # Start assuming at bottom
        self._preserve_scroll_state = False
        self._saved_scroll_position = 0
        self._saved_scroll_percentage = 0
        
        # Event processing settings
        self._auto_process_events = auto_process_events
        self._event_processing_count = 0
        self._event_processing_threshold = 5  # Process events after every 5 operations
        self._last_event_process_time = None
        
        # Connect scroll signals
        scrollbar = self.verticalScrollBar()
        scrollbar.valueChanged.connect(self._on_scroll)
        scrollbar.sliderPressed.connect(self._on_user_scroll_start)
        scrollbar.sliderReleased.connect(self._on_user_scroll_end)
        
        # Loading state
        self._loading = False
        
        # Create line loading indicator at bottom only - no more floating label
        self._line_indicator = ColorfulLineIndicator(self)
        self._update_line_indicator_position()
        self._line_indicator.hide()  # Ensure it's hidden by default
        
        # Create scroll-to-bottom button
        self._scroll_button = ScrollToBottomButton(self)
        self._update_scroll_button_position()
        self._scroll_button.clicked.connect(self._on_scroll_button_clicked)
        
        # First-run flag
        self._first_content = True
        
        # Inline progress update settings
        self._inline_progress_update = False
        self._progress_current = 0
        self._progress_total = 100
        self._progress_message_id = None
        
        # Install event filter to handle resize events
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filter events to handle resize and other events"""
        if obj == self and event.type() == QEvent.Type.Resize:
            # Update button position on resize
            self._update_scroll_button_position()
            
        return super().eventFilter(obj, event)

    def _process_batch(self):
        """Process pending message batch"""
        try:
            if not self._pending_batch:
                return
            
            # Save scroll info
            was_at_bottom = self._is_at_bottom()
            
            # Save scroll position if not at bottom
            if not was_at_bottom:
                self._save_scroll_position()
                self._preserve_scroll_state = True
            else:
                # Make sure we track that we're at the bottom
                self._preserve_scroll_state = False
            
            # Append all messages
            for message in self._pending_batch:
                super().append(message)
            
            # Clear batch
            self._pending_batch.clear()
            
            # Handle scrolling - respect the auto_scroll_enabled flag
            if not self._auto_scroll_enabled and self._preserve_scroll_state:
                # We're not at the bottom and auto-scroll is disabled
                self._restore_scroll_position()
                
                # Show scroll button since we're not at bottom
                if hasattr(self, '_scroll_button'):
                    self._scroll_button.show_animated()
            elif self._auto_scroll_enabled and (was_at_bottom or self._first_content):
                # We were at the bottom and auto-scroll is enabled
                self._do_auto_scroll()
                self._first_content = False
                
                # Hide scroll button since we're at bottom - use immediate hide
                if hasattr(self, '_scroll_button'):
                    self._scroll_button.hide()
            
            # Process events after batch processing
            self._process_events_if_needed()
            
            # Ensure loading indicator remains visible if we're in loading state
            if self._loading and hasattr(self, '_line_indicator'):
                self._line_indicator.show()
                self._update_line_indicator_position()
                
            # Update scroll button position
            self._update_scroll_button_position()
                
        except Exception as e:
            print(f"Error in _process_batch: {traceback.format_exc()}", file=sys.stderr)
            self._pending_batch.clear()
    
    def append_message(self, text):
        """Add a timestamped message"""
        try:
            # Create timestamp
            timestamp = datetime.now().strftime(self._timestamp_format + " ")
            full_message = f"{timestamp}{text}"
            
            # Queue or batch based on mode
            if self._loading and self._queue_messages and not self._passthrough_messages:
                self._message_queue.put(full_message)
            else:
                self._pending_batch.append(full_message)
                
                # Process immediately or schedule
                if len(self._pending_batch) == 1:
                    self._batch_timer.start(0)
                elif len(self._pending_batch) >= 10:
                    self._batch_timer.stop()
                    self._process_batch()
                    
                # Ensure loading indicator remains visible if we're in loading state
                if self._loading and hasattr(self, '_line_indicator'):
                    self._line_indicator.show()
                    self._update_line_indicator_position()
        except Exception as e:
            print(f"Error in append_message: {traceback.format_exc()}", file=sys.stderr)
    
    def append(self, text):
        """Overridden append method"""
        # Use built-in append
        super().append(text)
        
        # Auto-scroll as needed
        if self._auto_scroll_enabled:
            self._do_auto_scroll()
            
        # Ensure loading indicator remains visible if we're in loading state
        if self._loading and hasattr(self, '_line_indicator'):
            self._line_indicator.show()
            self._update_line_indicator_position()
    
    def set_loading_on(self, queue_messages=None, passthrough_messages=False, inline_update=False):
        """
        Activate the loading indicator
        
        Args:
            queue_messages (bool, optional): Whether to queue messages while loading. Defaults to None (use current setting).
            passthrough_messages (bool, optional): Whether to show messages immediately while loading. Defaults to False.
            inline_update (bool, optional): Whether to enable inline progress updates. Defaults to False.
        """
        try:
            # Determine if currently at the bottom before any changes
            was_at_bottom = self._is_at_bottom()
            
            # Save scroll position for potential restoration
            self._save_scroll_position()
            
            # Update settings
            if queue_messages is not None:
                self._queue_messages = queue_messages
            self._passthrough_messages = passthrough_messages
            
            # Save the original auto-scroll state
            self._pre_inline_auto_scroll_state = self._auto_scroll_enabled
            
            # Set inline progress update mode and reset progress
            self._inline_progress_update = inline_update
            self._progress_current = 0
            self._progress_total = 100
            self._progress_message_id = None
            
            # Process any pending batch messages
            self._process_batch()
            
            # Set loading state
            self._loading = True
            
            # Start the line animation
            if hasattr(self, '_line_indicator'):
                # Update position before showing
                self._update_line_indicator_position()
                self._line_indicator.start_animation()
                # Ensure it's visible and on top
                self._line_indicator.show()
                self._ensure_indicator_on_top()
            
            # Update scroll button position to account for line indicator
            self._update_scroll_button_position()
            
            # Handle inline progress mode initialization with specific scroll behavior
            if inline_update:
                # Get scrollbar for position management
                scrollbar = self.verticalScrollBar()
                old_value = scrollbar.value()
                
                # Add placeholder message
                timestamp = datetime.now().strftime(self._timestamp_format + " ")
                super().append(f"{timestamp}Preparing progress tracking...")
                
                if was_at_bottom:
                    # If we were at bottom, do one final scroll to make progress visible
                    self._do_auto_scroll()
                    # Then immediately disable auto-scrolling to prevent future jumps
                    self._auto_scroll_enabled = False
                else:
                    # If not at bottom, restore scroll position and disable auto-scroll
                    scrollbar.setValue(old_value)
                    self._auto_scroll_enabled = False
                    
                    # Show scroll button since we're not at bottom
                    if hasattr(self, '_scroll_button'):
                        self._scroll_button.show_animated()
                
                # Store the progress message ID for later updates
                self._progress_message_id = self.document().blockCount() - 1
                
                # We're explicitly managing scroll state
                self._preserve_scroll_state = True
            else:
                # Standard mode - maintain previous scroll behavior
                if was_at_bottom and self._auto_scroll_enabled:
                    self._do_auto_scroll()
                    
                    # Hide scroll button since we're at bottom
                    if hasattr(self, '_scroll_button'):
                        self._scroll_button.hide()
                else:
                    self._restore_scroll_position()
                    
                    # Show scroll button if not at bottom
                    if not self._is_at_bottom() and hasattr(self, '_scroll_button'):
                        self._scroll_button.show_animated()
            
            # Force update
            self._process_events_if_needed()
            
            # Ensure indicator is still visible after all operations
            if hasattr(self, '_line_indicator'):
                self._line_indicator.show()
                self._ensure_indicator_on_top()
                
            # Update scroll button position again
            self._update_scroll_button_position()
            
        except Exception as e:
            print(f"Error in set_loading_on: {traceback.format_exc()}", file=sys.stderr)
    
    def update_progress(self, current, total=None, message=None):
        """
        Update the progress indicator in inline progress mode
        
        Args:
            current (int): Current progress value
            total (int, optional): Total progress value. If None, uses last set total.
            message (str, optional): Optional message to display with the progress.
        
        Returns:
            bool: True if progress was updated, False if inline progress mode is not active
        """
        if not self._inline_progress_update or not self._loading:
            return False
            
        try:
            # Save current scroll position before doing anything
            scrollbar = self.verticalScrollBar()
            old_value = scrollbar.value()
            was_at_bottom = self._is_at_bottom()
            
            # Update progress values
            self._progress_current = max(0, min(current, self._progress_total))
            if total is not None:
                self._progress_total = max(1, total)  # Ensure total is at least 1
                
            # Calculate percentage
            percentage = int((self._progress_current / self._progress_total) * 100)
            
            # Format progress message
            if message:
                progress_text = f"{message} - {self._progress_current}/{self._progress_total} ({percentage}%)"
            else:
                progress_text = f"Progress: {self._progress_current}/{self._progress_total} ({percentage}%)"
            
            # Create timestamp
            timestamp = datetime.now().strftime(self._timestamp_format + " ")
            full_message = f"{timestamp}{progress_text}"
            
            # Find the block with our progress message
            doc = self.document()
            block = doc.findBlockByNumber(self._progress_message_id) if self._progress_message_id is not None else None
            
            if block is not None and block.isValid():
                # Create a cursor positioned at the START of the block
                cursor = QTextCursor(block)
                
                # Move cursor to start position and select the ENTIRE block
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                
                # Replace the entire text with our new message
                cursor.removeSelectedText()
                cursor.insertText(full_message)
            else:
                # If block not found, try to find the last block and update it
                last_block_id = doc.blockCount() - 1
                if last_block_id >= 0:
                    block = doc.findBlockByNumber(last_block_id)
                    if block.isValid():
                        cursor = QTextCursor(block)
                        cursor.movePosition(QTextCursor.StartOfBlock)
                        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                        cursor.removeSelectedText()
                        cursor.insertText(full_message)
                        self._progress_message_id = last_block_id
                    else:
                        # Fallback: append new message
                        super().append(full_message)
                        self._progress_message_id = doc.blockCount() - 1
                else:
                    # Fallback: append new message
                    super().append(full_message)
                    self._progress_message_id = doc.blockCount() - 1
            
            # Immediately restore scroll position to prevent jumping
            scrollbar.setValue(old_value)
            
            # Update scroll button visibility based on scroll position
            if not was_at_bottom and hasattr(self, '_scroll_button'):
                self._scroll_button.show_animated()
            elif was_at_bottom and hasattr(self, '_scroll_button'):
                # Hide immediately instead of animated to prevent lingering
                self._scroll_button.hide()
                
            # Update scroll button position
            self._update_scroll_button_position()
            
            # Process events to update the text display but maintain scroll
            self._process_events_if_needed()
            
            return True
            
        except Exception as e:
            print(f"Error in update_progress: {traceback.format_exc()}", file=sys.stderr)
            return False

    def _update_line_indicator_position(self):
        # Implementation of _update_line_indicator_position method
        pass

    def _update_scroll_button_position(self):
        # Implementation of _update_scroll_button_position method
        pass

    def _on_scroll(self, value):
        # Implementation of _on_scroll method
        pass

    def _on_user_scroll_start(self):
        # Implementation of _on_user_scroll_start method
        pass

    def _on_user_scroll_end(self):
        # Implementation of _on_user_scroll_end method
        pass

    def _on_scroll_button_clicked(self):
        # Implementation of _on_scroll_button_clicked method
        pass

    def _is_at_bottom(self):
        # Implementation of _is_at_bottom method
        pass

    def _do_auto_scroll(self):
        # Implementation of _do_auto_scroll method
        pass

    def _save_scroll_position(self):
        # Implementation of _save_scroll_position method
        pass

    def _restore_scroll_position(self):
        # Implementation of _restore_scroll_position method
        pass

    def _process_events_if_needed(self):
        # Implementation of _process_events_if_needed method
        pass

    def _ensure_indicator_on_top(self):
        # Implementation of _ensure_indicator_on_top method
        pass

    def set_loading_off(self, completion_message=None):
        """Deactivate the loading indicator"""
        try:
            if not self._loading:
                return
            
            # Determine current scroll state
            was_at_bottom = self._is_at_bottom()
            scrollbar = self.verticalScrollBar()
            old_value = scrollbar.value()
            
            # Check if we were in inline progress mode
            was_inline_mode = self._inline_progress_update
            
            # Save the auto-scroll state for restoration
            saved_auto_scroll = self._auto_scroll_enabled
            
            # Temporarily disable auto-scrolling for message additions
            self._auto_scroll_enabled = False
            
            # Reset inline progress tracking
            self._inline_progress_update = False
            self._progress_message_id = None
            
            # Update loading state
            self._loading = False
            
            # Stop the animation
            if hasattr(self, '_line_indicator'):
                self._line_indicator.stop_animation()
                self._line_indicator.hide()
            
            # Update scroll button position since line indicator is now hidden
            self._update_scroll_button_position()
            
            # Process any queued messages while maintaining scroll position
            if not self._message_queue.empty():
                messages = []
                while not self._message_queue.empty():
                    try:
                        messages.append(self._message_queue.get(block=False))
                    except queue.Empty:
                        break
                
                # Add all messages
                for message in messages:
                    super().append(message)
                    # Reset scroll position after each message
                    scrollbar.setValue(old_value)
                
                QApplication.processEvents()
            
            # Add completion message if provided
            if completion_message is not None:
                timestamp = datetime.now().strftime(self._timestamp_format + " ")
                super().append(f"{timestamp}{completion_message}")
                # Maintain scroll position
                scrollbar.setValue(old_value)
                QApplication.processEvents()
            
            # Restore the auto-scroll state AFTER all messages are added
            if was_inline_mode and hasattr(self, '_pre_inline_auto_scroll_state'):
                self._auto_scroll_enabled = self._pre_inline_auto_scroll_state
            else:
                self._auto_scroll_enabled = saved_auto_scroll
            
            # Handle final scrolling decision
            if self._auto_scroll_enabled and was_at_bottom:
                # Only auto-scroll if we were at bottom and auto-scroll is now enabled
                QTimer.singleShot(10, self._do_auto_scroll)
                
                # Hide scroll button since we'll be at bottom - use immediate hide
                if hasattr(self, '_scroll_button'):
                    self._scroll_button.hide()
            else:
                # Otherwise keep current position
                scrollbar.setValue(old_value)
                
                # Show scroll button if not at bottom
                if not self._is_at_bottom() and hasattr(self, '_scroll_button'):
                    self._scroll_button.show_animated()
            
            # Reset scroll preservation flag
            self._preserve_scroll_state = False
            
            # Process events after all messages are added
            self._process_events_if_needed()
            
            # Update scroll button position one final time
            self._update_scroll_button_position()
            
        except Exception as e:
            print(f"Error in set_loading_off: {traceback.format_exc()}", file=sys.stderr)
            # Ensure auto-scroll is restored even on error
            if hasattr(self, '_pre_inline_auto_scroll_state'):
                self._auto_scroll_enabled = self._pre_inline_auto_scroll_state
    
    def _ensure_loading_indicator_hidden(self):
        """Make sure all loading indicators are hidden"""
        if hasattr(self, '_line_indicator'):
            self._line_indicator.hide()
    
    def clear(self):
        """Clear the console content"""
        try:
            # Call the parent class's clear method
            super().clear()
            
            # Reset any internal state that might be affected by clearing
            self._first_content = True
            self._progress_message_id = None
            
            # Clear only the pending batch, not the queued messages
            self._pending_batch.clear()
            
            # Hide the scroll button since we're now at the bottom
            if hasattr(self, '_scroll_button'):
                self._scroll_button.hide()
                
            # Reset auto-scroll to enabled
            self._auto_scroll_enabled = True
            self._was_at_bottom = True
            
            # Note: We're intentionally NOT clearing the message queue here
            # so that any queued messages during loading will still be processed
                
        except Exception as e:
            print(f"Error in clear: {traceback.format_exc()}", file=sys.stderr)

    def _is_at_bottom(self):
        """Check if view is scrolled to bottom"""
        scrollbar = self.verticalScrollBar()
        return scrollbar.value() >= scrollbar.maximum() - 5
    
    def _on_user_scroll_start(self):
        """Handle when user begins manual scrolling"""
        self._user_has_scrolled = True
        self._last_known_position = self.verticalScrollBar().value()
    
    def _on_user_scroll_end(self):
        """Handle when user finishes manual scrolling"""
        # Check if we're at bottom after user scrolling
        at_bottom = self._is_at_bottom()
        
        # Enable auto-scroll if user scrolled to bottom
        if (at_bottom and not self._auto_scroll_enabled):
            self._auto_scroll_enabled = True
            self.scroll_state_changed.emit(True)
        # Disable auto-scroll if user scrolled away from bottom
        elif (not at_bottom and self._auto_scroll_enabled):
            self._auto_scroll_enabled = False
            self.scroll_state_changed.emit(False)
        
        self._user_has_scrolled = False
        self._was_at_bottom = at_bottom
    
    def _on_scroll(self, value):
        """Track scroll position changes"""
        # Only detect user scrolling, not programmatic scrolling
        if self._user_has_scrolled:
            was_at_bottom = self._was_at_bottom
            now_at_bottom = self._is_at_bottom()
            
            # If user scrolled away from bottom
            if (was_at_bottom and not now_at_bottom):
                self._auto_scroll_enabled = False
                self.scroll_state_changed.emit(False)
                
                # Show the scroll button
                if hasattr(self, '_scroll_button'):
                    self._scroll_button.show_animated()
            
            # If user scrolled back to bottom
            elif (not was_at_bottom and now_at_bottom):
                self._auto_scroll_enabled = True
                self.scroll_state_changed.emit(True)
                
                # Hide the scroll button immediately
                if hasattr(self, '_scroll_button'):
                    self._scroll_button.hide()
            
            # Update state
            self._was_at_bottom = now_at_bottom
        else:
            # Check if we need to show/hide the scroll button based on position
            now_at_bottom = self._is_at_bottom()
            
            if not now_at_bottom and hasattr(self, '_scroll_button'):
                self._scroll_button.show_animated()
            elif now_at_bottom and hasattr(self, '_scroll_button'):
                # Hide immediately instead of animated to prevent lingering
                self._scroll_button.hide()
    
    def _do_auto_scroll(self):
        """Perform auto-scrolling if enabled"""
        if not self._auto_scroll_enabled:
            return False
        
        # Reset text cursor to end
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        
        # Set scrollbar to maximum
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Force immediate update
        self.repaint()
        
        # Hide the scroll button since we're at bottom
        if hasattr(self, '_scroll_button'):
            # Force hide immediately rather than animated to prevent lingering
            self._scroll_button.hide()
        
        # Process events after scrolling
        self._process_events_if_needed()
        
        return True
    
    def _safe_auto_scroll(self):
        """Perform auto-scrolling only if it was previously enabled, respecting user scroll state"""
        if self._auto_scroll_enabled and not self._preserve_scroll_state:
            return self._do_auto_scroll()
        return False
    
    def _save_scroll_position(self):
        """Save current scroll position for later restoration"""
        scrollbar = self.verticalScrollBar()
        self._saved_scroll_position = scrollbar.value()
        if scrollbar.maximum() > 0:
            self._saved_scroll_percentage = scrollbar.value() / scrollbar.maximum()
        else:
            self._saved_scroll_percentage = 0
    
    def _restore_scroll_position(self):
        """Restore previously saved scroll position"""
        scrollbar = self.verticalScrollBar()
        scrollbar.blockSignals(True)
        
        if 0 <= self._saved_scroll_position <= scrollbar.maximum():
            scrollbar.setValue(self._saved_scroll_position)
        elif self._saved_scroll_percentage is not None:
            new_pos = int(self._saved_scroll_percentage * scrollbar.maximum())
            scrollbar.setValue(new_pos)
        
        scrollbar.blockSignals(False)
    
    def _update_scroll_button_position(self):
        """Update the position of the scroll-to-bottom button"""
        if hasattr(self, '_scroll_button') and self._scroll_button:
            # Position at bottom right with increased margin to avoid scrollbar
            margin_right = 20  # Increased from 10 to 20
            margin_bottom = 10
            x = self.width() - self._scroll_button.width() - margin_right
            y = self.height() - self._scroll_button.height() - margin_bottom
            
            # Adjust position if line indicator is visible
            if hasattr(self, '_line_indicator') and self._line_indicator and self._line_indicator.isVisible():
                y -= self._line_indicator.height()
                
            self._scroll_button.move(x, y)
            
            # Ensure button is on top
            self._ensure_scroll_button_on_top()
            
    def _ensure_scroll_button_on_top(self):
        """Ensure the scroll button is on top of the widget stack"""
        if hasattr(self, '_scroll_button') and self._scroll_button:
            # Raise the button to the top of the widget stack
            self._scroll_button.raise_()
            
            # Force a repaint of the button
            self._scroll_button.update()
            
    def _on_scroll_button_clicked(self):
        """Handle scroll button click - scroll to bottom"""
        # Enable auto-scroll
        self._auto_scroll_enabled = True
        
        # Perform scroll
        self._do_auto_scroll()
        
        # Hide the button immediately (not animated)
        if hasattr(self, '_scroll_button'):
            self._scroll_button.hide()
        
        # Emit signal that we're at bottom
        self.scroll_state_changed.emit(True)
        
        # Update state
        self._was_at_bottom = True
        
    def resizeEvent(self, event):
        """Handle resize to update indicator position"""
        super().resizeEvent(event)
        
        # Update line indicator position
        self._update_line_indicator_position()
        
        # Update scroll button position
        self._update_scroll_button_position()
        
        # Ensure indicator is visible if in loading state
        if self._loading and hasattr(self, '_line_indicator'):
            self._line_indicator.show()
            self._ensure_indicator_on_top()
            
        # Process events to ensure UI updates
        self._process_events_if_needed()
    
    def _update_line_indicator_position(self):
        """Update the position of the line indicator"""
        # Position at the bottom, full width
        if hasattr(self, '_line_indicator') and self._line_indicator:
            self._line_indicator.setFixedWidth(self.width())
            self._line_indicator.move(0, self.height() - self._line_indicator.height())
            
            # Ensure indicator is on top
            self._ensure_indicator_on_top()
    
    def focusInEvent(self, event):
        """Handle focus in event - ensure indicator remains hidden if not loading"""
        super().focusInEvent(event)
        
        # Handle loading indicator
        if hasattr(self, '_line_indicator') and not self._loading:
            self._line_indicator.hide()
            
        # Update scroll button visibility based on scroll position
        if hasattr(self, '_scroll_button'):
            if not self._is_at_bottom():
                self._scroll_button.show_animated()
            else:
                self._scroll_button.hide()
    
    def focusOutEvent(self, event):
        """Handle focus out event - ensure indicator remains hidden if not loading"""
        super().focusOutEvent(event)
        
        # Handle loading indicator
        if hasattr(self, '_line_indicator') and not self._loading:
            self._line_indicator.hide()
            
        # We don't hide the scroll button on focus out, as it should remain visible
        # if the user has scrolled away from the bottom
    
    def _process_events_if_needed(self):
        """Process events if auto_process_events is enabled and enough time has passed"""
        if not self._auto_process_events:
            return False
        
        current_time = time.time()
        
        # Increment counter
        self._event_processing_count += 1
        
        # Check if we should process events
        should_process = False
        
        # Process after certain number of operations
        if self._event_processing_count >= self._event_processing_threshold:
            should_process = True
        
        # Or after minimum elapsed time (100ms)
        elif self._last_event_process_time and current_time - self._last_event_process_time >= 0.1:
            should_process = True
            
        # Process events if needed
        if should_process:
            QApplication.processEvents()
            self._event_processing_count = 0
            self._last_event_process_time = current_time
            return True
        
        # Update last process time if it's the first call
        if not self._last_event_process_time:
            self._last_event_process_time = current_time
        
        return False
    
    def _ensure_indicator_on_top(self):
        """Ensure the loading indicator is on top of the widget stack"""
        if hasattr(self, '_line_indicator') and self._line_indicator:
            # Raise the indicator to the top of the widget stack
            self._line_indicator.raise_()
            
            # Force a repaint of the indicator
            self._line_indicator.update()
            
    @property
    def handles_event_processing(self):
        """
        Returns whether this logger automatically processes events.
        
        If True, client code generally doesn't need to call QApplication.processEvents()
        during operations with this logger.
        
        Returns:
            bool: True if the logger handles event processing automatically
        """
        return self._auto_process_events
    
    def set_event_processing(self, enabled, threshold=5):
        """
        Configure automatic event processing.
        
        Args:
            enabled (bool): Whether to automatically process events
            threshold (int): Number of operations before processing events
        """
        self._auto_process_events = enabled
        self._event_processing_threshold = max(1, threshold)
        self._event_processing_count = 0
        self._last_event_process_time = None
        
    def customize_scroll_button(self, size=None, background_color=None, hover_color=None, 
                               pressed_color=None, text=None, font=None, animation_duration=None,
                               shadow_enabled=True, shadow_color=None, shadow_blur=None, shadow_offset=None):
        """
        Customize the appearance of the scroll-to-bottom button
        
        Args:
            size (int, optional): Size of the button in pixels (button is square). Defaults to None.
            background_color (str, optional): Background color in CSS format. Defaults to None.
            hover_color (str, optional): Hover color in CSS format. Defaults to None.
            pressed_color (str, optional): Pressed color in CSS format. Defaults to None.
            text (str, optional): Button text. Defaults to None.
            font (QFont, optional): Button font. Defaults to None.
            animation_duration (int, optional): Duration of show/hide animations in ms. Defaults to None.
            shadow_enabled (bool, optional): Whether to show shadow. Defaults to True.
            shadow_color (QColor, optional): Shadow color. Defaults to None.
            shadow_blur (int, optional): Shadow blur radius. Defaults to None.
            shadow_offset (tuple, optional): Shadow offset (x, y). Defaults to None.
        """
        if hasattr(self, '_scroll_button') and self._scroll_button:
            self._scroll_button.customize_appearance(
                size=size,
                background_color=background_color,
                hover_color=hover_color,
                pressed_color=pressed_color,
                text=text,
                font=font,
                animation_duration=animation_duration,
                shadow_enabled=shadow_enabled,
                shadow_color=shadow_color,
                shadow_blur=shadow_blur,
                shadow_offset=shadow_offset
            )
            
            # Update position after customization
            self._update_scroll_button_position() 