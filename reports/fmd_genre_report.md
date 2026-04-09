# FMD Genre Comparison Report


Generated at: 2026-04-02T23:46:19


Experiment: XMIDI subset vs generated genre folders


## Overview


This report summarizes Frechet Music Distance comparisons between XMIDI reference genres and generated music genres.


## Configuration

| Field | Value |
| --- | --- |
| Reference root | `/Users/pkutyl/WIMU-2026L/data/XMIDI_subset` |
| Test root | `/Users/pkutyl/WIMU-2026L/data/topk15-t1.0-ngram0_midi` |
| Feature extractor | `clamp2` |
| Gaussian estimator | `mle` |
| FMD-Inf steps | `25` |
| FMD-Inf min_n | `2` |


## Summary

| Metric | Value |
| --- | --- |

| Total reference genres | `3` |


| Total generated genres | `3` |


| Total comparisons | `3` |


| Best pair | `religious -> religious` |
| Best pair FMD-Inf | `600.1720` |


| Worst pair | `pop -> pop` |
| Worst pair FMD-Inf | `813.9659` |





## Pairwise Results

| XMIDI genre | Generated genre | Reference samples | Test samples | FMD | FMD-Inf | R^2 | Slope |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |

| pop | pop | 3 | 3 | 761.2051 | 813.9659 | 0.0008 | -64.2180 |

| jazz | jazz | 3 | 3 | 798.5849 | 657.9225 | 0.1663 | 356.8452 |

| religious | religious | 3 | 3 | 651.1154 | 600.1720 | 0.0065 | 152.8302 |


## Detailed Comparisons


### pop vs pop

| Field | Value |
| --- | --- |
| Reference genre | `pop` |
| Generated genre | `pop` |
| Reference path | `/Users/pkutyl/WIMU-2026L/data/XMIDI_subset/pop` |
| Test path | `/Users/pkutyl/WIMU-2026L/data/topk15-t1.0-ngram0_midi/pop` |
| Reference samples | `3` |
| Test samples | `3` |
| FMD | `761.205126` |
| FMD-Inf score | `813.965950` |
| FMD-Inf R^2 | `0.000810` |
| FMD-Inf slope | `-64.218033` |




#### FMD-Inf Point Estimates

| Sample size | Point estimate |
| ---: | ---: |

| 2 | 839.547732 |

| 2 | 825.441020 |

| 2 | 839.547732 |

| 2 | 665.991076 |

| 2 | 637.878710 |

| 2 | 762.766285 |

| 2 | 839.547732 |

| 2 | 665.991076 |

| 2 | 825.441020 |

| 2 | 839.547732 |

| 2 | 839.547732 |

| 2 | 839.547732 |

| 2 | 825.441020 |

| 2 | 825.441020 |

| 2 | 665.991076 |

| 2 | 762.766285 |

| 2 | 822.195422 |

| 2 | 825.441020 |

| 2 | 825.441020 |

| 2 | 637.878710 |

| 2 | 839.547732 |

| 2 | 825.441020 |

| 2 | 822.195422 |

| 2 | 665.991076 |

| 3 | 792.559939 |






### jazz vs jazz

| Field | Value |
| --- | --- |
| Reference genre | `jazz` |
| Generated genre | `jazz` |
| Reference path | `/Users/pkutyl/WIMU-2026L/data/XMIDI_subset/jazz` |
| Test path | `/Users/pkutyl/WIMU-2026L/data/topk15-t1.0-ngram0_midi/jazz` |
| Reference samples | `3` |
| Test samples | `3` |
| FMD | `798.584901` |
| FMD-Inf score | `657.922455` |
| FMD-Inf R^2 | `0.166327` |
| FMD-Inf slope | `356.845239` |




#### FMD-Inf Point Estimates

| Sample size | Point estimate |
| ---: | ---: |

| 2 | 838.970438 |

| 2 | 862.422651 |

| 2 | 824.065486 |

| 2 | 824.065486 |

| 2 | 824.065486 |

| 2 | 838.970438 |

| 2 | 862.422651 |

| 2 | 784.336771 |

| 2 | 824.065486 |

| 2 | 862.422651 |

| 2 | 862.422651 |

| 2 | 824.065486 |

| 2 | 784.336771 |

| 2 | 824.065486 |

| 2 | 878.679742 |

| 2 | 838.970438 |

| 2 | 878.679742 |

| 2 | 838.970438 |

| 2 | 784.336771 |

| 2 | 862.422651 |

| 2 | 824.065486 |

| 2 | 824.065486 |

| 2 | 838.970438 |

| 2 | 862.422651 |

| 3 | 776.870868 |






### religious vs religious

| Field | Value |
| --- | --- |
| Reference genre | `religious` |
| Generated genre | `religious` |
| Reference path | `/Users/pkutyl/WIMU-2026L/data/XMIDI_subset/religious` |
| Test path | `/Users/pkutyl/WIMU-2026L/data/topk15-t1.0-ngram0_midi/religious` |
| Reference samples | `3` |
| Test samples | `3` |
| FMD | `651.115360` |
| FMD-Inf score | `600.171977` |
| FMD-Inf R^2 | `0.006488` |
| FMD-Inf slope | `152.830150` |




#### FMD-Inf Point Estimates

| Sample size | Point estimate |
| ---: | ---: |

| 2 | 611.842824 |

| 2 | 759.135600 |

| 2 | 661.970107 |

| 2 | 738.346060 |

| 2 | 759.135600 |

| 2 | 598.142629 |

| 2 | 738.346060 |

| 2 | 661.970107 |

| 2 | 598.142629 |

| 2 | 738.346060 |

| 2 | 738.346060 |

| 2 | 611.842824 |

| 2 | 611.842824 |

| 2 | 611.842824 |

| 2 | 759.135600 |

| 2 | 661.970107 |

| 2 | 661.970107 |

| 2 | 598.142629 |

| 2 | 713.691640 |

| 2 | 611.842824 |

| 2 | 611.842824 |

| 2 | 759.135600 |

| 2 | 759.135600 |

| 2 | 661.970107 |

| 3 | 651.115360 |











