# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, SavepointCase, new_test_user


class TestMaintenanceSignOca(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.company = cls.env.company
        cls.template = cls.env.ref(
            "maintenance_sign_oca.sign_oca_template_maintenance_equipment_demo"
        )
        cls.model_maintenance_equipment = cls.env.ref(
            "maintenance.model_maintenance_equipment"
        )
        cls.user_a = new_test_user(cls.env, login="test-user-a")
        cls.equipment_a = cls.env["maintenance.equipment"].create(
            {"name": "Test equipment A", "owner_user_id": cls.user_a.id}
        )
        cls.user_b = new_test_user(cls.env, login="test-user-b")
        cls.equipment_b = cls.env["maintenance.equipment"].create(
            {"name": "Test equipment B", "owner_user_id": cls.user_b.id}
        )

    def test_template_generate_multi_maintenance_equipment(self):
        equipments = self.equipment_a + self.equipment_b
        wizard_form = Form(
            self.env["sign.oca.template.generate.multi"].with_context(
                default_model="maintenance.equipment", active_ids=equipments.ids
            )
        )
        wizard_form.template_id = self.template
        action = wizard_form.save().generate()
        requests = self.env[action["res_model"]].search(action["domain"])
        self.assertEqual(len(requests), 2)
        request_a = requests.filtered(
            lambda x: x.maintenance_equipment_id == self.equipment_a
        )
        request_b = requests.filtered(
            lambda x: x.maintenance_equipment_id == self.equipment_b
        )
        self.assertIn(self.user_a.partner_id, request_a.mapped("signer_ids.partner_id"))
        self.assertIn(self.user_b.partner_id, request_b.mapped("signer_ids.partner_id"))

    def test_maintenance_equipment_create(self):
        self.company.maintenance_equipment_sign_oca_template_id = self.template
        equipment_c = self.env["maintenance.equipment"].create(
            {"name": "Test equipment C", "owner_user_id": self.user_a.id}
        )
        self.assertIn(
            self.user_a.partner_id,
            equipment_c.sign_request_ids.mapped("signer_ids.partner_id"),
        )

    def test_maintenance_equipment_write(self):
        self.company.maintenance_equipment_sign_oca_template_id = self.template
        self.equipment_a.write({"owner_user_id": False})
        self.assertFalse(self.equipment_a.sign_request_ids)
        self.equipment_b.write({"owner_user_id": False})
        self.assertFalse(self.equipment_b.sign_request_ids)
        self.equipment_a.write({"owner_user_id": self.user_a.id})
        self.assertIn(
            self.user_a.partner_id,
            self.equipment_a.sign_request_ids.mapped("signer_ids.partner_id"),
        )
        self.equipment_b.write({"owner_user_id": self.user_b.id})
        self.assertIn(
            self.user_b.partner_id,
            self.equipment_b.sign_request_ids.mapped("signer_ids.partner_id"),
        )
