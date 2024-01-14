# LLMSat
Implementation of the proposd spacecraft controller in LLMSat: An Large Lanuge Model-Based Goal-Oriented Autonomous Agent for Space Exploration (WIP).

As spacecraft journey further from Earth with more complex missions, systems of greater autonomy and onboard intelligence are called for. Reducing reliance on human-based mission control becomes increasingly critical if we are to increase our rate of solar-system-wide exploration. This work explores the application of LLMs as the high-level control system of a spacecraft. Using a simulated space mission as a case study, the proposed architecture's efficacy is evaluated based on key performance indicators. The popular game engine Kerbal Space Program is leveraged as the simulation environment. This research evaluates the potential of LLMs in augmenting autonomous decision-making systems for future safety-critical space applications.

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


## KSP Setup
1. Start with a fresh install
1. Install Realism Overhaul and its dependencies through CKAN
1. Install:
    KRPC
    KRPC-Mechjeb
    Parallax (for nice planet textures)

# Test
To run tests:
```
pytest -v -s
```