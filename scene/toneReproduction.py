import numpy as np

# Small constant to avoid log(0)
_DELTA = 1e-4

def _compute_log_avg_lum(lum):
    return np.exp(np.mean(np.log(_DELTA + lum)))

def aces_filmic(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x*(a*x + b)) / (x*(c*x + d) + e), 0.0, 1.0)

def tone_reproduce(hdr,
                   manual_exposure=1.0,
                   auto_key=True,
                   key_value=0.18,
                   white_pct=98.0,
                   contrast=1.1,
                   saturation=1.2,
                   gamma=2.2):
    """
    hdr:             H×W×3 HDR radiance
    manual_exposure: user multiplier (try 0.3–0.7)
    auto_key:        if True, override manual_exposure using log-average
    key_value:       target mid-gray (0.18)
    white_pct:       percentile for white clamp (90–99)
    contrast:        1.0–1.3
    saturation:      1.0–1.4
    gamma:           usually 2.2
    """
    # 1) compute luminance
    lum = 0.27*hdr[...,0] + 0.67*hdr[...,1] + 0.06*hdr[...,2]

    # 2) auto-exposure key
    if auto_key:
        Lwa = _compute_log_avg_lum(lum)
        exposure = key_value / Lwa
    else:
        exposure = manual_exposure

    img = hdr * exposure

    # 3) ACES curve
    ldr = aces_filmic(img)

    # 4) per-channel white normalization
    w = np.percentile(ldr, white_pct, axis=(0,1))
    ldr = np.clip(ldr / np.maximum(w, 1e-6), 0.0, 1.0)

    # 5) contrast
    ldr = np.clip((ldr - 0.5)*contrast + 0.5, 0.0, 1.0)

    # 6) saturation
    lum2 = 0.27*ldr[...,0] + 0.67*ldr[...,1] + 0.06*ldr[...,2]
    ldr = np.clip(lum2[...,None] + (ldr - lum2[...,None])*saturation, 0.0, 1.0)

    # 7) gamma
    return np.power(ldr, 1.0/gamma)
