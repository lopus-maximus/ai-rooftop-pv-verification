import cv2
import numpy as np

def run_inference(model, img_path, buffers, mpp, conf_thresh):
    pred = model(img_path, conf=conf_thresh, verbose=False)[0]
    h, w = buffers["1200"].shape

    best = {"area": 0, "mask": None, "conf": 0, "zone": None}

    if pred.masks is None:
        return best

    masks = pred.masks.data.cpu().numpy()
    confs = pred.boxes.conf.cpu().numpy()

    for i, m in enumerate(masks):
        m = (m > 0.5).astype(np.uint8)
        m = cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST)

        a1200 = (m * buffers["1200"]).sum() * (mpp ** 2)
        a2400 = (m * buffers["2400"]).sum() * (mpp ** 2)

        zone = "1200" if a1200 > 0 else "2400" if a2400 > 0 else None
        area = a1200 + a2400

        if area > best["area"]:
            best.update({
                "area": float(area),
                "mask": m,
                "conf": float(confs[i]),
                "zone": zone
            })

    return best
