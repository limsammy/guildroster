# Attendance Export Feature

## Overview

The Attendance Export feature allows users to generate attendance report images for sharing in Discord or other platforms. The feature creates clean, branded PNG images that display team attendance data in a table format similar to the frontend view.

## Features

### 1. Single Team Export
- Export attendance for a specific team as a PNG image
- Configurable time periods (current week, all time, custom range)
- Consistent 1600x900 dimensions for easy sharing
- Branded with guild name and team name

### 2. Multiple Teams Export
- Export all teams as a ZIP file containing individual PNG images
- Option to export all teams or teams from a specific guild
- Same time period options as single team export

### 3. Time Period Options
- **Current Week**: From previous Tuesday to now (default)
- **All Time**: All available raids for the team
- **Custom Range**: User-defined start and end dates

## API Endpoints

### Single Team Export
```
GET /attendance/export/team/{team_id}/image
```

**Parameters:**
- `period` (string): "current", "all", or "custom"
- `start_date` (datetime): Required for custom period
- `end_date` (datetime): Required for custom period
- `raid_count` (int): Maximum raids to include (1-50, default 20)

**Response:** PNG image file

### Multiple Teams Export
```
GET /attendance/export/all-teams/image
```

**Parameters:**
- `guild_id` (int, optional): Filter teams by guild
- `period` (string): "current", "all", or "custom"
- `start_date` (datetime): Required for custom period
- `end_date` (datetime): Required for custom period
- `raid_count` (int): Maximum raids to include per team (1-50, default 20)

**Response:** ZIP file containing PNG images

## Frontend Integration

### Export Controls
The export functionality is integrated into the Attendance Team View page with:

1. **Export Period Selector**: Choose between current week, all time, or custom range
2. **Custom Date Range**: Date pickers for custom period selection
3. **Export Buttons**:
   - "Export Team Report": Generate PNG for selected team
   - "Export All Teams (ZIP)": Generate ZIP with all team reports

### Usage Flow
1. Navigate to Attendance page
2. Select a team (or guild for all teams export)
3. Choose export period
4. Click export button
5. File downloads automatically

## Image Format

### Dimensions
- **Size**: 1600x900 pixels
- **Format**: PNG
- **Color Scheme**: Matches frontend theme (slate-900, amber-400, etc.)

### Content
- **Header**: Guild name and team name
- **Period**: Date range covered
- **Table**: Toons as rows, raids as columns
- **Attendance Status**: Color-coded cells (✓ present, ✗ absent, B benched)
- **Notes**: * indicator for cells with notes
- **Legend**: Explanation of symbols and colors

### Styling
- Consistent with frontend color scheme
- Clean, professional appearance
- Easy to read in Discord or other platforms
- Responsive layout that fits well in chat applications

## Technical Implementation

### Backend
- **Image Generation**: Uses Pillow (PIL) library
- **Color Scheme**: Matches frontend Tailwind CSS colors
- **Font Handling**: Falls back to system fonts if custom fonts unavailable
- **ZIP Generation**: Built-in Python zipfile module

### Frontend
- **API Integration**: New methods in AttendanceService
- **Blob Handling**: Downloads files as blobs
- **Error Handling**: User-friendly error messages
- **Loading States**: Visual feedback during export

## File Naming

### Single Team Export
```
{Guild_Name}_{Team_Name}_attendance_{YYYYMMDD}.png
```

### Multiple Teams Export
```
{Guild_Name}_all_teams_attendance_{YYYYMMDD}.zip
```

## Notes and Limitations

### Notes Display
- Notes are shown with * indicator
- Benched notes are displayed without "Benched Note:" prefix
- "Notes: Not present in warcraftlogs report" is filtered out

### Performance
- Large exports may take time to generate
- ZIP files can be large with many teams
- Consider raid_count parameter for performance

### Browser Compatibility
- Requires modern browser with Blob support
- Automatic download may be blocked by popup blockers
- File size limits may apply in some browsers

## Future Enhancements

### Potential Improvements
1. **PDF Export**: Add PDF format option
2. **Custom Styling**: Allow guild-specific branding
3. **Scheduled Exports**: Automatic weekly reports
4. **Email Integration**: Send reports via email
5. **Discord Integration**: Direct upload to Discord channels
6. **Template System**: Customizable report layouts

### Configuration Options
1. **Image Quality**: Adjustable PNG quality/size
2. **Custom Dimensions**: Different image sizes
3. **Color Themes**: Multiple color schemes
4. **Font Options**: Custom font support
5. **Layout Options**: Different table layouts

## Troubleshooting

### Common Issues
1. **Export Fails**: Check network connection and API availability
2. **Large Files**: Reduce raid_count parameter
3. **No Data**: Ensure team has attendance records
4. **Download Blocked**: Check browser popup settings
5. **Image Quality**: Verify Pillow installation

### Debug Information
- Check browser console for JavaScript errors
- Verify API endpoint responses
- Monitor server logs for backend errors
- Test with smaller datasets first 