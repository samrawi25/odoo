// /crm_telemarketing/static/src/js/tele_map.js
odoo.define('crm_telemarketing.tele_map', function (require) {
    "use strict";

    var core = require('web.core');
    var rpc = require('web.rpc');
    var Widget = require('web.Widget');

    var qweb = core.qweb;

    var TeleMap = Widget.extend({
        template: 'crm_telemarketing.tele_map_template',
        init: function (parent, options) {
            this._super(parent);
            this.options = options || {};
        },
        start: function () {
            var self = this;
            // initialize map container
            // Wait until template is in DOM
            this._render_map();
            return this._super.apply(this, arguments);
        },
        _render_map: function () {
            var self = this;
            // Create the leaflet map
            try {
                // default center (Addis Ababa)
                var map = L.map(self.$el.find('.o_crm_tele_map')[0]).setView([9.03, 38.74], 7);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(map);

                // Load data (partners, leads, opportunities) via RPC search_read
                var promises = [];
                promises.push(
                    rpc.query({
                        model: 'res.partner',
                        method: 'search_read',
                        args: [[['latitude', '!=', false], ['longitude', '!=', false]]],
                        kwargs: {fields: ['id', 'name', 'latitude', 'longitude', 'tin_number'], limit: 1000}
                    })
                );
                promises.push(
                    rpc.query({
                        model: 'crm.lead',
                        method: 'search_read',
                        args: [[['phone_number', '!=', false], ['phone_number', '!=', '']]],
                        kwargs: {fields: ['id', 'name', 'company_name', 'phone_number', 'assigned_user_id', 'campaign_id', 'partner_id', 'create_date', 'latitude', 'longitude'], limit: 1000}
                    })
                );
                promises.push(
                    rpc.query({
                        model: 'crm.tele_opportunity',
                        method: 'search_read',
                        args: [[['partner_id', '!=', false]]],
                        kwargs: {fields: ['id', 'name', 'partner_id', 'expected_total_sales_value'], limit: 1000}
                    })
                );

                Promise.all(promises).then(function (results) {
                    var partners = results[0];
                    var leads = results[1];
                    var opps = results[2];

                    // Add partner markers (blue)
                    partners.forEach(function (p) {
                        if (p.latitude && p.longitude) {
                            var marker = L.marker([p.latitude, p.longitude]).addTo(map);
                            marker.bindPopup('<b>Partner:</b> ' + (p.name || '') + '<br/><b>TIN:</b> ' + (p.tin_number || ''));
                        }
                    });

                    // Add lead markers (green) - attempt to use lat/lon fields if present in lead
                    leads.forEach(function (l) {
                        if (l.latitude && l.longitude) {
                            var marker = L.marker([l.latitude, l.longitude], {title: l.name}).addTo(map);
                            var popup = '<b>Lead:</b> ' + (l.name || '') + '<br/><b>Company:</b> ' + (l.company_name || '') +
                                '<br/><b>Phone:</b> ' + (l.phone_number || '') + '<br/>';
                            marker.bindPopup(popup);
                        }
                    });

                    // Add opportunities as circle markers near their partner if available
                    opps.forEach(function (o) {
                        if (o.partner_id && o.partner_id[0]) {
                            var partner_id = o.partner_id[0];
                            // find partner coordinates
                            var partner = partners.find(function (pp) { return pp.id === partner_id; });
                            if (partner && partner.latitude && partner.longitude) {
                                var circle = L.circle([partner.latitude, partner.longitude], {
                                    radius: 200,
                                    color: 'red',
                                    fillOpacity: 0.2
                                }).addTo(map);
                                circle.bindPopup('<b>Opportunity:</b> ' + (o.name || '') + '<br/><b>Expected:</b> ' + (o.expected_total_sales_value || '0'));
                            }
                        }
                    });
                }).catch(function (err) {
                    console.error('Error loading CRM Telemarketing map data', err);
                });
            } catch (e) {
                console.error('Leaflet not loaded or map error', e);
                this.$el.find('.o_crm_tele_map').html('<div class="o_alert">Map could not be initialized. Please ensure Leaflet is available.</div>');
            }
        }
    });

    // Register client action entry point
    core.action_registry.add('crm_tele_map_action', function (parent, action) {
        var widget = new TeleMap(parent, {});
        widget.appendTo(parent.el);
        return widget;
    });

    return TeleMap;
});
