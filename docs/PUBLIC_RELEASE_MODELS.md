# Public-Release Model Registry

Model weights are local benchmark inputs and are never committed or published
by this repository. Download each file from its immutable revision, then verify
both its exact byte count and SHA-256 before use.

| Workload | Repository and immutable revision | Filename | Bytes | SHA-256 | Terms recorded by source |
| --- | --- | --- | ---: | --- | --- |
| Llama 2 scoreboard | `TheBloke/Llama-2-7B-GGUF@7ab6ce6af81baefac28ea4ecab22d0205a90ea2f` | `llama-2-7b.Q4_0.gguf` | 3,825,807,040 | `78b8f9777dd620ad29cd2cffb6653b17fa8a5b1fddc1b8821180d60eedd24d48` | Preserve the upstream Llama 2 model terms; the quant repository API does not declare a license |

Immutable download URLs:

- `https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/7ab6ce6af81baefac28ea4ecab22d0205a90ea2f/llama-2-7b.Q4_0.gguf`

Recheck the local registry with:

```bash
sha256sum models/llama-2-7b.Q4_0.gguf
```

The source repository is public and ungated at the recorded revision. Its
metadata does not choose a license for this project. This project's own code
and documentation use the MIT License in `LICENSE`; upstream source notices
and the model's separate terms remain controlling for that material.
