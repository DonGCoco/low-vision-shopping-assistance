# Thesis-reported experimental results

Source: `graduation-thesis.pdf`, printed pages 19 and 31–33, Tables 2–4. The following tables summarize the thesis evaluation.

## Image restoration

| Condition | SSIM ↑ | PSNR, dB ↑ | FID ↓ |
|---|---:|---:|---:|
| Blurred | 0.45 | 18.2 | 75.3 |
| DeblurGAN | 0.87 | 26.5 | 38.7 |
| VAE | 0.75 | 23.8 | 50.2 |
| CNN | 0.70 | 22.5 | 55.4 |
| Clear image compared with itself | 1.00 | infinity | 0.0 |



## Downstream description quality

| Input | BLEU | ROUGE-1 | ROUGE-2 | ROUGE-L |
|---|---:|---:|---:|---:|
| Blurred image | 0.75 | 0.85 | 0.72 | 0.83 |
| DeblurGAN-restored image | 0.90 | 0.95 | 0.88 | 0.94 |

The all-1.00 benchmark in Table 4 is explicitly labeled a theoretical maximum using reference text. It must not be presented as an experimentally measured clear-image model score. Reference-text preparation is described as manual product annotations recorded in Excel, then JSON.

## Evaluation scope

The thesis describes approximately 25,000 images with an 80/10/10 split. BLEU and ROUGE assess overlap with reference descriptions; they are not direct measures of factual accuracy or user experience. The research evaluates image restoration and generated text under controlled conditions. Real-world user evaluation is a future research direction.
