{
    "name": "Telemarketor Dashboard",
    "summary": "Telemarketing calls (inbound/outbound), encounters (GPS), opportunities, campaign and KPI scaffolding with map & XLSX export",
    "version": "17.0.2.0.0",
    "author": "Custom / AMG",
    "license": "AGPL-3",
    "category": "Marketing",
    "depends": [
        "crm",
        "sale_management",
        "hr",
        "web"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence_data.xml",
        "views/menu.xml",
        "views/res_partner_views.xml",
        "views/crm_lead_views.xml",
        "views/crm_opportunity_views.xml",
        "views/crm_encounter_views.xml",
        "views/crm_campaign_views.xml",
        "views/crm_kpi_views.xml",
        "views/wizard_export_views.xml",
        "views/crm_tele_map_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "telemarketor_dashboard/static/src/css/leaflet.css",
            "telemarketor_dashboard/static/src/js/leaflet.js",
            "telemarketor_dashboard/static/src/js/tele_map.js",
            "telemarketor_dashboard/static/src/xml/tele_map_templates.xml",
        ]
    },
    "installable": True,
    "application": True,
}
