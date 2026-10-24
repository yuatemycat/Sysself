# DeepSeek Fill-In-The-Middle (FIM) Completion Protocol

DeepSeek code models utilize dedicated special tokens for Fill-In-The-Middle (FIM) repository-level auto-completion:

## Special Tokens
- Prefix Begin: `<｜fim begin｜>`
- Suffix / Hole: `<｜fim hole｜>`
- Completion End: `<｜fim end｜>`

## Completion Envelope
```
<｜fim begin｜>{file_prefix_context}
<｜fim hole｜>{file_suffix_context}
<｜fim end｜>{model_infill_prediction}
```

## Cross-File Context Prompting
For repository-level awareness, prepend relevant imported file signatures before `<｜fim begin｜>`:
```
# Path: src/utils/math.rs
pub fn compute_hash(data: &[u8]) -> u64;

<｜fim begin｜>
use crate::utils::math::compute_hash;

fn process(buf: &[u8]) {
    let hash = 
<｜fim hole｜>
    println!("Hash: {}", hash);
}
<｜fim end｜>
```
