param()
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$archive = Join-Path $root 'docs/history/context-migration-2026-10-21'
$records = Get-Content -Raw -LiteralPath (Join-Path $archive 'manifest.json') | ConvertFrom-Json
foreach ($record in $records) {
    $snapshotName = if ($record.PSObject.Properties.Name -contains 'archive_path') { $record.archive_path } else { $record.path }
    $file = Join-Path $archive $snapshotName
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $record.sha256) {
        throw "Archive hash mismatch: $($record.path)"
    }
}
$routes = @(
    'AGENTS.md', 'PROJECT_CONTEXT.md', 'PROJECT_STATUS.md', 'PROJECT_PLAN.md',
    'PROJECT_LOG.md', 'SKILL_FEEDBACK_LOG.md', 'README.md', 'CHATGPT_PROJECT_BRIEF.md',
    'docs/architecture/PROJECT_CONTEXT_POLICY.md', 'docs/architecture/index.md',
    'docs/architecture/environment-policy.md', 'docs/content/index.md',
    'docs/requirements/index.md', 'docs/operations/index.md', 'docs/history/index.md',
    'docs/exec-plans/active/post-messe-backend-horizon-2026-10.md',
    'docs/exec-plans/completed/post-messe-konsolidierung-2026-10.md',
    'docs/requirements/post-messe-product-2026-10-21.md',
    'docs/requirements/analytics-01-discovery-2026-10-21.md',
    'docs/decisions/PRIV-ANALYTICS-01.md',
    'docs/architecture/context-migration-audit-2026-10-21.md'
)
$links = 0
foreach ($route in $routes) {
    $path = Join-Path $root $route
    $content = Get-Content -Raw -LiteralPath $path
    foreach ($match in [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)')) {
        $target = $match.Groups[1].Value
        if ($target -match '^(https?://|#)') { continue }
        $relative = ($target -split '#', 2)[0]
        if (-not (Test-Path -LiteralPath (Join-Path (Split-Path $path -Parent) $relative))) {
            throw "Broken router link in ${route}: $target"
        }
        $links++
    }
}
$boot = @('AGENTS.md', 'PROJECT_CONTEXT.md')
$before = @($records | Where-Object { $_.path -in @('AGENTS.md', 'PROJECT_STATUS.md', 'PROJECT_PLAN.md', 'PROJECT_LOG.md') })
$afterBytes = ($boot | ForEach-Object { (Get-Item -LiteralPath (Join-Path $root $_)).Length } | Measure-Object -Sum).Sum
$afterLines = ($boot | ForEach-Object { [IO.File]::ReadAllLines((Join-Path $root $_)).Length } | Measure-Object -Sum).Sum
$beforeBytes = ($before | Measure-Object -Property bytes -Sum).Sum
$beforeLines = ($before | Measure-Object -Property lines -Sum).Sum
[pscustomobject]@{
    archive_files_verified = @($records).Count
    router_files_verified = $routes.Count
    local_links_verified = $links
    before_default_files = $before.Count
    before_default_lines = $beforeLines
    before_default_bytes = $beforeBytes
    after_default_files = $boot.Count
    after_default_lines = $afterLines
    after_default_bytes = $afterBytes
    byte_reduction_percent = [Math]::Round((1 - $afterBytes / $beforeBytes) * 100, 1)
} | ConvertTo-Json
