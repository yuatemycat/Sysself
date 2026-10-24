# Hugging Face Hub, Cloud ML & Training Invariants

## 1. Ambient Token Authentication Invariant
- **Rule**: In all Hugging Face scripts, Colab/Vertex AI notebooks, and Python ML pipelines, **ALWAYS** inject the Hugging Face token globally into `os.environ["HF_TOKEN"]` and call `huggingface_hub.login(token=..., add_to_git_credential=False)` at the very start of the script—prior to any calls to `from_pretrained()`, `load_dataset()`, `hf_hub_download()`, or `Trainer`.
- **Root Cause & Technical Rationale**:
  - Even for public models, unauthenticated HTTP requests are classified by Hugging Face as "Anonymous".
  - Cloud datacenter IP ranges (Google Cloud / Colab, AWS, Azure) face strict anonymous rate limits and throttled CDN bandwidth.
  - Setting `os.environ["HF_TOKEN"]` ensures every internal `urllib3`/`requests` call sends the `Authorization: Bearer <token>` header, unlocking unthrottled CDN bandwidth, preventing rate-limiting errors, and silencing `Warning: You are sending unauthenticated requests to the HF Hub`.
- **Canonical Boilerplate**:
  ```python
  import os
  from huggingface_hub import login

  HF_TOKEN = os.environ.get("HF_TOKEN", "hf_...")
  os.environ["HF_TOKEN"] = HF_TOKEN
  try:
      login(token=HF_TOKEN, add_to_git_credential=False)
  except Exception as e:
      print(f"[*] HF Auth notice: {e}")
  ```

## 2. Model Export & Upload Hygiene (Zero-Disk Duplicate Serialization)
- **Rule**: When saving and uploading merged standalone models, **NEVER** call `model.push_to_hub()`.
- **Root Cause**: `model.push_to_hub()` re-serializes the entire model into `/tmp` or the hub cache, duplicating 15+ GB of files and crashing cloud VMs with `I/O error: No space left on device (os error 28)`.
- **Remediation**:
  1. Save locally with `model.save_pretrained(TARGET_DIR, max_shard_size="4GB", safe_serialization=True)` and `tokenizer.save_pretrained(TARGET_DIR)`.
  2. Stream upload the saved folder directly using `huggingface_hub.HfApi().upload_folder(folder_path=TARGET_DIR, repo_id=TARGET_REPO, repo_type="model", token=HF_TOKEN)`.

## 3. PEFT & Colab Dependency Conflict Safeguard (`torchao` Bug)
- **Rule**: In Colab environments running `peft`, always execute `!pip uninstall -y -q torchao` and defensively patch `peft.import_utils.is_torchao_available` before importing `PeftModel`.
- **Root Cause**: Colab pre-installs `torchao 0.10.0`, but modern `peft` requires either `torchao >= 0.16.0` or complete absence. An outdated package causes `ImportError: Found an incompatible version of torchao`.

## 4. Cloud Storage Partition Awareness (`/content` vs Root `/`)
- **Rule**: In Google Colab / Vertex AI environments, always write large datasets, model checkpoints, and merged weights into `/content` (e.g. `/content/model_dir`), never into `.` or `/root` unless verified.
- **Root Cause**: Colab mounts a large persistent partition (~100 GB) at `/content`, whereas the root filesystem `/` often has less than 15 GB free. Writing to `.` when current working directory is `/home/jupyter` or `/root` causes premature disk exhaustion.
