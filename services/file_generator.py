"""
file_generator.py — Génération de fichiers PDF et Word à partir de contenu texte/markdown
"""
import io
import re


def sanitize_for_pdf(text):
    """Remplace les caractères Unicode non supportés par Helvetica par leurs équivalents ASCII"""
    replacements = {
        '\u2014': '-',   # em dash —
        '\u2013': '-',   # en dash –
        '\u2012': '-',   # figure dash
        '\u2015': '-',   # horizontal bar
        '\u2018': "'",   # ' guillemet simple gauche
        '\u2019': "'",   # ' guillemet simple droit
        '\u201a': ',',   # ‚
        '\u201b': "'",   # ‛
        '\u201c': '"',   # " guillemet double gauche
        '\u201d': '"',   # " guillemet double droit
        '\u201e': '"',   # „
        '\u201f': '"',   # ‟
        '\u00ab': '<<',  # «
        '\u00bb': '>>',  # »
        '\u2026': '...', # … ellipse
        '\u00a0': ' ',   # espace insécable
        '\u2022': '-',   # • puce
        '\u25cf': '-',   # ● cercle plein
        '\u2192': '->',  # →
        '\u2190': '<-',  # ←
        '\u2665': '<3',  # ♥
        '\u00b7': '-',   # ·
        '\u00d7': 'x',   # ×
        '\u00f7': '/',   # ÷
        '\u00ae': '(R)', # ®
        '\u00a9': '(C)', # ©
        '\u2122': '(TM)',# ™
        '\u20ac': 'EUR', # €
        '\u00e0': 'a',   # à
        '\u00e2': 'a',   # â
        '\u00e4': 'a',   # ä
        '\u00e7': 'c',   # ç
        '\u00e8': 'e',   # è
        '\u00e9': 'e',   # é
        '\u00ea': 'e',   # ê
        '\u00eb': 'e',   # ë
        '\u00ee': 'i',   # î
        '\u00ef': 'i',   # ï
        '\u00f4': 'o',   # ô
        '\u00f6': 'o',   # ö
        '\u00f9': 'u',   # ù
        '\u00fb': 'u',   # û
        '\u00fc': 'u',   # ü
        '\u00ff': 'y',   # ÿ
        '\u00c0': 'A',   # À
        '\u00c2': 'A',   # Â
        '\u00c7': 'C',   # Ç
        '\u00c8': 'E',   # È
        '\u00c9': 'E',   # É
        '\u00ca': 'E',   # Ê
        '\u00ce': 'I',   # Î
        '\u00d4': 'O',   # Ô
        '\u00d9': 'U',   # Ù
        '\u00db': 'U',   # Û
        '\u00dc': 'U',   # Ü
        '\u0153': 'oe',  # œ
        '\u0152': 'OE',  # Œ
        '\u00e6': 'ae',  # æ
        '\u00c6': 'AE',  # Æ
        '\u00df': 'ss',  # ß
        '\u00f1': 'n',   # ñ
        '\u00e1': 'a',   # á
        '\u00e3': 'a',   # ã
        '\u00e5': 'a',   # å
        '\u00ed': 'i',   # í
        '\u00f3': 'o',   # ó
        '\u00fa': 'u',   # ú
        '\u00fd': 'y',   # ý
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Remplacer tout caractère restant hors ASCII par '?'
    text = text.encode('ascii', errors='replace').decode('ascii')
    return text

def markdown_to_plain(text):
    """Convertit du markdown en texte propre pour les fichiers générés"""
    # Supprimer les blocs de code (garder le contenu)
    text = re.sub(r'```[\w]*\n?', '', text)
    # Titres → texte en majuscules
    text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    # Gras/italique
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Liens
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # Listes
    text = re.sub(r'^\s*[-*+]\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    return sanitize_for_pdf(text.strip())


def parse_sections(content):
    """Découpe le contenu en sections (titre + corps) selon les headers markdown"""
    sections = []
    current_title = None
    current_body = []

    for line in content.split('\n'):
        heading = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading:
            if current_body or current_title:
                sections.append((current_title, '\n'.join(current_body).strip()))
            current_title = heading.group(2).strip()
            current_body = []
        else:
            current_body.append(line)

    if current_body or current_title:
        sections.append((current_title, '\n'.join(current_body).strip()))

    return sections if sections else [(None, content)]


# ── PDF ──────────────────────────────────────────────────────────────────────

def generate_pdf(content, title="Document Cognito Chat"):
    """Génère un PDF et retourne les bytes"""
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(99, 102, 241)
            self.cell(0, 8, 'Cognito Chat — Cognito Inc.', align='R')
            self.ln(4)
            self.set_draw_color(99, 102, 241)
            self.set_line_width(0.3)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # Titre principal
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(99, 102, 241)
    clean_title = markdown_to_plain(title)
    pdf.multi_cell(0, 10, clean_title, align='C')
    pdf.ln(6)

    # Ligne de séparation
    pdf.set_draw_color(99, 102, 241)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(8)

    sections = parse_sections(content)

    for sec_title, sec_body in sections:
        # Titre de section
        if sec_title:
            pdf.set_font('Helvetica', 'B', 13)
            pdf.set_text_color(30, 30, 50)
            pdf.multi_cell(0, 7, markdown_to_plain(sec_title))
            pdf.ln(2)

        # Corps — ligne par ligne
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(40, 40, 60)

        for line in sec_body.split('\n'):
            line = line.rstrip()
            if not line:
                pdf.ln(3)
                continue

            # Ligne de code
            if line.startswith('    ') or line.startswith('\t'):
                pdf.set_font('Courier', '', 9)
                pdf.set_fill_color(240, 242, 255)
                pdf.multi_cell(0, 5, line.strip(), fill=True)
                pdf.set_font('Helvetica', '', 11)
                continue

            # Élément de liste
            if re.match(r'^\s*[-*+•]\s+', line):
                clean = re.sub(r'^\s*[-*+•]\s+', '', line)
                pdf.set_x(20)
                pdf.cell(5, 6, '•')
                pdf.multi_cell(0, 6, markdown_to_plain(clean))
                continue

            # Texte normal
            pdf.multi_cell(0, 6, markdown_to_plain(line))

        pdf.ln(4)

    return bytes(pdf.output())


# ── WORD ─────────────────────────────────────────────────────────────────────

def generate_word(content, title="Document Cognito Chat"):
    """Génère un fichier .docx et retourne les bytes"""
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Marges
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # En-tête
    header = doc.sections[0].header
    hp = header.paragraphs[0]
    hp.text = 'Cognito Chat — Cognito Inc.'
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.runs[0].font.size = Pt(9)
    hp.runs[0].font.color.rgb = RGBColor(99, 102, 241)
    hp.runs[0].font.italic = True

    # Titre principal
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.add_run(markdown_to_plain(title))
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.color.rgb = RGBColor(99, 102, 241)

    doc.add_paragraph()  # espace

    sections = parse_sections(content)

    for sec_title, sec_body in sections:
        # Titre de section
        if sec_title:
            heading = doc.add_heading(markdown_to_plain(sec_title), level=2)
            heading.runs[0].font.color.rgb = RGBColor(30, 30, 80)

        # Corps
        for line in sec_body.split('\n'):
            line = line.rstrip()
            if not line:
                continue

            # Ligne de code
            if line.startswith('    ') or line.startswith('\t'):
                p = doc.add_paragraph(line.strip(), style='No Spacing')
                p.runs[0].font.name = 'Courier New'
                p.runs[0].font.size = Pt(9)
                continue

            # Liste
            if re.match(r'^\s*[-*+•]\s+', line):
                clean = re.sub(r'^\s*[-*+•]\s+', '', line)
                doc.add_paragraph(markdown_to_plain(clean), style='List Bullet')
                continue

            # Liste numérotée
            if re.match(r'^\s*\d+\.\s+', line):
                clean = re.sub(r'^\s*\d+\.\s+', '', line)
                doc.add_paragraph(markdown_to_plain(clean), style='List Number')
                continue

            # Texte normal
            p = doc.add_paragraph()
            cleaned = markdown_to_plain(line)
            # Gras inline
            parts = re.split(r'\*\*(.+?)\*\*', line)
            if len(parts) > 1:
                for i, part in enumerate(parts):
                    run = p.add_run(markdown_to_plain(part))
                    run.bold = (i % 2 == 1)
            else:
                p.add_run(cleaned)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


# ── Détection de demande ─────────────────────────────────────────────────────

def should_generate_file(text):
    """
    Retourne ('pdf', prompt) ou ('word', prompt) ou (None, None)
    """
    text_lower = text.lower()

    action_words = [
        'génère', 'genere', 'générer', 'generer', 'crée', 'cree', 'créer', 'creer',
        'fais', 'faire', 'produis', 'produire', 'rédige', 'redige', 'écris', 'ecris',
        'generate', 'create', 'make', 'write', 'produce'
    ]
    has_action = any(w in text_lower for w in action_words)

    pdf_words = ['pdf', 'fichier pdf', 'document pdf', 'en pdf', 'au format pdf']
    word_words = ['word', 'docx', 'fichier word', 'document word', 'en word', 'au format word',
                  'fichier .docx', 'microsoft word']

    is_pdf = any(w in text_lower for w in pdf_words)
    is_word = any(w in text_lower for w in word_words)

    if not (is_pdf or is_word):
        return None, None

    # Extraire le sujet : retirer les mots de commande et de format
    subject = text
    for w in ['génère', 'genere', 'générer', 'crée', 'cree', 'créer', 'fais moi', 'fais-moi',
              'un pdf', 'une pdf', 'un word', 'une word', 'un fichier', 'un document',
              'au format pdf', 'en pdf', 'au format word', 'en word', 'pdf', 'word', 'docx']:
        subject = re.sub(re.escape(w), '', subject, flags=re.IGNORECASE).strip()
    subject = subject.strip(' ,.-:')
    if not subject:
        subject = text

    if is_pdf:
        return 'pdf', subject
    return 'word', subject
