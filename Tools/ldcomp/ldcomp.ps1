# +-----------------------------------------------+
# |            Labrune Dump Comparator            |
# +-----------------------------------------------+
# | Author: LondonCity                            |
# | Date:   03.05.2026                            |
# +-----------------------------------------------+

try {
    Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase -ErrorAction Stop
}
catch {
    
}

# Basisverzeichnis ermitteln
$Base = [System.IO.Path]::GetDirectoryName([System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
$xamlPath = Join-Path $Base "ldcomp.xaml"

# XAML laden
[xml]$xaml = Get-Content -Raw $XamlPath
$reader = New-Object System.Xml.XmlNodeReader($xaml)
$window = [Windows.Markup.XamlReader]::Load($reader)

# Referenzieren
$File1Box     = $window.FindName("File1Box")
$File2Box     = $window.FindName("File2Box")
$BtnFile1     = $window.FindName("BtnFile1")
$BtnFile2     = $window.FindName("BtnFile2")
$BtnCompare   = $window.FindName("BtnCompare")
$BtnSave      = $window.FindName("BtnSave")
$OutputBox    = $window.FindName("OutputBox")
$StatusText   = $window.FindName("StatusText")
$BtnSplitView = $window.FindName("BtnSplitView")
$BtnAbout     = $window.FindName("BtnAbout")


function Add-ColoredLine {
    param(
        [string]$Text,
        [string]$Color
    )

    # WPF Paragraph
    $paragraph = New-Object System.Windows.Documents.Paragraph
    $paragraph.Margin = [System.Windows.Thickness]::new(0)   # <-- Abstand entfernen
    $paragraph.Padding = [System.Windows.Thickness]::new(0)  # <-- Sicherheitshalber

    # Run erzeugen
    $run = New-Object System.Windows.Documents.Run
    $run.Text = $Text
    $run.Foreground = $Color

    # Run in Paragraph einfügen
    $paragraph.Inlines.Add($run)

    # Paragraph in RichTextBox einfügen
    $OutputBox.Document.Blocks.Add($paragraph)
}

function Get-TableLines {
    param([string]$Path)
    Get-Content -Encoding utf8 -Path $path | Select-Object -Skip 6
}

function Show-SplitView {

    # Basisverzeichnis ermitteln
    $Base = [System.IO.Path]::GetDirectoryName([System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
    $xamlPath = Join-Path $Base "splitview.xaml"

    # XAML laden
    [xml]$xaml = Get-Content -Raw $XamlPath
    $reader = New-Object System.Xml.XmlNodeReader($xaml)
    $window = [Windows.Markup.XamlReader]::Load($reader)

    $LeftBox  = $window.FindName("LeftBox")
    $RightBox = $window.FindName("RightBox")

    # Hilfsfunktion: farbige Zeile hinzufügen
    function Add-ColoredLine {
        param(
            [System.Windows.Controls.RichTextBox]$Box,
            [string]$Text,
            [System.Windows.Media.Brush]$Color
        )

        $paragraph = New-Object System.Windows.Documents.Paragraph
        $paragraph.Margin = [System.Windows.Thickness]::new(0)

        $run = New-Object System.Windows.Documents.Run
        $run.Text = $Text
        $run.Foreground = $Color

        $paragraph.Inlines.Add($run)
        $Box.Document.Blocks.Add($paragraph)
    }

    # Dateien laden (vom Hauptfenster übergeben)
    $File1 = $env:VCOMP_FILE1
    $File2 = $env:VCOMP_FILE2

    if (-not (Test-Path $File1) -or -not (Test-Path $File2)) {
        Add-ColoredLine $LeftBox  "File paths invalid." ([System.Windows.Media.Brushes]::Red)
        Add-ColoredLine $RightBox "File paths invalid." ([System.Windows.Media.Brushes]::Red)
        $window.ShowDialog() | Out-Null
        return
    }

    # Funktion zum Laden der relevanten Zeilen
    function Get-TableLines {
        param([string]$Path)
        Get-Content -Encoding utf8 -Path $Path | Select-Object -Skip 6
    }

    # Vergleich durchführen
    $lines1 = Get-TableLines $File1
    $lines2 = Get-TableLines $File2

    $diff = Compare-Object -ReferenceObject $lines1 -DifferenceObject $lines2 -IncludeEqual:$false

    $added   = $diff | Where-Object { $_.SideIndicator -eq '=>' } | ForEach-Object { $_.InputObject }
    $removed = $diff | Where-Object { $_.SideIndicator -eq '<=' } | ForEach-Object { $_.InputObject }

    # HashSets für schnellen Lookup
    $addedSet   = [System.Collections.Generic.HashSet[string]]::new()
    $removedSet = [System.Collections.Generic.HashSet[string]]::new()

    foreach ($line in $added) {
        if ($line -and $line.Trim() -ne "") {
            $addedSet.Add($line) | Out-Null
        }
    }

    foreach ($line in $removed) {
        if ($line -and $line.Trim() -ne "") {
            $removedSet.Add($line) | Out-Null
        }
    }

    # Datei 1 anzeigen (links)
    foreach ($line in $lines1) {
        if ($removedSet.Contains($line)) {
            Add-ColoredLine $LeftBox "- $line" ([System.Windows.Media.Brushes]::Red)
        }
        else {
            Add-ColoredLine $LeftBox "  $line" ([System.Windows.Media.Brushes]::Black)
        }
    }

    # Datei 2 anzeigen (rechts)
    foreach ($line in $lines2) {
        if ($addedSet.Contains($line)) {
            Add-ColoredLine $RightBox "+ $line" ([System.Windows.Media.Brushes]::Green)
        }
        else {
            Add-ColoredLine $RightBox "  $line" ([System.Windows.Media.Brushes]::Black)
        }
    }

    $window.ShowDialog() | Out-Null

}

function Show-About {

    # Basisverzeichnis ermitteln
    $Base = [System.IO.Path]::GetDirectoryName([System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
    $xamlPath = Join-Path $Base "about.xaml"
    
    # XAML laden
    [xml]$xaml = Get-Content -Raw $XamlPath
    $reader = New-Object System.Xml.XmlNodeReader($xaml)
    $window = [Windows.Markup.XamlReader]::Load($reader)

    $BtnClose = $window.FindName("BtnClose")
    $BtnClose.Add_Click({ $window.Close() })

    $GithubLink = $window.FindName("GithubLink")
    $GithubLink.Add_Click({
        Start-Process $GithubLink.NavigateUri.AbsoluteUri
    })

    $window.ShowDialog() | Out-Null

}

# Datei auswählen
$BtnFile1.Add_Click({
    $dlg = New-Object Microsoft.Win32.OpenFileDialog
    if ($dlg.ShowDialog()) { $File1Box.Text = $dlg.FileName }
})

$BtnFile2.Add_Click({
    $dlg = New-Object Microsoft.Win32.OpenFileDialog
    if ($dlg.ShowDialog()) { $File2Box.Text = $dlg.FileName }
})

# Vergleich starten
$BtnCompare.Add_Click({
    $OutputBox.Document.Blocks.Clear()
    $BtnSave.IsEnabled = $false

    $file1 = $File1Box.Text
    $file2 = $File2Box.Text

    if (-not (Test-Path $file1) -or -not (Test-Path $file2)) {
        Add-ColoredLine "Please select valid Labrune Dump files." "Red"
        return
    }

    # Identitätsprüfung
    $hash1 = Get-FileHash $file1 -Algorithm SHA256
    $hash2 = Get-FileHash $file2 -Algorithm SHA256

    if ($hash1.Hash -eq $hash2.Hash) {
        Add-ColoredLine "The compared Labrune Dump files are identical." "Green"
        $BtnSave.IsEnabled = $true
        return
    }

    # Vergleich
    $lines1 = Get-TableLines $file1
    $lines2 = Get-TableLines $file2

    $diff = Compare-Object $lines1 $lines2 -IncludeEqual:$false

    $added   = $diff | Where-Object { $_.SideIndicator -eq '=>' } | ForEach-Object { $_.InputObject }
    $removed = $diff | Where-Object { $_.SideIndicator -eq '<=' } | ForEach-Object { $_.InputObject }

    # Statistik
    Add-ColoredLine "Comparison Statistics:" "Black"
    Add-ColoredLine "  Added: $($added.Count)" "Green"
    Add-ColoredLine "  Removed:    $($removed.Count)" "Red"
    Add-ColoredLine "  Total:      $($added.Count + $removed.Count)" "Black"
    Add-ColoredLine "" "Black"

    if ($added) {
        Add-ColoredLine "Added Lines:" "Green"
        foreach ($line in $added) { Add-ColoredLine "+ $line" "Green" }
        Add-ColoredLine "" "Black"
    }

    if ($removed) {
        Add-ColoredLine "Removed Lines:" "Red"
        foreach ($line in $removed) { Add-ColoredLine "- $line" "Red" }
    }

    $BtnSave.IsEnabled = $true
})

# Speichern
$BtnSave.Add_Click({
    $dlg = New-Object Microsoft.Win32.SaveFileDialog
    $dlg.Filter = "Textfile (*.txt)|*.txt"
    $dlg.FileName = "ComparisonResult.txt"

    if ($dlg.ShowDialog()) {
        $text = New-Object System.Windows.Documents.TextRange($OutputBox.Document.ContentStart, $OutputBox.Document.ContentEnd)
        $text.Text | Out-File $dlg.FileName -Encoding utf8
        $StatusText.Text = "Result saved."
    }
})

$BtnSplitView.Add_Click({
    $env:VCOMP_FILE1 = $File1Box.Text
    $env:VCOMP_FILE2 = $File2Box.Text
    Show-SplitView
})


$BtnAbout.Add_Click({
    Show-About
})


# Fenster anzeigen
$window.ShowDialog() | Out-Null
