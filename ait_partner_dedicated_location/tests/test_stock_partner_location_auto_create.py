from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install", "test_stock_partner_location_auto_create")
class TestHrExpenseSheet(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': "Paperino"
        })

        # Creazione di un magazzino
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Test Warehouse',
            'code': 'TEST',
        })

        # Configurazioni stock locations e route
        cls.customer_location = cls.env['stock.location'].create({'name': 'customer', 'usage': 'internal'})
        cls.vendor_location = cls.env['stock.location'].create({'name': 'vendor', 'usage': 'internal'})
        cls.subcontracting_location = cls.env['stock.location'].create({'name': 'subcontracting', 'usage': 'internal'})
        cls.rental_location = cls.env['stock.location'].create({'name': 'rental', 'usage': 'internal'})

        cls.config = cls.env['res.config.settings'].create({
            'customer_parent': cls.customer_location.id,
            'vendor_parent': cls.vendor_location.id,
            'subcontracting_parent': cls.subcontracting_location.id,
            'rental_parent': cls.rental_location.id,
        })
        cls.config.set_values()

    def test_create_locations_on_create(self):
        partner_with_locations = self.env['res.partner'].create({
            'name': "Pippo",
            'dedicated_customer_location': True,
            'dedicated_vendor_location': True,
            'dedicated_subcontracting_location': True,
            'dedicated_rental_location': True,
        })
        self.assertTrue(partner_with_locations.dedicated_customer_location_created)
        self.assertTrue(partner_with_locations.dedicated_vendor_location_created)
        self.assertTrue(partner_with_locations.dedicated_subcontracting_location_created)
        self.assertTrue(partner_with_locations.dedicated_rental_location_created)
        self.assertIsNotNone(partner_with_locations.property_stock_customer)
        self.assertIsNotNone(partner_with_locations.property_stock_supplier)
        self.assertIsNotNone(partner_with_locations.property_stock_subcontractor)
        self.assertIsNotNone(partner_with_locations.property_stock_rental)
        self.assertEqual(partner_with_locations.property_stock_customer.name, partner_with_locations.name)
        self.assertEqual(partner_with_locations.property_stock_supplier.name, partner_with_locations.name)
        self.assertEqual(partner_with_locations.property_stock_subcontractor.name, partner_with_locations.name)
        self.assertEqual(partner_with_locations.property_stock_rental.name, partner_with_locations.name)


    def test_create_locations_on_update(self):
        self.partner.write({
            'dedicated_customer_location': True,
            'dedicated_vendor_location': True,
            'dedicated_subcontracting_location': True,
            'dedicated_rental_location': True,
        })
        self.assertTrue(self.partner.dedicated_customer_location_created)
        self.assertTrue(self.partner.dedicated_vendor_location_created)
        self.assertTrue(self.partner.dedicated_subcontracting_location_created)
        self.assertTrue(self.partner.dedicated_rental_location_created)
        self.assertIsNotNone(self.partner.property_stock_customer)
        self.assertIsNotNone(self.partner.property_stock_supplier)
        self.assertIsNotNone(self.partner.property_stock_subcontractor)
        self.assertIsNotNone(self.partner.property_stock_rental)
        self.assertEqual(self.partner.property_stock_customer.name, self.partner.name)
        self.assertEqual(self.partner.property_stock_supplier.name, self.partner.name)
        self.assertEqual(self.partner.property_stock_subcontractor.name, self.partner.name)
        self.assertEqual(self.partner.property_stock_rental.name, self.partner.name)
