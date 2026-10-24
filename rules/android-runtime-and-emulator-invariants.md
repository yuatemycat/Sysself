# Android Runtime, Emulator & Native Bridge Invariants

When automating, debugging, or patching Android applications, emulators (QEMU/AOSP), or ARM64 native bridges:

## 1. Framework Readiness Invariant (`stop; start` vs Boot Status)
- In AOSP/emulators, restarting Zygote via `stop; start` does NOT reset `sys.boot_completed` (it remains `1` from initial boot).
- Never rely on `getprop sys.boot_completed` to verify framework readiness after a runtime restart.
- **Mandatory Readiness Gate**: Always poll `adb shell "service check window"` until it returns `Service window: found` before injecting intents, monkey events, or interacting with activities.

## 2. Deterministic Application Launching
- Avoid using `monkey -p <package> -c android.intent.category.LAUNCHER 1` as the primary launch mechanism; it frequently aborts with `No activities found to run` if launcher activities or window managers are still reconciling.
- Always use deterministic component launch:
  ```sh
  adb shell am start -n <package>/<activity>
  ```
- If the main activity name is unknown, resolve it explicitly with:
  ```sh
  adb shell "cmd package resolve-activity --brief <package> | tail -n 1"
  ```

## 3. In-Memory Patching Scope & Collateral Damage Prevention
- **Never Patch Zygote In-Memory via Background Loops**: Zygote (`zygote64`) is the template for all system and application processes. In-memory pattern scanning and patching on Zygote memory risks false-positive collisions with system libraries (e.g. `libandroid_runtime.so` SQLite bindings), corrupting `com.android.networkstack.process` or `system_server` with fatal `SEGV_MAPERR` crashes.
- **Target-Specific Scoping**:
  - Always resolve and verify the specific target PID via `/proc/<pid>/cmdline`.
  - Apply in-memory patches exclusively to the target application process.
  - Utilize process-halting states (e.g. synchronization pipes or handshake reads) to safely apply patches before application initialization resumes.

## 4. ARM64 Native Bridge Translation Invariants (QEMU / `libndk_translation`)
- **The `wrap.<package>` Trap**: Never set `setprop wrap.<package> "LD_PRELOAD=..."` for ARM64 applications on x86_64 emulators. Setting `wrap.*` forces the process to spawn via `WrapperInit` and `app_process64` outside Zygote's normal fork flow, completely breaking `libndk_translation` initialization with `EM_AARCH64 instead of EM_X86_64` linker crashes.
- **Zygote Mount Inheritance**: In-memory or bind-mount modifications to native bridge libraries (`/system/lib64/libndk_translation.so`) require a clean `stop; start` restart so newly spawned processes inherit the updated mappings.
- **Dual Syscall Neutralization**:
  - Anti-tamper frameworks (such as Promon SHIELD) invoke inline `svc` assembly for termination.
  - Both ARM64 `exit` (syscall 93 -> host x86_64 syscall 60 / `0x3c`) and `exit_group` (syscall 94 -> host x86_64 syscall 231 / `0xe7`) must be neutralized at the native translation bridge (`RunKernelSyscall`), as they bypass both guest and host `libc.so` GOT stubs.

## 5. Serial Port Explicitness
- Always specify `-s <serial>` (e.g. `-s emulator-5564`) on every ADB command. Never assume default `emulator-5554` when working with custom instances or multi-device setups.
