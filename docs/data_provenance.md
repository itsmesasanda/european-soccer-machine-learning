# Data Provenance and Fingerprint

## Source

The project uses Hugo Mathien's [European Soccer Database on Kaggle](https://www.kaggle.com/datasets/hugomathien/soccer), covering matches, leagues, teams, players and dated FIFA-derived attributes from European football.

The local project source is stored as `data/raw/european_soccer_database.xlsx`. Large data files are intentionally ignored by Git and must be obtained separately for reproduction.

## SHA-256 fingerprints

```text
9288748def6d4dab386c3d9dc74f79485ccfde5fa4a2a70a5ed010ebe78695db  data/raw/european_soccer_database.xlsx
d20367f0f9d424651df6f6b506f06e721d670b5cc60e8de8b9a0db665d705ab0  data/extracted/Country.csv
42c431e9a1aa5d00ce4f6b23f0ed7986fa51660584ea97f9d47cbe2e5010828f  data/extracted/League.csv
6331fe8bfe4b3327721f06a35a315b12ffd130fb3764a516678ad1481bccd3d2  data/extracted/Match.csv
05c1e81e76e2d51ac8405dbab0d2ab775b5bb63868cfe8f879487f8ffed5a52a  data/extracted/Player.csv
941b2c7e919673ec2d5d80918761f19d86bfbe27d030fbf41e9821130c823cab  data/extracted/Player_Attributes.csv
64b2c2e383b2fa59df74830a36fb00a29f3d8c794a0d716d4a691419fcf9a32b  data/extracted/Team.csv
86d8ff51e7ef8bdefd3da15f8e5c811afd6091afb9d6c793ae7fae92bf170e7a  data/extracted/Team_Attributes.csv
d110e0e8296455f0f4c292860f7d1e84e4f95cdf58ddeac15f97a0462357726f  data/extracted/sqlite_sequence.csv
```

## Recreate extracted tables

Place the fingerprinted workbook at the documented path and run:

```bash
python src/excel_to_csv.py
```

The script exports each workbook sheet to `data/extracted/<sheet>.csv`.
