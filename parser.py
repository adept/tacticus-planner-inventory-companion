#!/usr/bin/env python3
import cv2
import numpy as np
import os
import pytesseract
from os.path import dirname, basename
import sys
import json

output_dir="output"

# Find all white-ish rectangles in the image (that enclose the upgrade icons)
def find_whiteish_rectangles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite("output/gray.png", gray)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    # cv2.imwrite("output/thresh.png", thresh)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    rectangles = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        x, y, w, h = cv2.boundingRect(approx)
        if 150 <= w <= 300 and 150 <= h <= 300:
            #print(f"FOUND rectangle-ish at ({x},{y}) (w:{w}, h:{h})")
            rectangles.append((x, y, w, h))
        else:
            #print(f"Discarding rectangle-ish at ({x},{y}) (w:{w}, h:{h})")
            #cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 255), 15)
            pass

    return rectangles

# Match the image of the upgrade icon in the i-th rectangle to the known upgrade icons
def match_images(i, rect_image, upgrades):
    best_match = None
    best_match_score = float('inf')
    for name in upgrades:
        upgrade_image = upgrades[name]['image']
        resized = cv2.resize(upgrade_image, (rect_image.shape[1], rect_image.shape[0]))
        diff = cv2.absdiff(rect_image, resized)
        score = np.sum(diff)
        if score < best_match_score:
            #print(f"#{i+1}: MATCHED with {name} (score: {score})")
            best_match_score = score
            best_match = name

    return best_match

def process_screenshot(screenshot_number, inventory_screenshot, upgrades, planner_inventory, screenshots_inventory):
    print(f"Processing {inventory_screenshot} ...")
    main_image = cv2.imread(inventory_screenshot)
    rectangles = find_whiteish_rectangles(main_image)
    print(f"Found {len(rectangles)} rectangles (best screenshot will have 5*7 = 35 rectangles)")
    
    matched_images = []

    # Mark the original file name on output image
    cv2.putText(main_image, f"file: {inventory_screenshot} (image #{screenshot_number+1})", (40, 40), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=2)

    for i, (x, y, w, h) in enumerate(rectangles):
        rect_image = main_image[y:y+h, x:x+w]
        match = match_images(i, rect_image, upgrades)

        # OCR the quantity of the upgrade, it is immediately below the icon
        # and about 60 pixes tall  
        qty_height = 60
        offset = 10
        qty_rect = main_image[y+h:y+h+qty_height, x+offset:x+w-2*offset]
        gray_qty_rect = cv2.cvtColor(qty_rect, cv2.COLOR_BGR2GRAY)
        _, thresh_qty_rect = cv2.threshold(gray_qty_rect, 0, 255, cv2.THRESH_OTSU)
        # Qty is white on black, but tesseract likes black on white more, so let's invert it 
        thresh_qty_rect = 255 - thresh_qty_rect
        quantity = pytesseract.image_to_string(thresh_qty_rect, config='--psm 6 digits')
        #print(f"OCR'ed quantity for rectangle #{i+1}: {quantity}")
        quantity = int(quantity.strip()) if quantity.strip().isdigit() else None
        if quantity:
            print(f"Quantity for rectangle #{i+1}: {quantity}")
            upgrade = upgrades[match]['name']
            screenshots_inventory[upgrade] = {}
            screenshots_inventory[upgrade]['quantity'] = quantity
            screenshots_inventory[upgrade]['screenshot'] = inventory_screenshot
            screenshots_inventory[upgrade]['rectangle'] = i+1

            existing_quantity = planner_inventory[upgrade] if upgrade in planner_inventory else 0
            if existing_quantity != quantity:
                # Mark the rectangle on the screenshot red, tag it with number, upgrade name, and quantity chage
                color=(0, 0, 255) # Red
                quantity_str=f"{existing_quantity}->{quantity}"
            else:
                # Quantities match.
                color=(0, 255, 0) # Green
                quantity_str=str(quantity)
            # Save the rectangle from the screenshot for debugging
            rect_image_path = os.path.join(output_dir, f"rect_{screenshot_number+1}_{i+1}.png")
            cv2.imwrite(rect_image_path, rect_image)
            # Mark upgrade rectange
            cv2.rectangle(main_image, (x, y), (x+w, y+h), color, 5)
            # Mark the rectangle number
            cv2.putText(main_image, str(i+1), (x+20, y+50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            # Mark the quantity rectangle
            cv2.rectangle(main_image, (x, y+h), (x+w, y+h+qty_height), color, 2)
            # Mark the quantity
            cv2.putText(main_image, quantity_str, (x+10, y+h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            # Mark the upgrade name
            for word_number, word in enumerate(upgrade.split()):
                cv2.putText(main_image, word, (x+10, y+70+word_number*20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    output_image_path = os.path.join(output_dir, f'output_{screenshot_number+1}.png')
    print(f"Saving output screenshot to {output_image_path}")
    cv2.imwrite(output_image_path, main_image)

# Load all the materials/upgrades known to TacticusPlanner from its recipeData.json
def load_upgrades_from_recipeData():
    print("Loading upgrade info from recipeData.json ...")
    if not os.path.exists('recipeData.json'):
        print("recipeData.json not found, copy it from the Tacticus Planner source code")
        sys.exit(1)

    with open('recipeData.json', 'r') as f:
        recipe_data = json.load(f)
    upgrades = {}
    for material in recipe_data.values():
        if 'icon' not in material or material['stat'] == 'Shard':
            # This is a shard then
            continue
        upgrades[material['icon']] = {} 
        upgrades[material['icon']]['name'] = material['material']

    print(f"Loaded {len(upgrades)} upgrades")
    return upgrades

# Take all the upgrades known to TacticusPlanner, and load their icons
def load_icons(upgrades):
    print("Loading upgrade icons from ./upgrades ...")
    failed = False
    for icon in upgrades:
        icon_path = os.path.join('upgrades', icon)
        if not os.path.exists(icon_path):
            print(f"Icon {icon} not found in ./upgrades")
            failed=True
        upgrades[icon]['image'] = cv2.imread(icon_path)
    print(f"Loaded {len(upgrades)} icons")
    if failed:
        print("Some icons were not found, copy them from the Tacticus Planner source code, exiting")
        sys.exit(1)

# Load current inventory counts from TacticusPlanner backup file
def load_inventory(backup_json):
    print(f"Loading inventory from {backup_json} ...")
    with open(backup_json, 'r') as f:
        backup = json.load(f)
    inventory = backup['inventory']['upgrades']
    print(f"Loaded inventory of {len(inventory)} upgrades")
    return inventory

def main(backup_json, inventory_screenshots):
    upgrades = load_upgrades_from_recipeData()
    load_icons(upgrades)
    planner_inventory = load_inventory(backup_json)
    screenshots_inventory = {}
    print(f"Processing {len(inventory_screenshots)} screenshots")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for screenshot_number, screenshot in enumerate(inventory_screenshots):
        process_screenshot(screenshot_number, screenshot, upgrades, planner_inventory, screenshots_inventory)
    print(f"Comparing inventories ... ")
    for upgrade in screenshots_inventory:
        ocred = screenshots_inventory[upgrade]
        new_quantity = ocred['quantity']        
        existing_quantity = planner_inventory[upgrade] if upgrade in planner_inventory else 0
        if existing_quantity != new_quantity:
            print(f"{upgrade}: {existing_quantity} -> {new_quantity} (screenshot: {ocred['screenshot']}, rectangle: {ocred['rectangle']})")

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("Usage: python parser.py <TacticusPlannerBackup.json> <inventory_screenshot1> [<inventory_screenshot2> ...]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2:])
