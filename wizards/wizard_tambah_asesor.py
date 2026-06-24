import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LspWizardTambahAsesor(models.TransientModel):
    _name = 'lsp.wizard.tambah.asesor'
    _description = 'Wizard Tambah Asesor ke Penugasan'

    penugasan_id = fields.Many2one(
        comodel_name='lsp.penugasan.asesor',
        string='Penugasan',
        required=True,
        default=lambda self: self.env.context.get('active_id'),
        ondelete='cascade',
    )
    skema_id = fields.Many2one(
        comodel_name='lsp.skema.sertifikasi',
        related='penugasan_id.jadwal_id.skema_id',
        string='Skema Sertifikasi',
    )
    asesor_ids = fields.Many2many(
        comodel_name='res.users',
        string='Asesor',
    )
    unavailable_asesor_ids = fields.Many2many(
        comodel_name='res.users',
        relation='wizard_unavailable_asesor_rel',
        string='Unavailable Asesors',
        compute='_compute_unavailable_asesors',
    )

    @api.depends('penugasan_id')
    def _compute_unavailable_asesors(self):
        for wizard in self:
            if not wizard.penugasan_id or not wizard.penugasan_id.jadwal_id:
                wizard.unavailable_asesor_ids = [(5, 0, 0)]
                continue

            jadwal = wizard.penugasan_id.jadwal_id
            domain = [
                ('id', '!=', jadwal.id),
                ('tanggal_mulai', '<=', jadwal.tanggal_selesai),
                ('tanggal_selesai', '>=', jadwal.tanggal_mulai),
                ('waktu_mulai', '<', jadwal.waktu_selesai),
                ('waktu_selesai', '>', jadwal.waktu_mulai),
                ('state', '!=', 'batal'),
            ]
            intersecting_jadwals = self.env['lsp.jadwal.ujian'].search(domain)
            busy_asesor_ids = intersecting_jadwals.mapped('penugasan_ids.penugasan_line_ids.asesor_id.id')
            wizard.unavailable_asesor_ids = [(6, 0, busy_asesor_ids)]
    preview_info = fields.Text(
        string='Informasi Preview',
        compute='_compute_preview_info',
    )

    @api.depends('penugasan_id', 'asesor_ids')
    def _compute_preview_info(self):
        for wizard in self:
            if wizard.penugasan_id:
                total_asesi = wizard.penugasan_id.total_asesi
                current_asesor = wizard.penugasan_id.total_asesor
                dibutuhkan = math.ceil(total_asesi / 10) if total_asesi > 0 else 0
                akan_ditambah = len(wizard.asesor_ids)
                wizard.preview_info = _(
                    'Saat ini: %d asesor, butuh minimal %d asesor untuk %d asesi.\n'
                    'Akan ditambahkan: %d asesor.\n'
                    'Total setelah ditambahkan: %d asesor.'
                ) % (current_asesor, dibutuhkan, total_asesi, akan_ditambah, current_asesor + akan_ditambah)
            else:
                wizard.preview_info = ''

    def action_tambah_asesor(self):
        """Menambahkan asesor yang dipilih ke penugasan."""
        self.ensure_one()

        if not self.asesor_ids:
            raise UserError(_('Silakan pilih minimal satu asesor untuk ditambahkan.'))

        existing_asesor_ids = self.penugasan_id.penugasan_line_ids.mapped('asesor_id').ids

        for asesor in self.asesor_ids:
            if asesor.id in existing_asesor_ids:
                raise UserError(
                    _('Asesor %s sudah ditambahkan di penugasan ini!') % asesor.name
                )
            self.env['lsp.penugasan.line'].create({
                'penugasan_id': self.penugasan_id.id,
                'asesor_id': asesor.id,
            })

        return {'type': 'ir.actions.act_window_close'}
