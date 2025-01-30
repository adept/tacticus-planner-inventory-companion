# tacticus-planner-inventory-companion
OCR Tacticus inventory screenshots and compare to Tacticus Planner backup

Usage:
```
python parser.py <TacticusPlannerBackup.json> <inventory_screenshot1> [<inventory_screenshot2> ...]
```

Will write out debug images with all the OCR results marked up on them, and then print out something like this:
```
Revered Talisman: 5 -> 4 (screenshot: screenshots/inventory1.png, rectangle: 1)
Unyielding Rivets: 7 -> 6 (screenshot: screenshots/inventory1.png, rectangle: 2)
Relic Hilt: 11 -> 8 (screenshot: screenshots/inventory1.png, rectangle: 3)
Adamantium Ore: 12 -> 4 (screenshot: screenshots/inventory1.png, rectangle: 4)
Plague Bell: 3 -> 8 (screenshot: screenshots/inventory1.png, rectangle: 5)
Warp Locus: 14 -> 12 (screenshot: screenshots/inventory1.png, rectangle: 6)
Blessed Cogitator: 14 -> 13 (screenshot: screenshots/inventory1.png, rectangle: 11)
Psychic Force Conduit: 5 -> 2 (screenshot: screenshots/inventory1.png, rectangle: 13)
Symbiotic Carapace: 0 -> 1 (screenshot: screenshots/inventory1.png, rectangle: 17)
Technocrafted Strength: 0 -> 1 (screenshot: screenshots/inventory1.png, rectangle: 20)
Codex Astartes Page: 3 -> 1 (screenshot: screenshots/inventory1.png, rectangle: 22)
Collar of Khorne: 0 -> 1 (screenshot: screenshots/inventory1.png, rectangle: 26)
```
