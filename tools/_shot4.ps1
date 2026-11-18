Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win3 {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
$p = Start-Process -FilePath "D:\mygame\halo2xbe\out\build\release\Game.exe" -WorkingDirectory "D:\mygame\halo2xbe\out\build\release" -PassThru
Start-Sleep -Seconds 75
$proc = Get-Process -Id $p.Id
$h = $proc.MainWindowHandle
[Win3]::ShowWindow($h, 9) | Out-Null
[Win3]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Seconds 2
$r = New-Object Win3+RECT
[Win3]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.R - $r.L; $ht = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
[Win3]::PrintWindow($h, $dc, 2) | Out-Null
$g.ReleaseHdc($dc)
$bmp.Save("D:\mygame\halo2xbe\out\build\release\shot2.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"saved shot2.png"
if (-not $p.HasExited) { "still running" } else { "exited 0x$('{0:X8}' -f $p.ExitCode)" }
if (-not $p.HasExited) { $p.Kill() }
