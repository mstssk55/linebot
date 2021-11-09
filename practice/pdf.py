import pdfkit, os
# pdfkit.from_file('test.html', 'out.pdf')
def pdf():
    return pdfkit.from_string(
        '<!DOCTYPE html>'
        '<html lang="ja">'
        '<head>'
        '<meta charset="utf-8"/>'
        '<title>もんてい</title>'
        '</head>'
        '<body>'
        '<p>'
        'ぱいそん'
        '</p>'
        '</body>'
        '</html>',
        'a.pdf')
pdf()