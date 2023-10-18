# LLMSat
An LLM-Based Goal-Oriented Autonomous Agent for Space Exploration

# Setup
1. Clone the repository
1. Install KSP with mods as per [RO & RP 1 Express Installation](https://github.com/KSP-RO/RP-1/wiki/RO-&-RP-1-Express-Installation-for-1.12.3)
    1. When selecting the compatible game versions in CKAN, select all from 1.8-1.12 as per [source](https://www.reddit.com/r/RealSolarSystem/comments/welsw2/comment/k5bnp2w/?utm_source=share&utm_medium=web2x&context=3)
1. Install Poetry as per [Poetry Instructions](https://python-poetry.org/docs/)
1. Install Python dependencies using:
```
Poetry install
```
1. Copy `.env.example` to new file `.env` and populate keys
1. Run tests to verify setup

# Test
To run tests:
```
pytest -v -s
```