# Wolfsberg CBDDQ Importer

A command-line and programmatic tool for converting **Wolfsberg CBDDQ v1.4** questionnaire responses to and from the **OpenKYCAML v1.8.0** envelope format.

## Usage

```bash
# Convert CBDDQ JSON → OpenKYCAML envelope
python wolfsberg_importer.py import --input cbddq-response.json --output openkycaml-profile.json

# Export OpenKYCAML envelope → CBDDQ JSON
python wolfsberg_importer.py export --input openkycaml-profile.json --output cbddq-export.json

# Produce gap report (fields in CBDDQ not covered by OpenKYCAML)
python wolfsberg_importer.py gap-report --input cbddq-response.json
```

## Field Mapping

See `../docs/mappings/wolfsberg-fccq-cbddq.md` and `wolfsberg-fccq-cbddq.yaml` for the complete field mapping table.

## Installation

```bash
pip install -r requirements.txt
```
