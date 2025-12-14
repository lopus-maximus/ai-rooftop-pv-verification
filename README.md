# AI-Based Rooftop Solar Verification Pipeline – Run Instructions

This repository contains an AI-based pipeline to remotely verify rooftop solar PV installations from satellite imagery using latitude and longitude inputs. The system performs detection, segmentation-based area estimation, and audit-friendly output generation.

---

## ⚠️ GPU Requirement (Recommended)

This pipeline is designed to run on a **GPU-enabled environment** for practical performance. CPU execution is supported but may be slow for batch inference. Recommended GPU: NVIDIA T4 / RTX / A100 class.

---

## 1. Requirements

- Python **3.10+** (tested on Google Colab)
- Ultralytics (YOLOv8)
- OpenCV
- NumPy, Pandas
- Google Maps **Static Maps API key**
- CUDA-enabled GPU (recommended)

Install dependencies:

```bash
pip install -r environment/requirements.txt
```

---

## 2. Google Maps API Key

The pipeline fetches satellite imagery using the **Google Static Maps API**. Set the API key as an environment variable.

**Linux / macOS**

```bash
export GOOGLE_MAPS_API_KEY=your_api_key_here
```

**Windows (PowerShell)**

```powershell
setx GOOGLE_MAPS_API_KEY your_api_key_here
```

The API key is **not included** in this repository. Evaluators should substitute their own key.

---

## 3. Input File Format

Input must be provided as an Excel (`.xlsx`) file with the following columns:

| sample_id | latitude | longitude |
| --------- | -------- | --------- |

Example location:

```
inputs/samples.xlsx
```

Each row represents one site to be verified.

---

## 4. Output Structure

All outputs are written to the directory provided via the `--output` argument. Default output structure:

```
outputs/
├── predictions/
│   └── <sample_id>.json
├── artefacts/
│   └── <sample_id>.png
├── images/
│   └── <sample_id>.png
```

- **predictions/** → machine-readable JSON results
- **artefacts/** → audit overlay images (segmentation mask + buffer zones)
- **images/** → raw satellite images fetched from Google Maps

Folders are created automatically if they do not exist.

---

## 5. Model Files

Place the trained YOLOv8 segmentation model in:

```
models/best.pt
```

The model should be compatible with Ultralytics YOLOv8 and trained for rooftop solar panel segmentation.

---

## 6. Run the Pipeline

From the **project root directory**, run:

```bash
python -m pipeline.run_pipeline \
  --input inputs/samples.xlsx \
  --output outputs
```

⚠️ Always pass the **parent output directory** (`outputs`), not subfolders.

---

## 7. Pipeline Behavior

For each input coordinate, the pipeline:

- Fetches a high-resolution satellite image
- Runs YOLOv8-based solar panel segmentation
- Applies circular buffer zones corresponding to:
  - **1200 sq. ft**
  - **2400 sq. ft**
- Estimates PV area (m²) using pixel-to-ground conversion
- Selects the buffer with the largest valid overlap
- Generates:
  - JSON prediction record
  - Audit-friendly overlay image

---

## 8. Output JSON Format

Each prediction file follows this structure:

```json
{
  "sample_id": 1,
  "lat": 10.156557,
  "lon": 76.382746,
  "has_solar": true,
  "confidence": 0.83,
  "pv_area_sqm_est": 204.54,
  "buffer_radius_sqft": 1200,
  "qc_status": "VERIFIABLE",
  "artefact_path": "artefacts/1.png"
}
```

---

## 9. Notes

- Zoom level: **20**
- Image size: **640×640** with `scale=2`
- Ground resolution is computed using standard Web Mercator formulas
- QC status values:
  - `VERIFIABLE`
  - `NOT_VERIFIABLE`

---

## 10. License

This project uses open-source libraries and publicly accessible imagery APIs. Please ensure compliance with Google Maps API usage terms and dataset licenses.