# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        if self.pool.ready:
            users._check_single_role()
        return users

    def write(self, vals):
        res = super().write(vals)
        # Odoo 19: field is 'group_ids' (not 'groups_id')
        if 'group_ids' in vals and self.pool.ready:
            self._check_single_role()
        return res

    def _check_single_role(self):
        group_admin = self.env.ref('plugins_manajement_asesor.group_admin_lsp', raise_if_not_found=False)
        group_asesor = self.env.ref('plugins_manajement_asesor.group_asesor', raise_if_not_found=False)
        group_keuangan = self.env.ref('plugins_custom_billing_module.group_lsp_keuangan', raise_if_not_found=False)
        group_portal = self.env.ref('base.group_portal', raise_if_not_found=False)

        conflicting_group_ids = {g.id for g in [group_admin, group_asesor, group_keuangan, group_portal] if g}

        for user in self:
            # Skip superuser to prevent boot install lockups
            if user.id == self.env.ref('base.user_root').id:
                continue

            # Odoo 19: field is 'group_ids' (not 'groups_id')
            assigned_conflict_groups = user.group_ids.filtered(lambda g: g.id in conflicting_group_ids)
            if len(assigned_conflict_groups) > 1:
                group_names = ", ".join(assigned_conflict_groups.mapped('name'))
                raise ValidationError(
                    _("User %s tidak boleh menjabat rangkap! Role aktif: %s. "
                      "Setiap user hanya boleh memiliki satu role aktif antara "
                      "Admin LSP, Asesor LSP, Keuangan LSP, atau Asesi (Portal).") % (user.name, group_names)
                )
