# Windows Background Automation & Power Event Invariants

When creating automated background services, scheduled tasks, or wake/startup hooks on Windows:

## 1. Power State Resume Triggers (Modern Standby vs Sleep)
- Modern Windows 11 laptops utilize **Modern Standby (S0 Low Power Idle)** rather than legacy S3 sleep.
- Task Scheduler and event-driven wake automation MUST subscribe to:
  - **Modern Standby Exit**: `Microsoft-Windows-Kernel-Power`, Event ID `507`
  - **Legacy Sleep Resume**: `Microsoft-Windows-Kernel-Power`, Event ID `107`
  - **Power Troubleshooter**: `Microsoft-Windows-Power-Troubleshooter`, Event ID `1`
  - **Logon / Boot**: `LogonTrigger` for restarts and user logins.

## 2. Mandatory Wake Debounce & Concurrency Guard
- Windows power transitions emit multiple related events in rapid succession (e.g. session transitions, display on, standby exit).
- Always implement a file-based cooldown lock (e.g. 60-second threshold) checking `LastWriteTime` at the start of any wake-triggered script to immediately terminate duplicate invocations.

## 3. Zero-Console Silent Execution
- Scheduled Tasks invoking PowerShell directly (even with `-WindowStyle Hidden`) momentarily flash a console window on screen.
- For 100% invisible background execution, invoke the script through a lightweight VBScript wrapper:
  ```vbs
  Set oShell = CreateObject("WScript.Shell")
  oShell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""...""", 0, False
  ```

## 4. Git Auto-Backup & Untracked File Safety
- Storing only untracked file paths leaves content vulnerable to data loss.
- **Safety Pattern**:
  - Exclude files matched by `.gitignore`.
  - For files <= 5 MiB: Auto-stage with `git add` to preserve contents in Git's object database and include them in binary diffs (`git diff --binary HEAD`) and Git bundles (`git bundle create`).
  - For files > 5 MiB: Skip Git staging to prevent repository bloat, logging them in an inventory manifest.

## 5. Diagnosing Broken Script Host Launchers (`wscript.exe` / `cscript.exe`)
- When a `Windows Script Host: Can not find script file` popup is active on screen, the triggering source is often not in Task Scheduler or Registry `Run` keys, but invoked by `explorer.exe` through Desktop or Start Menu shortcuts.
- **Diagnostic Invariant**:
  - Query the live `wscript.exe` instance and its parent process before dismissing the dialog:
    ```powershell
    Get-CimInstance Win32_Process -Filter "Name = 'wscript.exe'" | Select-Object ProcessId, ParentProcessId, CommandLine
    ```
  - Inspect the parent process (`Win32_Process` by `ProcessId = $parentPid`) to determine if the caller is `explorer.exe` (user shortcut / shell launch), `taskeng.exe` / `svchost.exe` (Task Scheduler), or another background supervisor.
  - Audit Desktop and Start Menu shortcut arguments across both user and public directories:
    ```powershell
    $wsh = New-Object -ComObject WScript.Shell
    @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs')) | ForEach-Object {
        Get-ChildItem -Path $_ -Filter '*.lnk' -Recurse | ForEach-Object {
            $sc = $wsh.CreateShortcut($_.FullName)
            if ($sc.Arguments -like "*<script-name>*" -or $sc.TargetPath -like "*<script-name>*") {
                [PSCustomObject]@{ File = $_.FullName; Target = $sc.TargetPath; Args = $sc.Arguments }
            }
        }
    }
    ```

## 6. Project Relocation & Renaming Invariant (`E:\02_Projects`)
- Renaming an active project directory in `E:\02_Projects` immediately breaks existing Desktop shortcuts, Start Menu entries, IDE configurations, and background scripts hardcoded to the old folder path.
- **Immediate Safeguard**:
  - Immediately establish an NTFS Directory Junction from the legacy project path to the new path before performing file audits:
    ```powershell
    New-Item -ItemType Junction -Path "E:\02_Projects\<OldName>" -Target "E:\02_Projects\<NewName>"
    ```
  - This ensures zero-downtime continuity for external tools, launchers, and user shortcuts while source code, scripts, and shortcut references are migrated to the canonical name.
