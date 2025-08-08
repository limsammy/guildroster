# Feature Flags

This document describes the feature flags available in GuildRoster and how to configure them.

## Overview

Feature flags allow administrators to enable or disable specific functionality without requiring code changes. This is useful for:
- Gradually rolling out new features
- Disabling features that may cause issues
- Controlling access to resource-intensive operations

## Available Feature Flags

### ENABLE_ATTENDANCE_EXPORT

**Description**: Controls whether users can export attendance reports as PNG images.

**Default**: `true` (enabled)

**Environment Variable**: `ENABLE_ATTENDANCE_EXPORT`

**Values**:
- `true`, `1`, `yes`, `on` - Enable attendance export
- `false`, `0`, `no`, `off` - Disable attendance export

**Usage**: When disabled, the export buttons will be hidden from the attendance view and API calls will return a 403 error.

## Configuration

### Environment Variable

Add to your `.env` file:

```bash
# Enable attendance export (default)
ENABLE_ATTENDANCE_EXPORT=true

# Disable attendance export
ENABLE_ATTENDANCE_EXPORT=false
```

### Docker Environment

When running with Docker, you can set the environment variable:

```bash
docker run -e ENABLE_ATTENDANCE_EXPORT=false guildroster-backend
```

### Production Deployment

For production deployments, set the environment variable in your deployment configuration:

```yaml
# Docker Compose example
services:
  backend:
    environment:
      - ENABLE_ATTENDANCE_EXPORT=true
```

## Frontend Integration

The frontend automatically checks the export status and conditionally shows/hides export buttons:

1. **API Check**: The frontend calls `/attendance/export/status` to check if export is enabled
2. **UI Updates**: Export buttons are only shown when the feature is enabled
3. **Error Handling**: If the status check fails, export is disabled by default

## Adding New Feature Flags

To add a new feature flag:

1. **Backend**: Add the flag to `app/config.py`
2. **API**: Create an endpoint to check the flag status
3. **Frontend**: Add the flag check to the relevant components
4. **Documentation**: Update this file with the new flag details

### Example

```python
# app/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    ENABLE_NEW_FEATURE: bool = True
```

```python
# app/routers/some_router.py
@router.get("/feature/status")
def get_feature_status():
    return {"new_feature_enabled": settings.ENABLE_NEW_FEATURE}
```

## Security Considerations

- Feature flags are checked on the backend for security
- Frontend checks are for UX only and should not be relied upon for security
- Always validate feature access in API endpoints
- Consider rate limiting for feature flag status endpoints

## Monitoring

Monitor feature flag usage to understand:
- Which features are most/least used
- Performance impact of enabled features
- User adoption of new features

Consider adding logging when features are accessed to track usage patterns.
