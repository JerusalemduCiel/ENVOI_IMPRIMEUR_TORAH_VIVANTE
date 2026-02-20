# ============================================================
# REMAPPING DES IMAGES → NUMÉROS DE FICHES
# Lumières d'Israël — La Torah Vivante
# ============================================================
# USAGE : 
#   cd "dossier_parent"
#   .\remapper_images.ps1
#
# Structure attendue :
#   dossier_parent/
#   ├── portraits/          (images originales 001-118)
#   └── portraits_mapped/   (copies renommées, créé automatiquement)
# ============================================================

$srcDir = "portraits"
$outDir = "portraits_mapped"

if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# Mapping : image_filename → fiche_number
# 001-066 : identiques
# 067+ : réordonnés selon l'ordre des fiches SVG

$mapping = @{
    # 1-66 identiques
    "001_adam_harishon"          = "001"
    "002_noah"                  = "002"
    "003_avraham_avinou"        = "003"
    "004_sarah_imenou"          = "004"
    "005_yitshak_avinou"        = "005"
    "006_rivka_imenou"          = "006"
    "007_yaakov_avinou"         = "007"
    "008_rahel_et_lea"          = "008"
    "009_yossef_hatsadik"       = "009"
    "010_yehouda"               = "010"
    "011_moshe_rabbenou"        = "011"
    "012_aharon_hacohen"        = "012"
    "013_myriam_hanevia"        = "013"
    "014_pinhas"                = "014"
    "015_yehoshoua"             = "015"
    "016_calev"                 = "016"
    "017_deborah"               = "017"
    "018_shimshon"              = "018"
    "019_ruth"                  = "019"
    "020_shmouel_hanavi"        = "020"
    "021_hanna"                 = "021"
    "022_david_hamelekh"        = "022"
    "023_shlomo_hamelekh"       = "023"
    "024_eliyahou_hanavi"       = "024"
    "025_elisha"                = "025"
    "026_yeshayahou"            = "026"
    "027_osee"                  = "027"
    "028_amos"                  = "028"
    "029_yirmeyahou"            = "029"
    "030_yona"                  = "030"
    "031_yehezkel"              = "031"
    "032_daniel"                = "032"
    "033_ezra_hasofer"          = "033"
    "034_nehemia"               = "034"
    "035_esther_hamalka"        = "035"
    "036_shimon_hatsadik"       = "036"
    "037_antigone_de_sokho"     = "037"
    "038_hillel_hazaken"        = "038"
    "039_shammai_hazaken"       = "039"
    "040_rabban_gamliel"        = "040"
    "041_yohanan_ben_zakkai"    = "041"
    "042_hanina_ben_dossa"      = "042"
    "043_eliezer_ben_hyrcanos"  = "043"
    "044_yehoshoua_ben_hanania" = "044"
    "045_rabbi_akiva"           = "045"
    "046_rabbi_tarfon"          = "046"
    "047_rabbi_ishmael"         = "047"
    "048_bar_kokhba"            = "048"
    "049_rabbi_meir"            = "049"
    "050_brouria"               = "050"
    "051_shimon_bar_yohai"      = "051"
    "052_yehouda_bar_ilai"      = "052"
    "053_yehouda_hanassi"       = "053"
    "054_rav_abba_arikha"       = "054"
    "055_mar_shmouel"           = "055"
    "056_rabbi_yohanan"         = "056"
    "057_reish_lakish"          = "057"
    "058_yehoshoua_ben_levi"    = "058"
    "059_eleazar_ben_pedat"     = "059"
    "060_rabbi_abbahou"         = "060"
    "061_abbaye"                = "061"
    "062_rava"                  = "062"
    "063_ravina_rav_ashi"       = "063"
    "064_rav_saadia_gaon"       = "064"
    "065_rav_sherira_gaon"      = "065"
    "066_rav_hai_gaon"          = "066"
    # 67+ : REMAPPING
    "067_rabbenou_guershom"         = "071"
    "068_rachi"                     = "073"
    "069_rabbenou_tam"              = "074"
    "070_bahya_ibn_paquda"          = "067"
    "071_shlomo_ibn_gabirol"        = "068"
    "072_yehouda_halevi"            = "069"
    "073_avraham_ibn_ezra"          = "070"
    "074_radak"                     = "076"
    "075_maimonide"                 = "075"
    "076_ramban"                    = "078"
    "077_rokeah"                    = "077"
    "078_yona_de_gerone"            = "079"
    "079_rashba"                    = "080"
    "080_ralbag"                    = "081"
    "081_rif"                       = "072"
    "082_meiri"                     = "082"
    "083_rosh"                      = "083"
    "084_le_tour"                   = "084"
    "085_yossef_karo"               = "085"
    "086_rama"                      = "086"
    "087_abravanel"                 = "087"
    "088_sforno"                    = "088"
    "089_maharal_de_prague"         = "089"
    "090_kli_yakar"                 = "090"
    "091_ramak"                     = "091"
    "092_ari_zal"                   = "092"
    "093_haim_vital"                = "093"
    "094_or_hahaim_hakadosh"        = "094"
    "095_ramhal"                    = "095"
    "096_baal_shem_tov"             = "096"
    "097_maguid_mezeritch"          = "097"
    "098_elimelekh_lizhensk"        = "098"
    "099_levi_yitshak_berditchev"   = "099"
    "100_nahman_breslev"            = "100"
    "101_shneur_zalman"             = "101"
    "102_rabbi_loubavitch"          = "102"
    "103_gaon_vilna"                = "103"
    "104_haim_volozhin"             = "104"
    "105_israel_salanter"           = "105"
    "106_hafets_haim"               = "106"
    "107_hazon_ish"                 = "110"
    "108_hatam_sofer"               = "107"
    "109_samson_raphael_hirsch"     = "108"
    "110_sarah_schenirer"           = "111"
    "111_rav_kook"                  = "109"
    "112_rav_tsvi_kook"             = "112"
    "113_moshe_feinstein"           = "113"
    "114_rav_soloveitchik"          = "114"
    "115_nechama_leibowitz"         = "115"
    "116_rav_ovadia_yossef"         = "116"
    "117_rav_steinsaltz"            = "117"
    "118_jonathan_sacks"            = "118"
}

$count = 0
$errors = 0

foreach ($file in Get-ChildItem "$srcDir\*.png") {
    $baseName = $file.BaseName  # ex: "067_rabbenou_guershom"
    
    if ($mapping.ContainsKey($baseName)) {
        $newNum = $mapping[$baseName]
        $newName = "$newNum.png"
        Copy-Item $file.FullName "$outDir\$newName"
        
        if ($baseName.Substring(0,3) -ne $newNum) {
            Write-Host "  🔄 $baseName → $newName" -ForegroundColor Yellow
        } else {
            Write-Host "  ✅ $baseName → $newName"
        }
        $count++
    } else {
        Write-Host "  ❌ Pas de mapping pour : $baseName" -ForegroundColor Red
        $errors++
    }
}

Write-Host ""
Write-Host "═══ RÉSULTAT ═══"
Write-Host "  ✅ $count images remappées → $outDir"
if ($errors -gt 0) { Write-Host "  ❌ $errors erreurs" -ForegroundColor Red }
