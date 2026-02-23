@echo off
echo ============================================================
echo   Conversion des 5 pages HTML corrigees
echo ============================================================

if not exist pages_pdf mkdir pages_pdf

echo.
echo Conversion p242...
wkhtmltopdf --enable-local-file-access --page-width 160mm --page-height 220mm --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 --dpi 300 --no-outline --disable-smart-shrinking --encoding utf-8 242__shneur_zalman_de_liadi_gauche__101_gauche.html pages_pdf\p242.pdf

echo Conversion p254...
wkhtmltopdf --enable-local-file-access --page-width 160mm --page-height 220mm --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 --dpi 300 --no-outline --disable-smart-shrinking --encoding utf-8 254__hafets_haim_gauche__106_gauche.html pages_pdf\p254.pdf

echo Conversion p262...
wkhtmltopdf --enable-local-file-access --page-width 160mm --page-height 220mm --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 --dpi 300 --no-outline --disable-smart-shrinking --encoding utf-8 262__rav_a_y_kook_gauche__109_gauche.html pages_pdf\p262.pdf

echo Conversion p274...
wkhtmltopdf --enable-local-file-access --page-width 160mm --page-height 220mm --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 --dpi 300 --no-outline --disable-smart-shrinking --encoding utf-8 274__nehama_leibowitz_gauche__115_gauche.html pages_pdf\p274.pdf

echo Conversion p278...
wkhtmltopdf --enable-local-file-access --page-width 160mm --page-height 220mm --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 --dpi 300 --no-outline --disable-smart-shrinking --encoding utf-8 278__rav_steinsaltz_gauche__117_gauche.html pages_pdf\p278.pdf

echo.
echo ============================================================
echo   5 PDF generes dans pages_pdf\
echo   Puis : conversion CMJN + remplacement dans pages_cmjn
echo ============================================================
pause
