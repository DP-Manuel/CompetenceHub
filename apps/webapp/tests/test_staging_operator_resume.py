"""Existing-custody completion with synthetic DPAPI and fake GPG only.

Never run the completer on a real operator directory or open a real key home.
Native pinentry/encryption and cross-machine recovery remain separate gates.
"""

import pytest

from test_staging_operator_custody import SCRIPT, STUBBED_FLOW, powershell, run_private


@pytest.mark.parametrize(
    "case", ["success", "cancel", "mismatch", "dpapi", "backup-race", "store-race"]
)
def test_resume_verifies_existing_material_without_regeneration(
    powershell, tmp_path, case
):
    run_private(
        powershell,
        tmp_path,
        STUBBED_FLOW
        + r"""
try {
    $script:CorruptDecrypt=$true
    $failed=$false
    try { $null=Initialize-StagingOperatorConfig @inputs } catch { $failed=$true }
    if (-not $failed) { throw 'Synthetic interruption missing' }
    $store=Join-Path $directory $script:OperatorStoreName
    $backup=Join-Path $directory $script:OperatorBackupName
    $metadata=Join-Path $directory $script:OperatorMetadataName
    $beforeStore=(Get-FileHash -LiteralPath $store).Hash
    $beforeBackup=(Get-FileHash -LiteralPath $backup).Hash
    function New-StagingOperatorSecret { throw 'Resume must never generate keys' }
    function Invoke-StagingGpg {
        param($Executable,$KeyHome,$Mode,$InputBytes,$EncryptedPath,$OutputStream)
        if ($Mode -cne 'Decrypt' -or $InputBytes) { throw 'Resume must never encrypt/export' }
        if ($script:ResumeCase -ceq 'cancel') { throw 'Synthetic pinentry cancel' }
        if ($script:ResumeCase -ceq 'backup-race') { [IO.File]::AppendAllText($EncryptedPath,'synthetic-race') }
        if ($script:ResumeCase -ceq 'store-race') { [IO.File]::AppendAllText($store,'synthetic-race') }
        if ($script:ResumeCase -ceq 'mismatch') { $OutputStream.WriteByte(1) }
        else { $OutputStream.Write($script:SyntheticMemory,0,$script:SyntheticMemory.Length) }
    }
"""
        + f"\n$script:ResumeCase='{case}'\n"
        + r"""
    if ($script:ResumeCase -ceq 'dpapi') { function Import-Clixml { throw 'Synthetic other-user/machine refusal' } }
    $result=$null; $rejected=$false
    try { $result=Complete-StagingOperatorConfig @inputs } catch { $rejected=$true }
    if ($script:ResumeCase -ceq 'success') {
        if ($rejected -or $result.status -cne 'READY' -or -not $result.existing_keys_preserved -or
            $result.account_created -ne $false -or $result.database_access -cne 'NONE') { throw 'Completion failed' }
        # The actual existing loader must accept the completed metadata/payload.
        Use-StagingOperatorEnvironment -StorageDirectory $directory -AcknowledgeOperatorCustody -Action {
            if ($env:COMPETENCE_HUB_TOTP_ACTIVE_KEY_VERSION -cne 'staging-totp-v1') { throw 'Wrong existing key version' }
        }
        $repeated=$false
        try { $null=Complete-StagingOperatorConfig @inputs } catch { $repeated=$true }
        if (-not $repeated) { throw 'Metadata overwrite accepted' }
    } else {
        if (-not $rejected -or (Test-Path -LiteralPath $metadata)) { throw 'Failure published READY' }
        if (@(Get-ChildItem -LiteralPath $directory -Filter '*.pending' -Force).Count) { throw 'Pending metadata remains' }
    }
    if ($script:ResumeCase -cne 'store-race' -and (Get-FileHash -LiteralPath $store).Hash -cne $beforeStore) { throw 'DPAPI bytes replaced' }
    if ($script:ResumeCase -cne 'backup-race' -and (Get-FileHash -LiteralPath $backup).Hash -cne $beforeBackup) { throw 'Ciphertext replaced' }
} finally {
    if ($script:SyntheticMemory) { [Array]::Clear($script:SyntheticMemory,0,$script:SyntheticMemory.Length) }
}
""",
    )


def test_resume_requires_acknowledgments_and_rejects_prior_account_attempt(
    powershell, tmp_path
):
    run_private(
        powershell,
        tmp_path,
        STUBBED_FLOW + r"""
try {
    $script:CorruptDecrypt=$true
    try { $null=Initialize-StagingOperatorConfig @inputs } catch { }
    function Import-Clixml { throw 'Preflight must stop before opening synthetic keys' }
    function Invoke-StagingGpg { throw 'Preflight must stop before GPG' }
    foreach ($name in @('AcknowledgeProtectedStorage','AcknowledgeOperatorCustody')) {
        $bad=$inputs.Clone(); $bad.Remove($name)
        $rejected=$false
        try { $null=Complete-StagingOperatorConfig @bad } catch { $rejected=$true }
        if (-not $rejected) { throw 'Missing acknowledgment accepted' }
    }
    [IO.File]::WriteAllText((Join-Path $directory 'bootstrap-attempt.json'),'SYNTHETIC_ATTEMPT')
    $rejected=$false
    try { $null=Complete-StagingOperatorConfig @inputs } catch { $rejected=$_.Exception.Message -ceq 'Prior account attempt requires separate reconciliation.' }
    if (-not $rejected) { throw 'Prior account attempt accepted' }
} finally {
    if ($script:SyntheticMemory) { [Array]::Clear($script:SyntheticMemory,0,$script:SyntheticMemory.Length) }
}
""",
    )


def test_resume_has_explicit_dispatch_and_no_key_replacement_or_server_operations():
    source = SCRIPT.read_text(encoding="ascii")
    body = source.split("function Complete-StagingOperatorConfig", 1)[1].split(
        "function Use-StagingOperatorEnvironment", 1
    )[0]
    for forbidden in (
        "New-StagingOperatorSecret",
        "Export-Clixml",
        "-Mode Encrypt",
        "New-StagingPrivateDirectory",
        "Read-Host",
        "ssh ",
        "psql ",
        "New-Item",
    ):
        assert forbidden not in body
    assert "[IO.File]::Move($pending,$metadata,$false)" in body
    assert body.index("FixedTimeEquals($plain, $restored)") < body.index(
        "status='READY'"
    )
    assert "[switch]$ResumeExisting" in source
    assert "if ($ResumeExisting) { 'Complete-StagingOperatorConfig' }" in source


@pytest.mark.parametrize(
    "case",
    [
        "root-extra",
        "schema-bool",
        "variable-extra",
        "duplicate-key",
        "wrong-version",
        "wrong-ring-case",
    ],
)
def test_shared_payload_validation_rejects_invalid_existing_key_contract(
    powershell, tmp_path, case
):
    run_private(
        powershell,
        tmp_path,
        r"""
$secret=New-StagingOperatorSecret
$pointer=[IntPtr]::Zero
try {
    $pointer=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
    $text=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    $payload=$text | ConvertFrom-Json -AsHashtable
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer); $pointer=[IntPtr]::Zero; $text=$null
    Assert-StagingOperatorPayload $payload $script:OperatorKeyVersions
"""
        + f"\n$case='{case}'\n"
        + r"""
    switch ($case) {
        'root-extra' { $payload['unexpected']='SYNTHETIC' }
        'schema-bool' { $payload.schema=$true }
        'variable-extra' { $payload.variables['UNREVIEWED_VARIABLE']='SYNTHETIC' }
        'duplicate-key' { $payload.variables.COMPETENCE_HUB_IDEMPOTENCY_HMAC_KEY=$payload.variables.COMPETENCE_HUB_RATE_LIMIT_HMAC_KEY }
        'wrong-version' { $payload.variables.COMPETENCE_HUB_TOTP_ACTIVE_KEY_VERSION='unknown-version' }
        'wrong-ring-case' {
            $ring=$payload.variables.COMPETENCE_HUB_TOTP_KEYRING | ConvertFrom-Json -AsHashtable
            $payload.variables.COMPETENCE_HUB_TOTP_KEYRING=@{'STAGING-TOTP-V1'=$ring['staging-totp-v1']} | ConvertTo-Json -Compress
        }
    }
    $rejected=$false
    try { Assert-StagingOperatorPayload $payload $script:OperatorKeyVersions } catch { $rejected=$true }
    if (-not $rejected) { throw 'Invalid existing payload accepted' }
} finally {
    if ($pointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
    $secret.Dispose(); $payload=$null; $text=$null; $ring=$null
}
""",
    )
