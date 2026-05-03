# +-----------------------------------------------+
# | UTF‑8 Export for NFSCO Localiaztion Databases |
# +-----------------------------------------------+
# | Author: LondonCity                            |
# | Date:   26.04.2026                            |
# +-----------------------------------------------+

$ErrorActionPreference = "Stop"

try {

    $dir = [System.IO.Path]::GetDirectoryName([System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
    $countryCode = Split-Path $dir -Leaf
    $map = @{
        "BR"       = "brportuguese"
        "CN_simp"  = "chinese_simp"
        "CN_trad"  = "chinese_trad"
        "CZ"       = "czech"
        "DE"       = "german"
        "DK"       = "danish"
        "EN"       = "english"
        "ES"       = "spanish"
        "FI"       = "finnish"
        "FR"       = "french"
        "HU"       = "hungarian"
        "IT"       = "italian"
        "JP"       = "japanese"
        "KR"       = "korean"
        "MX"       = "mexican"
        "NL"       = "dutch"
        "PO"       = "polish"
        "RU"       = "russian"
        "SE"       = "swedish"
        "TH"       = "thai"
    }

    if (-not $map.ContainsKey($countryCode)) {
        Write-Host "ERROR: The directory you are currently operating in ('$countryCode') does not correspond to a valid country code." -ForegroundColor Red
        exit 1
    }

    $loc = $map[$countryCode]
    $db  = "$dir\nfsco_loc_$($countryCode.ToLower()).db"

    if (-not (Test-Path $db)) {
        Write-Host "ERROR: The database '$db' was not found." -ForegroundColor Red
        exit 1
    }

    $tables = sqlite3 $db "SELECT name FROM sqlite_master WHERE type='table' AND (name='frontend.bin' OR name='global.bin' OR name='ingame.bin');"

    foreach ($table in $tables) {

        # Preparing SQL query (using sqlite)
        $query = "SELECT ""Chunk"", ""Hash (Hex)"", ""Label"", ""Value_$countryCode"" FROM ""$table"";"
        $export = "$dir\$loc" + "_" + "${table}.txt"
        $tableNameClean = ($table -replace '\.bin','')
        $tableNameClean = $tableNameClean.Substring(0,1).ToUpper() + $tableNameClean.Substring(1)

        # Header for Labrune dump file
        $header = @"
#       NFSCO Localization Export for Labrune - $export
#       File created on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
#
#Chunk  Hash (HEX)      Label           Value
# ---------------------------------------------------------------------------------------------------------
# Chunk 0 - $tableNameClean
"@

        # sqlite3 call via STDIN
        $sqlLines = @(
            ".mode tabs"
            ".headers off"
            ".once '$export'"
            $query
        )

        $sqlText = $sqlLines -join "`n"
        $sqlText | & sqlite3 $db

        $content = Get-Content $export -Encoding UTF8 | ForEach-Object { $_ -replace '"', '' }
        $header | Out-File $export -Encoding UTF8
        $content | Add-Content $export -Encoding UTF8

    }

    Write-Host "Export for language '$loc' successful." -ForegroundColor Green

}
catch {
    # Error handling
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
