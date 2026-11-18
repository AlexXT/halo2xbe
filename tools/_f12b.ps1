Add-Type @"
using System;
using System.Runtime.InteropServices;
public class K2 {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
}
"@
$p = Start-Process -FilePath "D:\mygame\halo2xbe\out\build\release\Game.exe" -WorkingDirectory "D:\mygame\halo2xbe\out\build\release" -PassThru
Start-Sleep -Seconds 15
$proc = Get-Process -Id $p.Id
$h = $proc.MainWindowHandle
[K2]::ShowWindow($h, 9) | Out-Null
[K2]::SetForegroundWindow($h) | Out-Null
for ($i = 0; $i -lt 3; $i++) {
  Start-Sleep -Seconds 4
  [K2]::PostMessage($h, 0x0100, [IntPtr]0x7B, [IntPtr]0) | Out-Null
}
Start-Sleep -Seconds 3
Get-ChildItem "D:\mygame\halo2xbe\out\build\release\screenshots" -ErrorAction SilentlyContinue | Select-Object Name, @{n='KB';e={[math]::Round($_.Length/1KB,1)}} | Format-Table -AutoSize
if (-not $p.HasExited) { $p.Kill() }
