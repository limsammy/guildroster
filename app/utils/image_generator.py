from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import io
import zipfile
from app.schemas.attendance import (
    TeamViewData,
    TeamViewToon,
    TeamViewRaid,
    ToonAttendanceRecord,
)
from app.models.team import Team
from app.models.guild import Guild


class AttendanceImageGenerator:
    """Generate attendance report images for teams."""

    # Frontend-matching color scheme (dark theme)
    COLORS = {
        "background": (15, 23, 42),  # slate-900 - dark background
        "header_bg": (30, 41, 59),  # slate-800 - dark header
        "card_bg": (30, 41, 59),  # slate-800 - dark cards
        "card_bg_alt": (51, 65, 85),  # slate-700 - alternate row
        "border": (71, 85, 105),  # slate-600 - borders
        "text_primary": (248, 250, 252),  # slate-50 - light text
        "text_secondary": (203, 213, 225),  # slate-300 - medium text
        "text_muted": (148, 163, 184),  # slate-400 - muted text
        "accent": (245, 158, 11),  # amber-500 - accent color
        "success": (34, 197, 94),  # green-500 - success
        "warning": (234, 179, 8),  # yellow-500 - warning
        "error": (239, 68, 68),  # red-500 - error
        "header_text": (255, 255, 255),  # white header text
    }

    def __init__(
        self, width: int = 1200, height: int = 1600
    ):  # Webpage-like dimensions
        self.width = width
        self.height = height
        self.font_size_small = 16
        self.font_size_normal = 18
        self.font_size_large = 20
        self.font_size_xlarge = 24
        self.font_size_title = 32

    def _get_font(
        self, size: int, bold: bool = False
    ) -> ImageFont.FreeTypeFont:
        """Get font with specified size and weight."""
        try:
            if bold:
                return ImageFont.truetype("arialbd.ttf", size)
            else:
                return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.Draw,
        bbox: Tuple[int, int, int, int],
        fill: Tuple[int, int, int],
        radius: int = 4,
    ):
        """Draw a rounded rectangle."""
        x1, y1, x2, y2 = bbox

        # Draw main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

        # Draw corners
        draw.pieslice(
            [x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill
        )
        draw.pieslice(
            [x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill
        )
        draw.pieslice(
            [x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill
        )
        draw.pieslice(
            [x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill
        )

    def _draw_attendance_cell(
        self,
        draw: ImageDraw.Draw,
        x: int,
        y: int,
        size: int,
        status: str,
        note_id: Optional[int] = None,
    ):
        """Draw an attendance status cell with improved readability."""
        # Background color based on status
        if status == "present":
            bg_color = self.COLORS["success"]
            text_color = (255, 255, 255)
            symbol = "✓"  # Proper checkmark
        elif status == "absent":
            bg_color = self.COLORS["error"]
            text_color = (255, 255, 255)
            symbol = "✗"  # Proper X
        elif status == "benched":
            bg_color = self.COLORS["warning"]
            text_color = (0, 0, 0)  # Black text on yellow for better contrast
            symbol = "B"
        else:
            bg_color = self.COLORS["text_muted"]
            text_color = (255, 255, 255)
            symbol = "?"

        # Draw cell background
        self._draw_rounded_rectangle(draw, (x, y, x + size, y + size), bg_color)

        # Draw symbol with larger font for better readability
        font = self._get_font(self.font_size_large, bold=True)
        bbox = draw.textbbox((0, 0), symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (size - text_width) // 2
        text_y = y + (size - text_height) // 2
        draw.text((text_x, text_y), symbol, fill=text_color, font=font)

        # Draw note indicator as superscript (only if there's a note)
        if note_id is not None:
            note_font = self._get_font(12, bold=True)
            note_text = f"[{note_id}]"
            # Position as superscript (top right, smaller and higher)
            draw.text(
                (x + size - 8, y - 8),
                note_text,
                fill=(255, 255, 255),  # White for visibility
                font=note_font,
            )

    def _format_date(self, date_str: str) -> str:
        """Format date string for display in a readable format."""
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date.strftime("%m/%d")  # MM/DD format for compact display
        except:
            return date_str

    def _get_period_text(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> str:
        """Get period text for the report."""
        if start_date and end_date:
            return f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        elif start_date:
            return f"Starting: {start_date.strftime('%B %d, %Y')}"
        else:
            return f"Generated: {datetime.now().strftime('%B %d, %Y')}"

    def generate_team_report(
        self,
        team_data: TeamViewData,
        guild: Guild,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bytes:
        """Generate attendance report image for a team."""
        # Create image with dark background
        img = Image.new(
            "RGB", (self.width, self.height), self.COLORS["background"]
        )
        draw = ImageDraw.Draw(img)

        # Collect all notes for footnotes
        notes_collection = []
        note_counter = 1

        # Header
        header_height = 120
        header_bg = self.COLORS["header_bg"]
        draw.rectangle([0, 0, self.width, header_height], fill=header_bg)

        # Title
        title_font = self._get_font(self.font_size_title, bold=True)
        title = f"{guild.name} Attendance Report"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text(
            (title_x, 25),
            title,
            fill=self.COLORS["header_text"],
            font=title_font,
        )

        # Team name
        team_font = self._get_font(self.font_size_large)
        team_name = f"Team: {team_data.team['name']}"
        team_bbox = draw.textbbox((0, 0), team_name, font=team_font)
        team_width = team_bbox[2] - team_bbox[0]
        team_x = (self.width - team_width) // 2
        draw.text(
            (team_x, 65), team_name, fill=self.COLORS["accent"], font=team_font
        )

        # Period
        period_font = self._get_font(self.font_size_normal)
        period_text = self._get_period_text(start_date, end_date)
        period_bbox = draw.textbbox((0, 0), period_text, font=period_font)
        period_width = period_bbox[2] - period_bbox[0]
        period_x = (self.width - period_width) // 2
        draw.text(
            (period_x, 95),
            period_text,
            fill=self.COLORS["text_muted"],
            font=period_font,
        )

        # Table area
        table_start_y = header_height + 40
        table_width = self.width - 80
        table_height = (
            self.height - table_start_y - 180
        )  # Leave space for legend and footnotes

        # Calculate column widths - more compact layout
        toon_col_width = 140
        class_col_width = 100
        role_col_width = 100
        attendance_col_width = 100
        raid_col_width = 80

        # Table header
        header_y = table_start_y
        header_font = self._get_font(self.font_size_normal, bold=True)

        # Draw header background
        draw.rectangle(
            [40, header_y, self.width - 40, header_y + 50],
            fill=self.COLORS["card_bg"],
        )
        draw.rectangle(
            [40, header_y, self.width - 40, header_y + 50],
            outline=self.COLORS["border"],
            width=1,
        )

        # Header text
        x_offset = 40
        headers = ["Toon", "Class", "Role", "Att %"]
        widths = [
            toon_col_width,
            class_col_width,
            role_col_width,
            attendance_col_width,
        ]

        for header, width in zip(headers, widths):
            draw.text(
                (x_offset + 15, header_y + 15),
                header,
                fill=self.COLORS["text_primary"],
                font=header_font,
            )
            x_offset += width

        # Raid headers with better formatting to prevent overlap
        for raid in team_data.raids:
            raid_text = f"{self._format_date(raid.scheduled_at)}"
            raid_bbox = draw.textbbox((0, 0), raid_text, font=header_font)
            raid_width = raid_bbox[2] - raid_bbox[0]
            raid_x = x_offset + (raid_col_width - raid_width) // 2
            draw.text(
                (raid_x, header_y + 15),
                raid_text,
                fill=self.COLORS["text_primary"],
                font=header_font,
            )
            x_offset += raid_col_width

        # Table rows
        row_height = 45
        current_y = header_y + 50

        for i, toon in enumerate(team_data.toons):
            if current_y + row_height > table_start_y + table_height:
                break  # Don't overflow

            # Row background
            row_bg = (
                self.COLORS["card_bg"]
                if i % 2 == 0
                else self.COLORS["card_bg_alt"]
            )  # Alternate rows
            draw.rectangle(
                [40, current_y, self.width - 40, current_y + row_height],
                fill=row_bg,
            )
            draw.rectangle(
                [40, current_y, self.width - 40, current_y + row_height],
                outline=self.COLORS["border"],
                width=1,
            )

            # Toon info
            x_offset = 40
            info_font = self._get_font(self.font_size_normal)

            # Toon name
            draw.text(
                (x_offset + 15, current_y + 12),
                toon.username,
                fill=self.COLORS["text_primary"],
                font=info_font,
            )
            x_offset += toon_col_width

            # Class
            draw.text(
                (x_offset + 15, current_y + 12),
                toon.class_name,
                fill=self.COLORS["text_secondary"],
                font=info_font,
            )
            x_offset += class_col_width

            # Role
            draw.text(
                (x_offset + 15, current_y + 12),
                toon.role,
                fill=self.COLORS["text_secondary"],
                font=info_font,
            )
            x_offset += role_col_width

            # Attendance percentage
            attendance_text = f"{toon.overall_attendance_percentage:.1f}%"
            attendance_bbox = draw.textbbox(
                (0, 0), attendance_text, font=info_font
            )
            attendance_width = attendance_bbox[2] - attendance_bbox[0]
            attendance_x = (
                x_offset + (attendance_col_width - attendance_width) // 2
            )

            # Color code attendance percentage
            if toon.overall_attendance_percentage >= 80:
                color = self.COLORS["success"]
            elif toon.overall_attendance_percentage >= 60:
                color = self.COLORS["warning"]
            else:
                color = self.COLORS["error"]

            draw.text(
                (attendance_x, current_y + 12),
                attendance_text,
                fill=color,
                font=info_font,
            )
            x_offset += attendance_col_width

            # Attendance cells
            for raid in team_data.raids:
                record = next(
                    (
                        r
                        for r in toon.attendance_records
                        if r.raid_id == raid.id
                    ),
                    None,
                )
                if record:
                    # Check if this record has notes
                    note_id = None
                    if record.has_note:
                        # Create note text
                        note_parts = []
                        if record.notes:
                            note_parts.append(record.notes)
                        if record.benched_note:
                            note_parts.append(record.benched_note)

                        if note_parts:
                            note_text = " | ".join(note_parts)
                            notes_collection.append(
                                f"[{note_counter}] {toon.username} - {note_text}"
                            )
                            note_id = note_counter
                            note_counter += 1

                    self._draw_attendance_cell(
                        draw,
                        x_offset + 20,
                        current_y + 8,
                        30,
                        record.status,
                        note_id,
                    )
                x_offset += raid_col_width

            current_y += row_height

        # Legend
        legend_y = self.height - 180
        legend_font = self._get_font(self.font_size_small)

        # Legend background
        draw.rectangle(
            [40, legend_y, self.width - 40, legend_y + 60],
            fill=self.COLORS["card_bg"],
        )
        draw.rectangle(
            [40, legend_y, self.width - 40, legend_y + 60],
            outline=self.COLORS["border"],
            width=1,
        )

        # Legend title
        draw.text(
            (50, legend_y + 15),
            "Legend:",
            fill=self.COLORS["text_primary"],
            font=legend_font,
        )

        # Legend items
        legend_items = [
            ("✓", "Present", "success"),
            ("✗", "Absent", "error"),
            ("B", "Benched", "warning"),
        ]

        x_offset = 50
        for symbol, text, color in legend_items:
            # Draw symbol
            draw.text(
                (x_offset, legend_y + 40),
                symbol,
                fill=self.COLORS[color],
                font=legend_font,
            )
            x_offset += 25

            # Draw text
            draw.text(
                (x_offset, legend_y + 40),
                text,
                fill=self.COLORS["text_secondary"],
                font=legend_font,
            )
            x_offset += 100

        # Footnotes section
        if notes_collection:
            footnotes_y = legend_y + 80
            footnotes_font = self._get_font(self.font_size_small)

            # Footnotes background
            draw.rectangle(
                [40, footnotes_y, self.width - 40, self.height - 40],
                fill=self.COLORS["card_bg"],
            )
            draw.rectangle(
                [40, footnotes_y, self.width - 40, self.height - 40],
                outline=self.COLORS["border"],
                width=1,
            )

            # Footnotes title
            draw.text(
                (50, footnotes_y + 15),
                "Notes:",
                fill=self.COLORS["text_primary"],
                font=footnotes_font,
            )

            # Display footnotes
            current_note_y = footnotes_y + 45
            for note in notes_collection:
                if current_note_y + 25 > self.height - 50:
                    break  # Don't overflow

                draw.text(
                    (50, current_note_y),
                    note,
                    fill=self.COLORS["text_secondary"],
                    font=footnotes_font,
                )
                current_note_y += 25

        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG", optimize=True)
        return img_bytes.getvalue()

    def generate_multiple_reports(
        self,
        reports_data: List[
            Tuple[TeamViewData, Guild, Optional[datetime], Optional[datetime]]
        ],
    ) -> bytes:
        """Generate multiple team reports and return as ZIP file."""
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for team_data, guild, start_date, end_date in reports_data:
                # Generate image
                image_bytes = self.generate_team_report(
                    team_data, guild, start_date, end_date
                )

                # Create filename
                team_name = (
                    team_data.team["name"].replace(" ", "_").replace("/", "_")
                )
                guild_name = guild.name.replace(" ", "_").replace("/", "_")
                date_str = datetime.now().strftime("%Y%m%d")
                filename = f"{guild_name}_{team_name}_attendance_{date_str}.png"

                # Add to zip
                zip_file.writestr(filename, image_bytes)

        return zip_buffer.getvalue()


def get_current_period() -> Tuple[datetime, datetime]:
    """Get the current period (from previous Tuesday to now)."""
    now = datetime.now()

    # Find the most recent Tuesday
    days_since_tuesday = (now.weekday() - 1) % 7  # Tuesday is 1
    if (
        days_since_tuesday == 0 and now.hour < 12
    ):  # If it's Tuesday morning, use last Tuesday
        days_since_tuesday = 7

    start_date = now - timedelta(days=days_since_tuesday)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    return start_date, end_date
