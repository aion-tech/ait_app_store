# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, _


class StockLotHistory(models.TransientModel):
    _name = "stock.lot.inventory.wizard"
    _description = "Wizard for generating stock lot inventory"

    location_ids = fields.Many2many(comodel_name="stock.location", string="Location")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    # EUR-114
    def action_generate_report(self):
        """
        Generates a summarized inventory report by product and lot within the selected location and date range.

        This method:
        - Clears previous transient report records.
        - Retrieves all stock move lines matching the given location and date filters.
        - Groups data by product and lot, summing incoming and outgoing quantities.
        - Creates transient records in 'stock.inventory.detail'.
        - Returns a list view action showing the generated report.
        """
        self.ensure_one()
        MoveLine = self.env["stock.move.line"]
        DetailModel = self.env["stock.inventory.detail"]

        # Optional: clear previously generated report data
        DetailModel.search([]).unlink()

        date_start = self._set_date_start()
        date_end = self._set_date_end()

        # Fetch move lines based on date range and selected location (as source or destination)
        move_lines = MoveLine.search(
            [
                ("date", ">=", date_start),
                ("date", "<=", date_end),
                "|",
                ("location_id", "in", self.location_ids.ids),
                ("location_dest_id", "in", self.location_ids.ids),
            ]
        )

        # Summary structure: {(product_tmpl_id, lot_id): {"incoming": float, "outgoing": float}}
        summary = {}

        for line in move_lines:
            if not line.lot_id:
                continue

            product_tmpl_id = line.product_id.product_tmpl_id.id

            # Entrata nella location selezionata
            if line.location_dest_id.id in self.location_ids.ids:
                key = (product_tmpl_id, line.lot_id.id, line.location_dest_id.id)
                if key not in summary:
                    summary[key] = {"incoming": 0.0, "outgoing": 0.0}
                summary[key]["incoming"] += line.qty_done

            # Uscita dalla location selezionata
            if line.location_id.id in self.location_ids.ids:
                key = (product_tmpl_id, line.lot_id.id, line.location_id.id)
                if key not in summary:
                    summary[key] = {"incoming": 0.0, "outgoing": 0.0}
                summary[key]["outgoing"] += line.qty_done

        # Crea le righe del report
        for (product_tmpl_id, lot_id, location_id), data in summary.items():
            self.env["stock.inventory.detail"].create(
                {
                    "name": f"{self.env['stock.location'].browse(location_id).display_name} - {product_tmpl_id}",
                    "location_id": location_id,
                    "product_id": product_tmpl_id,
                    "lot_id": lot_id,
                    "incoming_qty": data["incoming"],
                    "outgoing_qty": data["outgoing"],
                    "net_qty": data["incoming"] - data["outgoing"],
                }
            )

        # Return an action to open the report in list view (popup)
        return {
            "name": _("{} Inventory Detail from {} to {}").format(
                self.location_ids.mapped("display_name"),
                date_start.strftime("%d/%m/%Y") if date_start else "N/A",
                date_end.strftime("%d/%m/%Y") if date_end else "N/A",
            ),
            "type": "ir.actions.act_window",
            "res_model": "stock.inventory.detail",
            "view_mode": "list",
            "target": "current",
        }

    # EUR-114
    def _set_date_start(self):
        date_start = self.date_start
        if date_start:
            return date_start
        oldest_move_line = self.env["stock.move.line"].search(
            [
                "|",
                ("location_id", "in", self.location_ids.ids),
                ("location_dest_id", "in", self.location_ids.ids),
            ],
            order="date asc",
            limit=1,
        )
        if oldest_move_line:
            return oldest_move_line.date

    # EUR-114
    def _set_date_end(self):
        date_end = self.date_end
        if date_end:
            return date_end
        return datetime.today()