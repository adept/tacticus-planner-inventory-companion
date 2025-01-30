import cv2
import numpy as np
import os
import pytesseract
import sys

# Find all white-ish rectangles in the image (that enclose the upgrade icons)
def find_whiteish_rectangles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
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
def match_images(i, rect_image, upgrade_images):
    best_match = None
    best_match_score = float('inf')
    for name, upgrade_image in upgrade_images.items():
        resized = cv2.resize(upgrade_image, (rect_image.shape[1], rect_image.shape[0]))
        diff = cv2.absdiff(rect_image, resized)
        score = np.sum(diff)
        if score < best_match_score:
            #print(f"#{i+1}: MATCHED with {name} (score: {score})")
            best_match_score = score
            best_match = name

    return best_match

def main(inventory_screenshot):
    main_image = cv2.imread(inventory_screenshot)
    rectangles = find_whiteish_rectangles(main_image)
    
    print(f"Found {len(rectangles)} rectangles")

    print("Loading upgrade images from ./upgrades ...")
    upgrade_images = {}
    for filename in os.listdir('upgrades'):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            upgrade_images[filename] = cv2.imread(os.path.join('upgrades', filename))
    
    matched_images = []
    for i, (x, y, w, h) in enumerate(rectangles):
        rect_image = main_image[y:y+h, x:x+w]
        match = match_images(i, rect_image, upgrade_images)
        # Mark the rectangle on the screenshot and tag it with number
        cv2.rectangle(main_image, (x, y), (x+w, y+h), (0, 0, 255), 5)
        cv2.putText(main_image, str(i+1), (x+20, y+50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

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
        cv2.rectangle(main_image, (x+offset, y+h), (x+w-2*offset, y+h+qty_height), (0, 255, 255), 2)
        if quantity:
            cv2.putText(main_image, str(quantity), (x+20, y+h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        print(f"Quantity for rectangle #{i+1}: {quantity}")
        matched_images.append((match,quantity))

    cv2.imwrite('output.png', main_image)
    
    with open('matched_images.txt', 'w') as f:
        for i, (match,quantity) in enumerate(matched_images):
            f.write(f"{i+1}: {quantity} of {match}\n")

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Usage: python parser.py <inventory_screenshot>")
        sys.exit(1)
    main(sys.argv[1])
