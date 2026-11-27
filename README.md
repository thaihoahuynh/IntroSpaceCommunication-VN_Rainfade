# IntroSpaceCommunication-VN_Rainfade
# Rain Attenuation and Link Availability across Vietnam

PH035IU Introduction to Space Communications - Group Project 2 (Fall 2026)

**Question:** How much rain-fade margin do earth stations across Vietnam need to reach
99.5 %, 99.9 % and 99.99 % availability towards a satellite at 132°E, at C, Ku and
(hypothetical) Ka band?

- Scenario 1 (real): VINASAT-1 at 132°E, C and Ku band.
- Scenario 2 (hypothetical): a Ka-band payload co-located at 132°E.

## How to reproduce

```
pip install -r requirements.txt
python scripts/fetch_data.py      # downloads every source file into data/raw/
```

Large files (the ITU-R P.837-8 map ZIP, ~360 MB) are not stored in this repository.
`fetch_data.py` downloads them again; `data/provenance.csv` records the URL, UTC download
time and SHA-256 checksum of every file so the copy can be verified.

## Repository layout

| Path | Content |
|---|---|
| `data/sources.csv` | List of files to download (name, URL, note) |
| `data/provenance.csv` | Written by the script: URL, date, SHA-256, size, who downloaded |
| `data/raw/` | Downloaded files - never edited by hand |
| `data/sites.csv` | Earth-station sites: latitude, longitude, altitude and its source |
| `data/nso_rainfall_annual.csv` | Annual rainfall 2019-2025, NSO Statistical Yearbook 2025, Tables 4 & 6 |
| `data/nso_rainfall_monthly_2025.csv` | Monthly rainfall 2025, NSO Statistical Yearbook 2025, Table 5 |
| `scripts/fetch_data.py` | Download + provenance script |

## Team

| Member | 
|---|
| Huynh Thai Hoa | 
| Tran Ngoc Hai Trieu | 
| Le Thao My |

All data sources are listed in `data/provenance.csv`.
