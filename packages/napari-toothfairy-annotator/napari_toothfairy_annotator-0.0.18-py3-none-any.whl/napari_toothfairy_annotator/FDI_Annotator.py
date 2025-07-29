import numpy as np

class FDI_Annotator:
    def __init__(self,):
        self.inverse = {
            "Background": {"quadrant":0, "ID": "00", "type": "Background", "name": "Background"},
            "Lower Jawbone": {"quadrant": 0, "ID": "01", "type": "Lower Jawbone", "name": "Lower Jawbone"},
            "Upper Jawbone": {"quadrant": 0, "ID": "02", "type": "Upper Jawbone", "name": "Upper Jawbone"},
            "Left Inferior Alveolar Canal": {"quadrant": 0, "ID": "03", "type": "Left Inferior Alveolar Canal", "name": "Left Inferior Alveolar Canal"},
            "Right Inferior Alveolar Canal": {"quadrant": 0, "ID": "04", "type": "Right Inferior Alveolar Canal", "name": "Right Inferior Alveolar Canal"},
            "Left Maxillary Sinus": {"quadrant": 0, "ID": "05", "type": "Left Maxillary Sinus", "name": "Left Maxillary Sinus"},
            "Right Maxillary Sinus": {"quadrant": 0, "ID": "06", "type": "Right Maxillary Sinus", "name": "Right Maxillary Sinus"},
            "Pharynx": {"quadrant": 0, "ID": "07", "type": "Pharynx", "name": "Pharynx"},
            "Bridge": {"quadrant": 0, "ID": "08", "type": "Bridge", "name": "Bridge"},
            "Crown": {"quadrant": 0, "ID": "09", "type": "Crown", "name": "Crown"},
            "Implant": {"quadrant": 0, "ID": "10", "type": "Implant", "name": "Implant"},
            "Upper Right Central Incisor": {"quadrant": 1, "ID": "11", "type": "Incisor", "name": "Upper Right Central Incisor"},
            "Upper Right Lateral Incisor": {"quadrant": 1, "ID": "12", "type": "Incisor", "name": "Upper Right Lateral Incisor"},
            "Upper Right Canine": {"quadrant": 1, "ID": "13", "type": "Canine", "name": "Upper Right Canine"},
            "Upper Right First Premolar": {"quadrant": 1, "ID": "14", "type": "Premolar", "name": "Upper Right First Premolar"},
            "Upper Right Second Premolar": {"quadrant": 1, "ID": "15", "type": "Premolar", "name": "Upper Right Second Premolar"},
            "Upper Right First Molar": {"quadrant": 1, "ID": "16", "type": "Molar", "name": "Upper Right First Molar"},
            "Upper Right Second Molar": {"quadrant": 1, "ID": "17", "type": "Molar", "name": "Upper Right Second Molar"},
            "Upper Right Third Molar (Wisdom Tooth)": {"quadrant": 1, "ID": "18", "type": "Molar", "name": "Upper Right Third Molar (Wisdom Tooth)"},
            "Upper Left Central Incisor": {"quadrant": 2, "ID": "21", "type": "Incisor", "name": "Upper Left Central Incisor"},
            "Upper Left Lateral Incisor": {"quadrant": 2, "ID": "22", "type": "Incisor", "name": "Upper Left Lateral Incisor"},
            "Upper Left Canine": {"quadrant": 2, "ID": "23", "type": "Canine", "name": "Upper Left Canine"},
            "Upper Left First Premolar": {"quadrant": 2, "ID": "24", "type": "Premolar", "name": "Upper Left First Premolar"},
            "Upper Left Second Premolar": {"quadrant": 2, "ID": "25", "type": "Premolar", "name": "Upper Left Second Premolar"},
            "Upper Left First Molar": {"quadrant": 2, "ID": "26", "type": "Molar", "name": "Upper Left First Molar"},
            "Upper Left Second Molar": {"quadrant": 2, "ID": "27", "type": "Molar", "name": "Upper Left Second Molar"},
            "Upper Left Third Molar (Wisdom Tooth)": {"quadrant": 2, "ID": "28", "type": "Molar", "name": "Upper Left Third Molar (Wisdom Tooth)"},
            "Lower Left Central Incisor": {"quadrant": 3, "ID": "31", "type": "Incisor", "name": "Lower Left Central Incisor"},
            "Lower Left Lateral Incisor": {"quadrant": 3, "ID": "32", "type": "Incisor", "name": "Lower Left Lateral Incisor"},
            "Lower Left Canine": {"quadrant": 3, "ID": "33", "type": "Canine", "name": "Lower Left Canine"},
            "Lower Left First Premolar": {"quadrant": 3, "ID": "34", "type": "Premolar", "name": "Lower Left First Premolar"},
            "Lower Left Second Premolar": {"quadrant": 3, "ID": "35", "type": "Premolar", "name": "Lower Left Second Premolar"},
            "Lower Left First Molar": {"quadrant": 3, "ID": "36", "type": "Molar", "name": "Lower Left First Molar"},
            "Lower Left Second Molar": {"quadrant": 3, "ID": "37", "type": "Molar", "name": "Lower Left Second Molar"},
            "Lower Left Third Molar (Wisdom Tooth)": {"quadrant": 3, "ID": "38", "type": "Molar", "name": "Lower Left Third Molar (Wisdom Tooth)"},
            "Lower Right Central Incisor": {"quadrant": 4, "ID": "41", "type": "Incisor", "name": "Lower Right Central Incisor"},
            "Lower Right Lateral Incisor": {"quadrant": 4, "ID": "42", "type": "Incisor", "name": "Lower Right Lateral Incisor"},
            "Lower Right Canine": {"quadrant": 4, "ID": "43", "type": "Canine", "name": "Lower Right Canine"},
            "Lower Right First Premolar": {"quadrant": 4, "ID": "44", "type": "Premolar", "name": "Lower Right First Premolar"},
            "Lower Right Second Premolar": {"quadrant": 4, "ID": "45", "type": "Premolar", "name": "Lower Right Second Premolar"},
            "Lower Right First Molar": {"quadrant": 4, "ID": "46", "type": "Molar", "name": "Lower Right First Molar"},
            "Lower Right Second Molar": {"quadrant": 4, "ID": "47", "type": "Molar", "name": "Lower Right Second Molar"},
            "Lower Right Third Molar (Wisdom Tooth)": {"quadrant": 4, "ID": "48", "type": "Molar", "name": "Lower Right Third Molar (Wisdom Tooth)"}
        }


        self.fdi_notation = {
            "00": {"quadrant":0, "ID": "00", "type": "Background", "name": "Background"},
            "01": {"quadrant": 0, "ID": "01", "type": "Lower Jawbone", "name": "Lower Jawbone"},
            "02": {"quadrant": 0, "ID": "02", "type": "Upper Jawbone", "name": "Upper Jawbone"},
            "03": {"quadrant": 0, "ID": "03", "type": "Left Inferior Alveolar Canal", "name": "Left Inferior Alveolar Canal"},
            "04": {"quadrant": 0, "ID": "04", "type": "Right Inferior Alveolar Canal", "name": "Right Inferior Alveolar Canal"},
            "05": {"quadrant": 0, "ID": "05", "type": "Left Maxillary Sinus", "name": "Left Maxillary Sinus"},
            "06": {"quadrant": 0, "ID": "06", "type": "Right Maxillary Sinus", "name": "Right Maxillary Sinus"},
            "07": {"quadrant": 0, "ID": "07", "type": "Pharynx", "name": "Pharynx"},
            "08": {"quadrant": 0, "ID": "08", "type": "Bridge", "name": "Bridge"},
            "09": {"quadrant": 0, "ID": "09", "type": "Crown", "name": "Crown"},
            "10": {"quadrant": 0, "ID": "10", "type": "Implant", "name": "Implant"},
            "11": {"quadrant": 1, "ID": "11", "type": "Incisor", "name": "Upper Right Central Incisor"},
            "12": {"quadrant": 1, "ID": "12", "type": "Incisor", "name": "Upper Right Lateral Incisor"},
            "13": {"quadrant": 1, "ID": "13", "type": "Canine", "name": "Upper Right Canine"},
            "14": {"quadrant": 1, "ID": "14", "type": "Premolar", "name": "Upper Right First Premolar"},
            "15": {"quadrant": 1, "ID": "15", "type": "Premolar", "name": "Upper Right Second Premolar"},
            "16": {"quadrant": 1, "ID": "16", "type": "Molar", "name": "Upper Right First Molar"},
            "17": {"quadrant": 1, "ID": "17", "type": "Molar", "name": "Upper Right Second Molar"},
            "18": {"quadrant": 1, "ID": "18", "type": "Molar", "name": "Upper Right Third Molar (Wisdom Tooth)"},

            "21": {"quadrant": 2, "ID": "21", "type": "Incisor", "name": "Upper Left Central Incisor"},
            "22": {"quadrant": 2, "ID": "22", "type": "Incisor", "name": "Upper Left Lateral Incisor"},
            "23": {"quadrant": 2, "ID": "23", "type": "Canine", "name": "Upper Left Canine"},
            "24": {"quadrant": 2, "ID": "24", "type": "Premolar", "name": "Upper Left First Premolar"},
            "25": {"quadrant": 2, "ID": "25", "type": "Premolar", "name": "Upper Left Second Premolar"},
            "26": {"quadrant": 2, "ID": "26", "type": "Molar", "name": "Upper Left First Molar"},
            "27": {"quadrant": 2, "ID": "27", "type": "Molar", "name": "Upper Left Second Molar"},
            "28": {"quadrant": 2, "ID": "28", "type": "Molar", "name": "Upper Left Third Molar (Wisdom Tooth)"},

            "31": {"quadrant": 3, "ID": "31", "type": "Incisor", "name": "Lower Left Central Incisor"},
            "32": {"quadrant": 3, "ID": "32", "type": "Incisor", "name": "Lower Left Lateral Incisor"},
            "33": {"quadrant": 3, "ID": "33", "type": "Canine", "name": "Lower Left Canine"},
            "34": {"quadrant": 3, "ID": "34", "type": "Premolar", "name": "Lower Left First Premolar"},
            "35": {"quadrant": 3, "ID": "35", "type": "Premolar", "name": "Lower Left Second Premolar"},
            "36": {"quadrant": 3, "ID": "36", "type": "Molar", "name": "Lower Left First Molar"},
            "37": {"quadrant": 3, "ID": "37", "type": "Molar", "name": "Lower Left Second Molar"},
            "38": {"quadrant": 3, "ID": "38", "type": "Molar", "name": "Lower Left Third Molar (Wisdom Tooth)"},

            "41": {"quadrant": 4, "ID": "41", "type": "Incisor", "name": "Lower Right Central Incisor"},
            "42": {"quadrant": 4, "ID": "42", "type": "Incisor", "name": "Lower Right Lateral Incisor"},
            "43": {"quadrant": 4, "ID": "43", "type": "Canine", "name": "Lower Right Canine"},
            "44": {"quadrant": 4, "ID": "44", "type": "Premolar", "name": "Lower Right First Premolar"},
            "45": {"quadrant": 4, "ID": "45", "type": "Premolar", "name": "Lower Right Second Premolar"},
            "46": {"quadrant": 4, "ID": "46", "type": "Molar", "name": "Lower Right First Molar"},
            "47": {"quadrant": 4, "ID": "47", "type": "Molar", "name": "Lower Right Second Molar"},
            "48": {"quadrant": 4, "ID": "48", "type": "Molar", "name": "Lower Right Third Molar (Wisdom Tooth)"}
        }


if __name__ == "__main__":
    annot = FDI_Annotator()
    for k, name in annot.fdi_notation.items():
        print(int(k), name['name'])
