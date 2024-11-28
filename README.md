# uralicBPE

Specialized monolingual BPE tokenizers for Uralic languages representation in Large Language Models.

## Overview

This repository contains monolingual BPE tokenizers trained on Wikipedia data for four Uralic languages:
- Estonian
- Finnish
- Hungarian 
- Northern Sami

Each tokenizer is trained with a vocabulary size of 256,000 tokens (except Northern Sami: 93,187 tokens due to limited data).

## Features

- Clean monolingual datasets extracted from Wikipedia
- Specialized BPE tokenizers for each language
- Combined Uralic tokenizer
- Token ranking analysis tools
- Significantly improved compression ratios compared to general-purpose tokenizers

## Repository Structure

```
uralicBPE/
├── notebooks/          # Jupyter notebooks with analysis
├── src/                # Tokenizer training scripts
├── tokenizers/         # Trained tokenizer models
└── README.md
```

## Performance Comparison

Compression ratios comparison with popular tokenizers:

| Language | Our BPE | LLaMA-2 | Gemma-2 |
|----------|---------|----------|----------|
| Estonian | 1.13 | 3.09 | 2.45 |
| Finnish | 1.18 | 3.41 | 2.49 |
| Hungarian | 1.11 | 2.69 | 2.18 |
| Northern Sami | 1.32 | 3.53 | 3.04 |

## Installation & Usage

1. Clone the repository:
```bash
git clone https://github.com/nup-csai/uralicBPE.git
cd uralicBPE
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Access the tokenizers:
```python
from tokenizers import Tokenizer
tokenizer = Tokenizer.from_file("tokenizers/et.wiki_paragraphs.2024-05.json")
```

## Data Availability

The processed Wikipedia datasets and pre-trained tokenizers are available on Hugging Face:
https://huggingface.co/datasets/nup-csai/uralicBPE

## Citation

If you use these tokenizers in your research, please cite:

```bibtex
@article{chelombitko2024specialized,
  title={Specialized Monolingual BPE Tokenizers for Uralic Languages Representation in Large Language Models},
  author={Chelombitko, Iaroslav and Komissarov, Aleksey},
  year={2024}
}
```

## Contributing

We welcome contributions! We're particularly interested in:
- Additional Uralic language datasets
- Tokenizer performance improvements
- Integration with language models
- Documentation improvements

Please feel free to open issues or submit pull requests.

## License

MIT License

## Contact

- Iaroslav Chelombitko - i.chelombitko@nup.ac.cy
- Aleksey Komissarov - ad3002@gmail.com

## Acknowledgments

We thank the Wikimedia Foundation for providing Wikipedia data and the open-source community for tokenizer tools and libraries.