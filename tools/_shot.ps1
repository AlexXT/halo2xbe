Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
$p = Start-Process -FilePath "D:\mygame\halo2xbe\out\build\release\Game.exe" -WorkingDirectory "D:\mygame\halo2xbe\out\build\release" -PassThru
Start-Sleep -Seconds 12
$proc = Get-Process -Id $p.Id
$h = $proc.MainWindowHandle
if ($h -eq 0) { "no main window yet"; }
else {
  "window handle: $h  title: $($proc.MainWindowTitle)"
  [Win]::ShowWindow($h, 9) | Out-Null
  [Win]::SetForegroundWindow($h) | Out-Null
  Start-Sleep -Milliseconds 800
  $r = New-Object Win+RECT
  [Win]::GetWindowRect($h, [ref]$r) | Out-Null
  "rect: $($r.L),$($r.T) - $($r.R),$($r.B)"
  $w = $r.R - $r.L; $ht = $r.B - $r.T
  if ($w -gt 0 -and $ht -gt 0) {
    $bmp = New-Object System.Drawing.Bitmap $w, $ht
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
    $bmp.Save("D:\mygame\halo2xbe\out\build\release\shot.png", [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    "saved shot.png ($w x $ht)"
  }
}
Start-Sleep -Seconds 2
if (-not $p.HasExited) { "still running: no crash" } else { "exited 0x$('{0:X8}' -f $p.ExitCode)" }
if (-not $p.HasExited) { $p.Kill() }
