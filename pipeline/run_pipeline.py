import os, json, cv2, argparse
import pandas as pd
from ultralytics import YOLO

from pipeline import config
from pipeline.geometry import *
from pipeline.image_fetcher import fetch_static_map
from pipeline.inference import run_inference


def main(input_xlsx, output_dir):
    df = pd.read_excel(input_xlsx)
    model = YOLO("models/best.pt")

    # ✅ Create subfolders explicitly
    pred_dir = os.path.join(output_dir, "predictions")
    art_dir = os.path.join(output_dir, "artefacts")
    img_dir = os.path.join(output_dir, "images")

    os.makedirs(pred_dir, exist_ok=True)
    os.makedirs(art_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    for _, row in df.iterrows():
        sid = row["sample_id"]
        lat, lon = row["latitude"], row["longitude"]

        # ---------- Fetch image ----------
        img_path = os.path.join(img_dir, f"{sid}.png")
        fetch_static_map(lat, lon, img_path, config)

        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        # ---------- Geometry ----------
        mpp = meters_per_pixel(lat, config.ZOOM)
        buffers = {
            "1200": circular_mask(h, w, area_to_radius_px(sqft_to_m2(1200), mpp)),
            "2400": circular_mask(h, w, area_to_radius_px(sqft_to_m2(2400), mpp))
        }

        # ---------- Inference ----------
        res = run_inference(model, img_path, buffers, mpp, config.CONF_THRESH)

        qc = "VERIFIABLE" if res["area"] > 0 else "NOT_VERIFIABLE"

        # ---------- Overlay ----------
        overlay = img.copy()
        if res["mask"] is not None:
            overlay[res["mask"] == 1] = (0, 255, 0)

        cx, cy = w // 2, h // 2
        cv2.circle(overlay, (cx, cy), int(area_to_radius_px(sqft_to_m2(1200), mpp)), (255, 0, 0), 2)
        cv2.circle(overlay, (cx, cy), int(area_to_radius_px(sqft_to_m2(2400), mpp)), (0, 0, 255), 2)

        overlay_path = os.path.join(art_dir, f"{sid}.png")
        cv2.imwrite(overlay_path, overlay)

        # ---------- JSON output ----------
        out = {
            "sample_id": int(sid),
            "lat": float(lat),
            "lon": float(lon),
            "has_solar": res["area"] > 0,
            "confidence": res["conf"],
            "pv_area_sqm_est": res["area"],
            "buffer_radius_sqft": 1200 if res["zone"] == "1200" else 2400,
            "qc_status": qc,
            "artefact_path": f"artefacts/{sid}.png"
        }

        json_path = os.path.join(pred_dir, f"{sid}.json")
        with open(json_path, "w") as f:
            json.dump(out, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.input, args.output)
