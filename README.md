# tacticus-planner-inventory-companion

OCR Tacticus inventory screenshots and compare to [Tacticus Planner](https://tacticusplanner.app/) backup.

Uses upgrade images and upgrade names from Tacticus Planner codebase (mostly).

Screenshots would be marked up with green rectangles where quantity matches Tacticus Planner and red rectangles where it does not:


# Installation

Clone the repository, do `poetry install` (if you are using poetry) or:

- Clone the repository
- Create python venv `virtualenv .venv --python=python3`
- do `pip install -r requirements.txt`

# Usage

Do `Export` in Tacticus Planner. Take screenshots of your Tacticus inventory, and put them somewhere - let's say in `./screenshots`

Then pass both export json and screenshots to `parser.py`: `./parser.py export.json ./screenshots/*.png`

It will create `./output` with lots of PNG files. Check `./output/output_*.png` - they would be your screenshots with all the
recognized upgrades clearly marked and all mismatching quantities highlighted. You can now update your Tacticus Planner inventory based on this.

# Limitations

Some of the upgrade icon images in `./upgrades` are of low quality (75x75 px), which leads to false positives and false negatives in recognition.

Sourcing better upgrade images will help to improve quality - maybe to a point where this tool would be reliable enough to allow it to write out
the updated JSON file that could be imported back into Tacticus Planner.

There are some places in code where I have too many magic numbers for my liking (like "quantity is in the aread about 60 pixels tall below the upgrade image").

# Reporting issues

When reporting issues, include/make available original inventory screenshot and marked up result from the output directory (`./output/output_N.png`).
