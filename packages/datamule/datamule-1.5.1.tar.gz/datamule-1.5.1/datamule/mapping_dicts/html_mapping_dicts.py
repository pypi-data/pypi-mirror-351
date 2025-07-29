dict_10k_html = {
    ('part',r'^part\s*([ivx]+)$') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+)\.?([a-z])?') : 1,
}
dict_10q_html = dict_10k_html

dict_8k_html = {
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 0,
}

dict_sd_html = {
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 0,
}

dict_abs15g_html = {
    ('part',r'^part\s*([ivx]+)') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
    ('item',r'^item\s*(\d+\.\d+)') : 1,
}



dict_nt10k_html = {
    ('part',r'^part\s*([ivx]+)') : 0,
}
dict_nt10q_html = dict_nt10k_html
dict_nt20f_html = dict_nt10k_html
dict_ntncen_html = dict_nt10k_html
dict_ntncsr_html = dict_nt10k_html
dict_ntfcen_html = dict_nt10k_html
dict_ntfncsr_html = dict_nt10k_html

dict_1kpartii_html = {
    ('item',r'^item\s*(\d+)') : 0,
}

dict_1sa_html = dict_1kpartii_html

dict_1u_html = {('item',r'^item\s*(\d+)') : 0,
                ('signatures',r'^signatures?\.*$') : 0,}

dict_1012b_html = dict_1u_html

dict_10d_html = dict_10k_html

dict_20f_html = {
    ('part',r'^part\s*([ivx]+)') : 0,
    ('item',r'^item\s*(\d+)\.?([a-z])?') : 1,
    ('letter',r'\d*\.?([a-z])') : 2,
    ('signatures',r'^signatures?\.*$') : 0,
}

dict_8a12b_html = dict_1kpartii_html
dict_8a12g_html = dict_1kpartii_html

dict_8k12b_html = dict_8k_html

dict_8k12g3_html = dict_8k_html
dict_8k15d5_html = dict_8k_html

dict_absee_html = {('item',r'^item\s*(\d+)') : 0,
                ('signatures',r'^signatures?\.*$') : 0,}

dict_appntc_html = {('agency',r'^agency') : 0,
                    ('action',r'^action') : 0,
                    ('summary',r'^summary of application') : 0,
                    ('applicants',r'^applicants') : 0,
                    ('filing',r'^filing dates') : 0,
                    ('hearing',r'^hearing or notification of hearing') : 0,
                    ('addresses',r'^addresses') : 0,
                    ('further contact',r'^for further information contact') : 0,
                    ('supplementary information',r'^supplementary information') : 0,
}

dict_cb_html = {
    ('part', r'^part\s*([ivx]+)') : 0,
    ('item', r'^item\s*(\d+)') : 1,
}

dict_dstrbrpt_html = dict_1kpartii_html

dict_n18f1_html = {
    ('notification of election', r'^notification of election') : 0,
    ('signatures', r'^signatures?\.*$') : 0,
}

dict_ex99cert_html = {
    ('item',r'^(\d+)') : 0,
    ('letter',r'^\(?([a-z])') : 1,
}

dict_ncsrs_html = {
    ('item',r'^(\d+)') : 0,
    ('signatures',r'^signatures?\.*$') : 0,
}

dict_sc13e3_html = {
    ('item', r'^item\s*(\d+)') : 0,
    ('signatures', r'^signatures?\.*$') : 0,
    ('letter', r'^\(?([a-z])') : 1,
}

dict_sc14d9_html = {
    ('item', r'^item\s*(\d+)') : 0,
    ('signatures', r'^signatures?\.*$') : 0,
    ('annex', r'^annex') : 0,
}

dict_sp15d2_html = dict_10k_html

dict_t3_html = {('general',r'^general'):0,
                ('affiliations',r'^affiliations'):0,
                ('management and control',r'^management and control'):0,
                ('underwriters',r'^underwriters'):0,
                ('capital securities',r'^capital securities'):0,
                ('indenture securities',r'^indenture securities'):0,
                ('signatures',r'^signatures?\.*$') : 0,
                ('number',r'^(\d+)') : 1,}