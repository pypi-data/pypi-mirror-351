import logging
from lxf import settings

logger = logging.getLogger('Test Analysis')
fh = logging.FileHandler('./logs/extract_titles.log')
fh.setLevel(settings.get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(settings.get_logging_level())
logger.addHandler(fh)

from collections import defaultdict
import pdfplumber
import re

def extract_text_with_format(pdf_path):
    """
    """
    formatted_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for word in page.extract_words(extra_attrs=["size", "fontname"]):
                word["bold"] = "Bold" in word.get("fontname", "")
                formatted_text.append(word)
    return formatted_text

def filter_titles_with_regex(words):
    """
    """
    titles = []
    regex = r"^[0-9.]{0,}(I|II|III|IV|V|VI)*[)\.\- ]{0,1}[A-Z’']{2,}.{1,60}$"
    for word in words:
        if re.match(regex, word["text"]):
            titles.append(word)
    return titles

def detect_title_candidates(candidates, font_size_threshold=5, bold=True):
    """
    """
    titles = []
    for word in candidates:
        if word["size"] > font_size_threshold and word["bold"] == bold:
            titles.append(word)
    return titles

def group_words_by_line(words, tolerance=5):
    """
    """
    lines = []
    current_line = []
    current_y0 = None

    sorted_words = sorted(words, key=lambda w: (w["doctop"]))

    for word in sorted_words:
        if current_y0 is None or abs(word["doctop"] - current_y0) < tolerance:
            current_line.append(word)
        else:
            if current_line:
                lines.append(current_line)
            current_line = [word]
        current_y0 = word["doctop"]

    if current_line:
        lines.append(current_line)

    return lines

def concatenate_multi_line_titles(lines, line_gap_threshold=30):
    """
    """
    titles = []
    i = 0
    while i < len(lines):
        current_line = lines[i]
        title = " ".join(word["text"] for word in current_line)

        if i + 1 < len(lines):
            next_line = lines[i + 1]
            gap = next_line[0]["doctop"] - current_line[-1]["doctop"]
            if gap < line_gap_threshold:
                title += " " + " ".join(word["text"] for word in next_line)
                i += 1  

        titles.append(title)
        i += 1

    return titles

pdf_path = "data/Accord de confidentialité LexFluent MaSuccessionFR.pdf"

formatted_text = extract_text_with_format(pdf_path)
candidates = filter_titles_with_regex(formatted_text)

titles = detect_title_candidates(candidates)

grouped_titles = group_words_by_line(titles)

final_titles = concatenate_multi_line_titles(grouped_titles)

print("Titres extraits :", final_titles)