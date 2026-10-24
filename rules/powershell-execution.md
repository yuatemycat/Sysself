# PowerShell Execution & Script Safety Rule

When executing shell commands via `run_command` or automating scripts on Windows:

## 1. Avoid Risky Inline Double-Quoted PowerShell Scripts
- In PowerShell, invoking inline commands with double quotes (e.g. `powershell -Command "..."`) containing variables such as `$_`, `$input`, or `$env:NAME` leads to premature expansion or variable corruption before execution.
- If inline PowerShell is required, use single-quoted scriptblocks or explicitly escape symbols with backticks (e.g. `` `$_ ``).

## 2. Prefer Batch or Dedicated Script Files for Environment Setups
- When configuring environments with custom paths (`PATH`, `INCLUDE`, `LIB`, `LIBCLANG_PATH`) and running native builds, prefer calling standard batch wrappers:
  ```cmd
  cmd.exe /c "call E:\03_Devops\env.bat && <command>"
  ```
- For complex multi-step orchestration, generate a dedicated script file (`.bat` or `.ps1`) and execute it directly rather than sending large inline commands.

## 3. Command Chaining and Working Directory Switching
- In `cmd.exe /c`, wrap chained statements (`&&`, `&`) in outer quotes:
  ```cmd
  cmd.exe /c "call env.bat && cd /d E:\project && npm run build"
  ```
- Always use `cd /d` to safely switch across different drive volumes (e.g. `C:` to `E:`).

## 4. Text Redirection & Encoding Invariant (PowerShell 5.1 UTF-16LE Pitfall)
- In Windows PowerShell 5.1, redirecting command output with `>` or `>>` produces **UTF-16LE with BOM**, which breaks Unix/Git tools (e.g. `git apply` fails with `error: No valid patches in input`).
- When generating `.patch`, `.diff`, or tool files that require raw ASCII/UTF-8:
  - Use `cmd.exe /c "command > output.patch 2>nul"` or write raw bytes with `[System.IO.File]::WriteAllBytes(...)`.
  - Do not rely on PowerShell `>` redirection for external tool inputs/outputs.

## 5. PowerShell 5.1 vs Core Cmdlet Parameter Compatibility
- Avoid PowerShell 7-only parameters when running in default Windows PowerShell 5.1.
  - Example: `Test-Connection` in 5.1 requires `-ComputerName` (do not use `-TargetName`, which fails on 5.1).

## 6. Non-Standard Zip Archive Extensions (.xapk, .apk, .jar, .aar, .whl)
- In Windows PowerShell 5.1, `Expand-Archive` strictly enforces the `.zip` file extension and fails with `NotSupportedArchiveFileExtension` on `.xapk`, `.apk`, `.jar`, `.aar`, or `.whl` files.
- **Invariant**: Do not attempt `Expand-Archive` on non-`.zip` targets. Use .NET's `ZipFile` assembly directly in PowerShell scripts:
  ```powershell
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [System.IO.Compression.ZipFile]::ExtractToDirectory($sourcePath, $destinationPath)
  ```
- For in-memory entry inspection without disk extraction:
  ```powershell
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $zip = [System.IO.Compression.ZipFile]::OpenRead($sourcePath)
  $zip.Entries | Select-Object FullName, Length, CompressedLength
  $zip.Dispose()
  ```

## 7. Python Inline Script Quoting Invariant (`python -c` vs Script Files)
- In PowerShell, invoking complex or multiline Python snippets via `python -c "..."` frequently fails due to PowerShell's parser misinterpreting escaped double quotes (`\"`), Python format strings (`f"..."`), or regex characters as shell tokens (`TerminatorExpectedAtEndOfString`, `ParameterBindingException`).
- **Mandatory Invariant**: Never chain multiline inline Python strings with quotes or regex in PowerShell. Always write the script to a dedicated `.py` file in the project workspace (or scratch directory) and execute it cleanly via `python path\to\script.py`.
- Always explicitly enforce UTF-8 file I/O in written scripts to avoid Windows default code page (`cp1252`) encoding crashes on non-ASCII characters.

## 8. Filesystem Links & Junctions (`mklink` vs `New-Item`)
- `mklink` is an internal built-in command of `cmd.exe`, **NOT** an executable on `PATH` or a PowerShell cmdlet. Executing `mklink` directly in PowerShell results in `CommandNotFoundException`.
- **Mandatory Pattern**:
  - When creating Directory Junctions in PowerShell, use:
    ```powershell
    New-Item -ItemType Junction -Path "<link-path>" -Target "<target-path>"
    ```
  - Or explicitly invoke through CMD:
    ```powershell
    cmd.exe /c mklink /J "<link-path>" "<target-path>"
    ```
  - For symbolic links, use `New-Item -ItemType SymbolicLink -Path ... -Target ...` (requires Developer Mode or administrative elevation).

