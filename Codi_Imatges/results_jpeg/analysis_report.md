# Anàlisi de compressió JPEG

## Resum executiu
- Imatges processades: 8 de 8 disponibles.
- Qualitats analitzades: [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
- Figura 1: `figure1_mse_vs_quality.png`
- Figura 2: `figure2_cr_vs_quality.png`

## (c) Possibles raons de diferències de MSE entre imatges
- En general, imatges amb més detall fi (textures/vores) i més variabilitat cromàtica pateixen més error JPEG a quality fixa.
- Imatges amb zones uniformes solen donar MSE menor perquè la quantització DCT introdueix menys artefactes visibles.
- Comparativa quantitativa a quality de referència q=50:

- `image1`: MSE@q50=60.841, entropia=7.444, LapVar=1394.522, var cromàtica=308.226.
- `image2`: MSE@q50=71.523, entropia=7.362, LapVar=2491.713, var cromàtica=121.718.
- `image3`: MSE@q50=74.216, entropia=7.622, LapVar=3841.675, var cromàtica=78.758.
- `image4`: MSE@q50=22.522, entropia=6.979, LapVar=538.519, var cromàtica=77.030.
- `image5`: MSE@q50=28.823, entropia=6.336, LapVar=978.790, var cromàtica=72.589.
- `image6`: MSE@q50=20.209, entropia=7.251, LapVar=408.605, var cromàtica=528.225.
- `image7`: MSE@q50=41.298, entropia=2.111, LapVar=8434.212, var cromàtica=0.000.
- `image8`: MSE@q50=65.490, entropia=3.416, LapVar=182.598, var cromàtica=4421.708.

## (d) Diferències d'error dins de cada imatge
- Per cada imatge es generen visuals per q=30, q=best i q=90 amb: original, JPEG, mapa d'error absolut i 3 crops amb error màxim.

### image1
- Qualitat recomanada (compromís CR/MSE): **q=90**
- q30 (q=30): MSE=87.180, CR=17.034, err_vores=9.329, err_suau=4.385. L'error es concentra sobretot en vores i textures fines. (visual: `image1_q30_q30.png`)
- qbest (q=90): MSE=15.225, CR=4.845, err_vores=2.658, err_suau=1.977. L'error es concentra sobretot en vores i textures fines. (visual: `image1_qbest_q90.png`)
- q90 (q=90): MSE=15.225, CR=4.845, err_vores=2.658, err_suau=1.977. L'error es concentra sobretot en vores i textures fines. (visual: `image1_q90_q90.png`)

### image2
- Qualitat recomanada (compromís CR/MSE): **q=90**
- q30 (q=30): MSE=109.631, CR=15.415, err_vores=10.843, err_suau=5.233. L'error es concentra sobretot en vores i textures fines. (visual: `image2_q30_q30.png`)
- qbest (q=90): MSE=15.000, CR=4.804, err_vores=2.644, err_suau=1.946. L'error es concentra sobretot en vores i textures fines. (visual: `image2_qbest_q90.png`)
- q90 (q=90): MSE=15.000, CR=4.804, err_vores=2.644, err_suau=1.946. L'error es concentra sobretot en vores i textures fines. (visual: `image2_q90_q90.png`)

### image3
- Qualitat recomanada (compromís CR/MSE): **q=80**
- q30 (q=30): MSE=114.720, CR=15.395, err_vores=10.754, err_suau=5.862. L'error es concentra sobretot en vores i textures fines. (visual: `image3_q30_q30.png`)
- qbest (q=80): MSE=31.610, CR=6.838, err_vores=4.521, err_suau=3.317. L'error es concentra sobretot en vores i textures fines. (visual: `image3_qbest_q80.png`)
- q90 (q=90): MSE=15.489, CR=4.763, err_vores=2.664, err_suau=2.253. L'error es concentra sobretot en vores i textures fines. (visual: `image3_q90_q90.png`)

### image4
- Qualitat recomanada (compromís CR/MSE): **q=10**
- q30 (q=30): MSE=34.085, CR=22.848, err_vores=6.155, err_suau=2.503. L'error es concentra sobretot en vores i textures fines. (visual: `image4_q30_q30.png`)
- qbest (q=10): MSE=87.527, CR=45.538, err_vores=9.284, err_suau=3.971. L'error es concentra sobretot en vores i textures fines. (visual: `image4_qbest_q10.png`)
- q90 (q=90): MSE=6.679, CR=6.061, err_vores=2.160, err_suau=1.264. L'error es concentra sobretot en vores i textures fines. (visual: `image4_q90_q90.png`)

### image5
- Qualitat recomanada (compromís CR/MSE): **q=10**
- q30 (q=30): MSE=41.408, CR=21.425, err_vores=7.433, err_suau=1.672. L'error es concentra sobretot en vores i textures fines. (visual: `image5_q30_q30.png`)
- qbest (q=10): MSE=96.794, CR=38.862, err_vores=10.811, err_suau=2.936. L'error es concentra sobretot en vores i textures fines. (visual: `image5_qbest_q10.png`)
- q90 (q=90): MSE=8.223, CR=6.264, err_vores=2.562, err_suau=0.856. L'error es concentra sobretot en vores i textures fines. (visual: `image5_q90_q90.png`)

### image6
- Qualitat recomanada (compromís CR/MSE): **q=10**
- q30 (q=30): MSE=29.839, CR=27.042, err_vores=4.615, err_suau=1.868. L'error es concentra sobretot en vores i textures fines. (visual: `image6_q30_q30.png`)
- qbest (q=10): MSE=84.283, CR=47.912, err_vores=7.015, err_suau=3.547. L'error es concentra sobretot en vores i textures fines. (visual: `image6_qbest_q10.png`)
- q90 (q=90): MSE=7.063, CR=7.211, err_vores=2.031, err_suau=0.954. L'error es concentra sobretot en vores i textures fines. (visual: `image6_q90_q90.png`)

### image7
- Qualitat recomanada (compromís CR/MSE): **q=40**
- q30 (q=30): MSE=71.755, CR=4.257, err_vores=10.137, err_suau=1.196. L'error es concentra sobretot en vores i textures fines. (visual: `image7_q30_q30.png`)
- qbest (q=40): MSE=53.189, CR=3.770, err_vores=8.649, err_suau=1.023. L'error es concentra sobretot en vores i textures fines. (visual: `image7_qbest_q40.png`)
- q90 (q=90): MSE=3.607, CR=1.763, err_vores=2.200, err_suau=0.327. L'error es concentra sobretot en vores i textures fines. (visual: `image7_q90_q90.png`)

### image8
- Qualitat recomanada (compromís CR/MSE): **q=20**
- q30 (q=30): MSE=85.403, CR=3.771, err_vores=1.547, err_suau=0.000. L'error es concentra sobretot en vores i textures fines. (visual: `image8_q30_q30.png`)
- qbest (q=20): MSE=107.358, CR=4.771, err_vores=2.511, err_suau=0.000. L'error es concentra sobretot en vores i textures fines. (visual: `image8_qbest_q20.png`)
- q90 (q=90): MSE=27.551, CR=1.293, err_vores=0.581, err_suau=0.000. L'error es concentra sobretot en vores i textures fines. (visual: `image8_q90_q90.png`)
