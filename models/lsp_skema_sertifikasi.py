# -*- coding: utf-8 -*-
from odoo import models, fields

class LspSkemaSertifikasi(models.Model):
    _name = 'lsp.skema.sertifikasi'
    _description = 'Skema Sertifikasi LSP'

    name = fields.Char(string='Nama Skema', required=True)
    code = fields.Char(string='Kode Jurusan/Skema', required=True, help='Contoh: rpl, bdp, tbsm')
    survey_id = fields.Many2one('survey.survey', string='Survei Ujian Sertifikasi')
