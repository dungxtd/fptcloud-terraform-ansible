# Disable Windows Firewall completely
Write-Host "Disabling Windows Firewall..."

# Disable Windows Firewall for all profiles
netsh advfirewall set allprofiles state off
Write-Host "Firewall disabled via netsh"

# Disable via PowerShell cmdlets
try {
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
    Write-Host "Firewall disabled via PowerShell cmdlets"
} catch {
    Write-Host "PowerShell cmdlet failed: $($_.Exception.Message)"
}

# Stop and disable Windows Firewall service
try {
    Stop-Service -Name "MpsSvc" -Force -ErrorAction SilentlyContinue
    Set-Service -Name "MpsSvc" -StartupType Disabled
    Write-Host "Windows Firewall service stopped and disabled"
} catch {
    Write-Host "Service stop failed: $($_.Exception.Message)"
}

# Disable Windows Firewall via registry
$regPaths = @(
    "HKLM:\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\DomainProfile",
    "HKLM:\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\PublicProfile",
    "HKLM:\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile"
)

foreach ($path in $regPaths) {
    try {
        Set-ItemProperty -Path $path -Name "EnableFirewall" -Value 0 -Type DWord
    } catch {
        Write-Host "Registry update failed for $path"
    }
}
Write-Host "Firewall disabled via registry"

Write-Host "Windows Firewall has been completely disabled."
