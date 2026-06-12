<#
.SYNOPSIS
    Create a new standard project skeleton under D:\reasonix-workspace
.DESCRIPTION
    Auto-scan existing project numbers, assign next number,
    copy template, auto-fill placeholders, update register table.
.PARAMETER ProjectName
    Project name (Chinese or English, no illegal chars)
.EXAMPLE
    .\create_project.ps1 -ProjectName "knowledge-base"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName
)

# Config
$workspaceRoot = "D:\reasonix-workspace"
$templateDir = Join-Path $workspaceRoot "templates\project_template"

# 1. Validate project name
$illegalChars = [System.IO.Path]::GetInvalidFileNameChars()
foreach ($c in $illegalChars) {
    if ($ProjectName.Contains($c)) {
        Write-Error "Project name contains illegal char: $c"
        exit 1
    }
}

# 2. Scan existing projects for next number
$existing = Get-ChildItem -Path $workspaceRoot -Directory | Where-Object { $_.Name -match "^Project_(\d{3})_" }
$nextNum = 1
if ($existing) {
    $maxNum = $existing | ForEach-Object { [int]($_.Name -replace "^Project_(\d{3})_.*", "$1") } | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum
    $nextNum = $maxNum + 1
}
$numStr = $nextNum.ToString("000")
$projectDirName = "Project_${numStr}_${ProjectName}"
$projectPath = Join-Path $workspaceRoot $projectDirName

# 3. Check if target exists
if (Test-Path $projectPath) {
    Write-Error "Target directory already exists: $projectPath"
    exit 1
}

# 4. Copy template
Write-Host "Creating project: $projectDirName"
Copy-Item -Path $templateDir -Destination $projectPath -Recurse
Write-Host "Project directory created: $projectPath"

# 5. Auto-fill placeholders in template files
$today = Get-Date -Format "yyyy-MM-dd"

Write-Host "Filling template placeholders..."
$replaces = @{
    "Project_XXX_项目名称" = "Project_${numStr}_${ProjectName}"
    "XXX"                 = $numStr
    "YYYY-MM-DD"          = $today
}

$templateFiles = Get-ChildItem -Path $projectPath -Filter "*.md" -Recurse
foreach ($file in $templateFiles) {
    $content = Get-Content $file.FullName -Encoding UTF8 -Raw
    $changed = $false
    foreach ($key in $replaces.Keys) {
        if ($content -match [regex]::Escape($key)) {
            $content = $content -replace [regex]::Escape($key), $replaces[$key]
            $changed = $true
        }
    }
    if ($changed) {
        $content | Set-Content $file.FullName -Encoding UTF8
        Write-Host "  Filled: $($file.Name)"
    }
}

# 6. Update global console register table
$consoleFile = Join-Path $workspaceRoot "99-全局控制台.md"
$newEntry = "| $numStr | $ProjectName | $today | 进行中 |"
$content = Get-Content $consoleFile -Encoding UTF8
$found = $false
$newContent = @()
foreach ($line in $content) {
    $newContent += $line
    if ($line -match "^\| \- \| \- \| \- \| \- \|$") {
        $found = $true
        $newContent += $newEntry
    }
}
if (-not $found) {
    $newContent += ""
    $newContent += $newEntry
}
$newContent | Set-Content $consoleFile -Encoding UTF8
Write-Host "Register table updated"

Write-Host ""
Write-Host "=== Done ==="
Write-Host "Project : $projectDirName"
Write-Host "Path    : $projectPath"
Write-Host "Date    : $today"
Write-Host ""
Write-Host "Next: open $projectPath to start development"
