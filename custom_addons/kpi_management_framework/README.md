# KPI Management Framework Module

## Overview
The KPI Management Framework module provides a comprehensive system for tracking and managing Key Performance Indicators (KPIs) for users in the CRM system. It allows administrators to:
- Assign KPIs to users
- Track progress against targets
- Automatically calculate achievements
- Generate reports on performance

## Technical Architecture

### Models
- `kpi.target`: Main KPI target assignment model
- `kpi.target.line`: Individual KPI lines/targets
- `kpi.history`: Activity history tracking

### Key Features
- Automatic calculation of KPI achievements
- Integration with CRM leads
- Data quality tracking
- Performance summary dashboards

### Dependencies
- Odoo CRM module
- Odoo HR module (for user assignments)
- Odoo Mail module (for notifications)

## Installation
1. Install the module through Odoo Apps
2. Configure KPI definitions in Settings
3. Assign KPIs to users via the KPI Targets menu

## Configuration
```python
# Sample configuration for KPI definitions
'kpi_type': fields.Selection([
    ('leads_registered', 'Leads Registered'),
    ('data_quality', 'Data Quality')
], string='KPI Type')
```

## Automated Processes
- Nightly cron job updates all active targets
- Real-time updates when leads are registered
- Data quality checks triggered by telemarketing confirmations

## API Reference
```python
def _recalculate_values(self):
    """Recalculate all KPI values for the target document"""
    # Implementation details...
```

## Troubleshooting
Check logs for:
- `_logger.error` entries
- Missing dependencies
- Permission issues
