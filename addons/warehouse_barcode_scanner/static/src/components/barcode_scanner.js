/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class WarehouseBarcodeScanner extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            picking: null,
            scannedLines: [],
        });

        this.barcodeInput = useRef("barcodeInput");

        onWillStart(async () => {
            await this.loadPickingData();
        });
    }

    async loadPickingData() {
        const pickingData = await this.orm.read(
            "stock.picking",
            [this.props.action.context.active_id],
            ["name", "move_line_ids"]
        );
        this.state.picking = pickingData[0];
    }

    async onBarcodeScanned(ev) {
        const barcode = ev.target.value;
        if (!barcode) return;

        ev.target.value = ""; // Clear the input

        const result = await this.rpc("/warehouse_barcode_scanner/scan_barcode", {
            barcode: barcode,
            picking_id: this.state.picking.id,
        });

        if (result.error) {
            this.notification.add(result.error, { type: "danger" });
        } else if (result.success) {
            this.notification.add(result.message, { type: "success" });
            // Update the UI with the new data
            const existingLine = this.state.scannedLines.find(line => line.product_id === result.product_id);
            if (existingLine) {
                existingLine.qty_done = result.qty_done;
            } else {
                this.state.scannedLines.push(result);
            }
        }
    }
}

WarehouseBarcodeScanner.template = "warehouse_barcode_scanner.BarcodeScannerTemplate";

registry.category("actions").add("warehouse_barcode_scanner.ui", WarehouseBarcodeScanner);