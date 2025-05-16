# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install", "eur")
class TestStockLotInventoryWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        This method is called once for the whole test class to set up the test data.
        It creates example locations, products, lots, stock move lines, and the wizard.
        """
        super(TestStockLotInventoryWizard, cls).setUpClass()

        # Create example locations
        cls.location_incoming = cls.env["stock.location"].create(
            {
                "name": "Test Location Incoming",
                "usage": "internal",
            }
        )

        cls.location_outgoing = cls.env["stock.location"].create(
            {
                "name": "Test Location Outgoing",
                "usage": "internal",
            }
        )

        # Create example product
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        # Create an example lot associated with the product
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "Test Lot",
                "product_id": cls.product.product_variant_id.id,
            }
        )

        # Create a stock move line for the product
        cls.move_line = cls.env["stock.move.line"].create(
            {
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
                "location_id": cls.location_incoming.id,
                "location_dest_id": cls.location_outgoing.id,
                "qty_done": 10,
                "date": fields.Date.today(),
                "company_id": cls.env.user.company_id.id,
            }
        )

        # Create the inventory wizard
        cls.wizard = cls.env["stock.lot.inventory.wizard"].create(
            {
                "location_id": cls.location_incoming.id,
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today(),
            }
        )

    def test_action_generate_report(self):
        """
        Test the 'action_generate_report' method of the stock lot inventory wizard.
        This method should create inventory detail records and return the correct action.

        Steps:
        1. Execute the 'action_generate_report' method.
        2. Check if the correct action is returned.
        3. Check if inventory detail records are created.
        4. Verify that the created details contain correct information.
        """
        # Execute the 'action_generate_report' method
        action = self.wizard.action_generate_report()

        # Verify that the action returned contains the correct model
        self.assertEqual(action["res_model"], "stock.inventory.detail")

        # Verify that the returned view is of type "tree"
        self.assertEqual(action["view_mode"], "tree")

        # Verify that records were created
        detail_records = self.env["stock.inventory.detail"].search([], limit=1)
        self.assertGreater(
            len(detail_records), 0, "No inventory detail records were created."
        )

        # Verify that the created details contain the correct information
        detail = detail_records
        self.assertEqual(detail.product_id, self.product)
        self.assertEqual(detail.lot_id, self.lot)
        self.assertEqual(detail.incoming_qty, 0.0)  # Verify incoming quantity
        self.assertEqual(detail.outgoing_qty, 10.0)  # Verify outgoing quantity
        self.assertEqual(detail.net_qty, -10.0)  # Verify net quantity
