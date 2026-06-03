from odoo import api, fields, models


class LspStudent(models.Model):
    _inherit = 'lsp.student'
    _rec_name = 'full_name'

    # Override payment_state agar bisa di-search (untuk domain di Many2many)
    payment_state = fields.Selection(
        search='_search_payment_state',
    )

    @api.model
    def _search_payment_state(self, operator, value):
        """Custom search agar payment_state (non-stored computed) bisa digunakan di domain."""
        if operator == '=' and value == 'paid':
            # Cari sale.order yang semua invoice-nya sudah paid
            paid_orders = self.env['sale.order'].sudo().search([
                ('invoice_ids', '!=', False),
            ])
            paid_order_ids = [
                o.id for o in paid_orders
                if o.payment_settlement_state == 'paid'
            ]
            return [('sale_order_id', 'in', paid_order_ids)]
        elif operator == '!=' and value == 'paid':
            paid_orders = self.env['sale.order'].sudo().search([
                ('invoice_ids', '!=', False),
            ])
            paid_order_ids = [
                o.id for o in paid_orders
                if o.payment_settlement_state == 'paid'
            ]
            return [
                '|',
                ('sale_order_id', '=', False),
                ('sale_order_id', 'not in', paid_order_ids),
            ]
        # Fallback generik
        all_students = self.sudo().search([])
        matching_ids = []
        for student in all_students:
            match = False
            if operator == '=' and student.payment_state == value:
                match = True
            elif operator == '!=' and student.payment_state != value:
                match = True
            elif operator == 'in' and student.payment_state in value:
                match = True
            elif operator == 'not in' and student.payment_state not in value:
                match = True
            if match:
                matching_ids.append(student.id)
        return [('id', 'in', matching_ids)]

    def name_get(self):
        result = []
        for student in self:
            name = student.full_name or student.email or ''
            if student.nik:
                name = '%s (%s)' % (name, student.nik)
            result.append((student.id, name))
        return result
