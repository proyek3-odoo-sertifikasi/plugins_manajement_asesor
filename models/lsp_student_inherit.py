from odoo import models


class LspStudent(models.Model):
    _inherit = 'lsp.student'

    def name_get(self):
        result = []
        for student in self:
            name = student.full_name or student.email or ''
            if student.nik:
                name = '%s (%s)' % (name, student.nik)
            result.append((student.id, name))
        return result
