# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LspSkemaSertifikasi(models.Model):
    _name = 'lsp.skema.sertifikasi'
    _description = 'Skema Sertifikasi LSP'

    name = fields.Char(string='Nama Skema', required=True)
    code = fields.Char(string='Kode Jurusan/Skema', required=True, help='Contoh: rpl, bdp, tbsm')
    survey_id = fields.Many2one('survey.survey', string='Survei Ujian Sertifikasi')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_survey_skema()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'survey_id' in vals:
            self._sync_survey_skema()
        return result

    def _sync_survey_skema(self):
        """Sinkronisasi skema_sertifikasi_ids di survey.survey agar record rules bisa berjalan."""
        for skema in self:
            if skema.survey_id:
                skema.survey_id.sudo().write({
                    'skema_sertifikasi_ids': [(4, skema.id)],
                })


class SurveySurveyInheritLsp(models.Model):
    """Tambah relasi Many2many antara survey.survey dengan lsp.skema.sertifikasi
    agar record rules dapat memfilter survey berdasarkan skema asesor."""
    _inherit = 'survey.survey'

    skema_sertifikasi_ids = fields.Many2many(
        'lsp.skema.sertifikasi',
        'survey_skema_rel',
        'survey_id',
        'skema_id',
        string='Skema Sertifikasi',
        help='Skema sertifikasi yang menggunakan survey ini sebagai instrumen ujian.',
    )

