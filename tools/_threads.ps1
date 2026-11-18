Add-Type @"
using System;
using System.Runtime.InteropServices;
public class TD {
  [DllImport("kernel32.dll", SetLastError=true)] public static extern IntPtr OpenThread(uint access, bool inherit, uint id);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern int GetThreadDescription(IntPtr h, out IntPtr desc);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
  [DllImport("kernel32.dll")] public static extern IntPtr LocalFree(IntPtr p);
}
"@
$p = Start-Process -FilePath "D:\mygame\halo2xbe\out\build\release\Game.exe" -WorkingDirectory "D:\mygame\halo2xbe\out\build\release" -PassThru
Start-Sleep -Seconds 12
$th = (Get-Process -Id $p.Id).Threads | Sort-Object TotalProcessorTime -Descending | Select-Object -First 8
foreach ($t in $th) {
  $name = "(unnamed)"
  $h = [TD]::OpenThread(0x0800, $false, $t.Id)   # THREAD_QUERY_LIMITED_INFORMATION
  if ($h -ne [IntPtr]::Zero) {
    $d = [IntPtr]::Zero
    if ([TD]::GetThreadDescription($h, [ref]$d) -eq 0 -and $d -ne [IntPtr]::Zero) {
      $name = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($d)
      [TD]::LocalFree($d) | Out-Null
    }
    [TD]::CloseHandle($h) | Out-Null
  }
  "  id {0,-6} cpu {1,6:N2}s  state {2,-10} {3}" -f $t.Id, $t.TotalProcessorTime.TotalSeconds, $t.ThreadState, $name
}
if (-not $p.HasExited) { $p.Kill() }
