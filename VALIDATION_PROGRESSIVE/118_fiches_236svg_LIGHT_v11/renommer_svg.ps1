## ============================================================
## SCRIPT DE RENOMMAGE DES FICHIERS SVG
## Lumières d'Israël — La Torah Vivante
## ============================================================
## 
## Ce script renomme les fichiers SVG (001_gauche.svg, 001_droite.svg, etc.)
## pour qu'ils portent le même nom de base que les images PNG correspondantes.
##
## USAGE (PowerShell) :
##   cd "chemin/vers/le/dossier/parent"
##   .\renommer_svg.ps1
##
## STRUCTURE ATTENDUE :
##   dossier_parent/
##   ├── 118_fiches_236svg_LIGHT_v11/    (les SVG)
##   │   ├── 001_gauche.svg
##   │   ├── 001_droite.svg
##   │   └── ...
##   ├── images_retenues/                 (les PNG)
##   │   ├── 001_adam_harishon.png
##   │   └── ...
##   └── svg_renamed/                     (sortie — créé automatiquement)
## ============================================================

$svgDir = "."
$outDir = "svg_renamed"

# Créer le dossier de sortie
if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# ============================================================
# MAPPING COMPLET : SVG numéro → nom de base image
# ============================================================
# Format : SVG_NUM = "NNN_nom_image" (identique au fichier PNG sans .png)
#
# Les SVG et les images n'ont PAS la même numérotation pour certains personnages.
# Ce mapping a été vérifié personnage par personnage.
# ============================================================

$mapping = @{
    # ── Ch.1-6 : Les Patriarches et Prophètes (or #8B6914) ──
    "001" = "001_adam_harishon"
    "002" = "002_noah"
    "003" = "003_avraham_avinou"
    "004" = "004_sarah_imenou"
    "005" = "005_yitshak_avinou"
    "006" = "006_rivka_imenou"
    "007" = "007_yaakov_avinou"
    "008" = "008_rahel_et_lea"
    "009" = "009_yossef_hatsadik"
    "010" = "010_yehouda"
    "011" = "011_moshe_rabbenou"
    "012" = "012_aharon_hacohen"
    "013" = "013_myriam_hanevia"
    "014" = "014_pinhas"
    "015" = "015_yehoshoua"
    "016" = "016_calev"
    "017" = "017_deborah"
    "018" = "018_shimshon"
    "019" = "019_ruth"
    "020" = "020_shmouel_hanavi"
    "021" = "021_hanna"
    "022" = "022_david_hamelekh"
    "023" = "023_shlomo_hamelekh"
    "024" = "024_eliyahou_hanavi"
    "025" = "025_elisha"
    "026" = "026_yeshayahou"
    # ⚠️ DÉCALAGE PROPHÈTES (027-030) — les numéros SVG et images ne correspondent pas
    "027" = "029_yirmeyahou"          # SVG 027 = Yirméyahou → image 029
    "028" = "028_amos"                # SVG 028 = Amos → image 028 (OK)
    "029" = "030_yona"                # SVG 029 = Yona → image 030
    "030" = "027_osee"                # SVG 030 = Osée (ex-doublon) → image 027
    "031" = "031_yehezkel"
    "032" = "032_daniel"
    "033" = "033_ezra_hasofer"
    "034" = "034_nehemia"
    "035" = "035_esther_hamalka"

    # ── Ch.7-9 : Torah Orale (bleu #2D4A6E) ──
    "036" = "036_shimon_hatsadik"
    "037" = "037_antigone_de_sokho"
    "038" = "038_hillel_hazaken"
    "039" = "039_shammai_hazaken"
    "040" = "040_rabban_gamliel"
    "041" = "041_yohanan_ben_zakkai"
    "042" = "042_hanina_ben_dossa"
    "043" = "043_eliezer_ben_hyrcanos"
    "044" = "044_yehoshoua_ben_hanania"
    "045" = "045_rabbi_akiva"
    "046" = "046_rabbi_tarfon"
    "047" = "047_rabbi_ishmael"
    "048" = "048_bar_kokhba"
    "049" = "049_rabbi_meir"
    "050" = "050_brouria"
    "051" = "051_shimon_bar_yohai"
    "052" = "052_yehouda_bar_ilai"
    "053" = "053_yehouda_hanassi"
    "054" = "054_rav_abba_arikha"
    "055" = "055_mar_shmouel"
    "056" = "056_rabbi_yohanan"
    "057" = "057_reish_lakish"
    "058" = "058_yehoshoua_ben_levi"
    "059" = "059_eleazar_ben_pedat"
    "060" = "060_rabbi_abbahou"
    "061" = "061_abbaye"
    "062" = "062_rava"
    "063" = "063_ravina_rav_ashi"
    "064" = "064_rav_saadia_gaon"
    "065" = "065_rav_sherira_gaon"
    "066" = "066_rav_hai_gaon"

    # ── Ch.10-14 : Les Rishonim ──
    # ⚠️ DÉCALAGE MAJEUR (067-081) — réorganisation par chapitres dans les SVG
    # Les images gardent la numérotation originale du livre
    "067" = "070_bahya_ibn_paquda"        # SVG 067 = Ibn Paquda → image 070
    "068" = "071_shlomo_ibn_gabirol"      # SVG 068 = Ibn Gabirol → image 071
    "069" = "072_yehouda_halevi"          # SVG 069 = Halevi → image 072
    "070" = "073_avraham_ibn_ezra"        # SVG 070 = Ibn Ezra → image 073
    "071" = "067_rabbenou_guershom"       # SVG 071 = Guershom → image 067
    "072" = "081_rif"                     # SVG 072 = Rif → image 081
    "073" = "068_rachi"                   # SVG 073 = Rachi → image 068
    "074" = "069_rabbenou_tam"            # SVG 074 = Rabbénou Tam → image 069
    "075" = "075_maimonide"               # SVG 075 = Maïmonide → image 075 (OK)
    "076" = "074_radak"                   # SVG 076 = Radak → image 074
    "077" = "077_rokeah"                  # SVG 077 = Rokeah → image 077 (OK)
    "078" = "076_ramban"                  # SVG 078 = Ramban → image 076
    "079" = "078_yona_de_gerone"          # SVG 079 = Yona de Gérone → image 078
    "080" = "079_rashba"                  # SVG 080 = Rashba → image 079
    "081" = "080_ralbag"                  # SVG 081 = Ralbag → image 080
    "082" = "082_meiri"
    "083" = "083_rosh"
    "084" = "084_le_tour"
    "085" = "085_yossef_karo"
    "086" = "086_rama"
    "087" = "087_abravanel"
    "088" = "088_sforno"
    "089" = "089_maharal_de_prague"
    "090" = "090_kli_yakar"

    # ── Ch.15-16 : Kabbale et Hassidisme ──
    "091" = "091_ramak"
    "092" = "092_ari_zal"
    "093" = "093_haim_vital"
    "094" = "094_or_hahaim_hakadosh"
    "095" = "095_ramhal"
    "096" = "096_baal_shem_tov"
    "097" = "097_maguid_mezeritch"
    "098" = "098_elimelekh_lizhensk"
    "099" = "099_levi_yitshak_berditchev"
    "100" = "100_nahman_breslev"
    "101" = "101_shneur_zalman"
    "102" = "102_rabbi_loubavitch"

    # ── Ch.17 : Monde Lituanien ──
    "103" = "103_gaon_vilna"
    "104" = "104_haim_volozhin"
    "105" = "105_israel_salanter"
    "106" = "106_hafets_haim"

    # ── Ch.18 : Bâtisseurs et Contemporains ──
    # ⚠️ DÉCALAGE (107-111) — ordre différent entre SVG et images
    "107" = "108_hatam_sofer"             # SVG 107 = Hatam Sofer → image 108
    "108" = "109_samson_raphael_hirsch"   # SVG 108 = Hirsch → image 109
    "109" = "111_rav_kook"                # SVG 109 = Rav Kook → image 111
    "110" = "107_hazon_ish"               # SVG 110 = Hazon Ish → image 107
    "111" = "110_sarah_schenirer"         # SVG 111 = Sarah Schenirer → image 110
    "112" = "112_rav_tsvi_kook"
    "113" = "113_moshe_feinstein"
    "114" = "114_rav_soloveitchik"
    "115" = "115_nechama_leibowitz"
    "116" = "116_rav_ovadia_yossef"
    "117" = "117_rav_steinsaltz"
    "118" = "118_jonathan_sacks"
}

# ============================================================
# EXÉCUTION DU RENOMMAGE
# ============================================================

$total = 0
$errors = 0

foreach ($entry in $mapping.GetEnumerator() | Sort-Object Key) {
    $svgNum = $entry.Key
    $imgBase = $entry.Value

    foreach ($side in @("gauche", "droite")) {
        $src = Join-Path $svgDir "${svgNum}_${side}.svg"
        $dst = Join-Path $outDir "${imgBase}_${side}.svg"

        if (Test-Path $src) {
            Copy-Item $src $dst
            $total++
        } else {
            Write-Host "⚠️  MANQUANT: $src" -ForegroundColor Yellow
            $errors++
        }
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host "RENOMMAGE TERMINÉ"
Write-Host "============================================================"
Write-Host "Fichiers copiés : $total"
if ($errors -gt 0) {
    Write-Host "Erreurs : $errors" -ForegroundColor Red
} else {
    Write-Host "Aucune erreur !" -ForegroundColor Green
}
Write-Host "Dossier de sortie : $outDir"
Write-Host ""
Write-Host "Vérification rapide :"
Write-Host "  Fichiers dans sortie : $((Get-ChildItem $outDir -Filter *.svg).Count)"
Write-Host "  Attendu : 236 (118 x 2)"
