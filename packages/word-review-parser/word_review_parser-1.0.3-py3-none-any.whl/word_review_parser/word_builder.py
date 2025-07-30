# --- ADD: Module docstring ---
"""Module for building Word documents with revisions and comments from parsed data."""
# --- END ADD ---
import os
import zipfile
from lxml import etree
import uuid
from datetime import datetime, timezone # Import timezone
import logging
import shutil # Import shutil for copytree and rmtree
import re # Import re for parsing options

# --- ADD: Configure logging ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] - %(message)s')
logger = logging.getLogger(__name__)
# --- END ADD ---

class WordBuilder:
    """
    Builds a Word document (.docx) by injecting revisions (added, deleted, replaced)
    and comments into its underlying XML structure.
    """
    def __init__(self, template_path: str, output_path: str):
        """
        Initializes the WordBuilder with paths for the template and output document.

        Args:
            template_path: The path to the base Word document template (unzipped directory).
            output_path: The desired path for the output .docx file.
        """
        self._template_path = template_path
        self._output_path = output_path
        self._temp_unzip_path = os.path.join(os.path.dirname(output_path), f"temp_word_build_{uuid.uuid4().hex}")
        self.nsmap = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
            'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
            'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
            'v': 'urn:schemas-microsoft-com:vml',
            'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
            'wpc': 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas',
            'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
            'o': 'urn:schemas-microsoft-com:office:office',
            've': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
            'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
            'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
            'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
            'wsp': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
            'w16du': 'http://schemas.microsoft.com/office/word/2023/wordml/word16du' # Added w16du namespace
        }
        logger.info(f"Initialized WordBuilder with template: {template_path}, output: {output_path}")

    def _get_xml_path(self, part_name: str) -> str:
        """Helper to get the full path to an XML part within the template."""
        return os.path.join(self._template_path, part_name)

    def _read_xml(self, part_name: str):
        """Reads and parses an XML part from the template."""
        xml_path = self._get_xml_path(part_name)
        if not os.path.exists(xml_path):
            logger.warning(f"XML part not found: {xml_path}")
            return None
        try:
            return etree.parse(xml_path)
        except Exception as e:
            logger.error(f"Error parsing {xml_path}: {e}", exc_info=True)
            return None

    def _write_xml(self, tree, part_name: str):
        """Writes an XML tree back to the template directory."""
        output_xml_path = os.path.join(self._temp_unzip_path, part_name)
        os.makedirs(os.path.dirname(output_xml_path), exist_ok=True)
        try:
            tree.write(output_xml_path, encoding='UTF-8', xml_declaration=True, standalone=True)
            logger.debug(f"Successfully wrote XML to {output_xml_path}")
        except Exception as e:
            logger.error(f"Error writing XML to {output_xml_path}: {e}", exc_info=True)

    def _create_run_element(self, text: str, is_bold: bool = False, is_italic: bool = False):
        """Creates a w:r (run) element with w:t (text) and optional formatting."""
        r = etree.Element(etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
        if is_bold or is_italic:
            rpr = etree.SubElement(r, etree.QName(self.nsmap['w'], 'rPr'), nsmap=self.nsmap)
            if is_bold:
                etree.SubElement(rpr, etree.QName(self.nsmap['w'], 'b'), nsmap=self.nsmap)
            if is_italic:
                etree.SubElement(rpr, etree.QName(self.nsmap['w'], 'i'), nsmap=self.nsmap)
        t = etree.SubElement(r, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap)
        t.text = text
        # Preserve whitespace if necessary
        # Preserve whitespace if necessary using xml:space
        if text.startswith(' ') or text.endswith(' ') or '  ' in text:
             t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        return r

    def _create_comment_element(self, comment_id: str, author: str, date: str, text: str):
        """Creates a w:comment element."""
        comment = etree.Element(etree.QName(self.nsmap['w'], 'comment'), nsmap=self.nsmap,
                                id=comment_id, author=author, date=date)
        p = etree.SubElement(comment, etree.QName(self.nsmap['w'], 'p'), nsmap=self.nsmap)
        # Correctly create run and text elements within the paragraph
        r = etree.SubElement(p, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
        t = etree.SubElement(r, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap)
        t.text = text
        # Preserve whitespace if necessary
        # Preserve whitespace if necessary using xml:space
        if text.startswith(' ') or text.endswith(' ') or '  ' in text:
             t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        return comment

    def _create_revision_element(self, tag_type: str, text: str, author: str = "Author", date: str = None, revision_id: str = None):
        """Creates w:ins or w:del elements for revisions."""
        if date is None:
            date = datetime.now().isoformat(timespec='seconds') + 'Z' # ISO 8601 format
        if revision_id is None:
            # Generate a 32-bit integer ID for w:id attribute
            revision_id = str(uuid.uuid4().int & (1<<32)-1)

        # Convert ISO 8601 date to UTC for w16du:dateUtc
        try:
            date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
            date_utc = date_obj.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
        except ValueError:
            logger.warning(f"Could not parse date '{date}' for revision. Using current UTC date.")
            date_utc = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

        # Attributes for the revision element
        attrib = {
            'id': revision_id,
            'author': author,
            'date': date,
            f"{{{self.nsmap['w16du']}}}dateUtc": date_utc # Corrected attribute key
        }

        if tag_type == 'added':
            ins = etree.Element(etree.QName(self.nsmap['w'], 'ins'), nsmap=self.nsmap, **attrib)
            r = etree.SubElement(ins, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
            rpr = etree.SubElement(r, etree.QName(self.nsmap['w'], 'rPr'), nsmap=self.nsmap)
            etree.SubElement(rpr, etree.QName(self.nsmap['w'], 'rFonts'), nsmap=self.nsmap, **{f"{{{self.nsmap['w']}}}hint": 'eastAsia'}) # Corrected attribute key
            etree.SubElement(rpr, etree.QName(self.nsmap['w'], 'b'), nsmap=self.nsmap)
            etree.SubElement(rpr, etree.QName(self.nsmap['w'], 'bCs'), nsmap=self.nsmap) # Bold for complex script
            t = etree.SubElement(r, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap) # Text element inside run
            t.text = text
            # Preserve whitespace if necessary
            # Preserve whitespace if necessary using xml:space
            if text.startswith(' ') or text.endswith(' ') or '  ' in text:
                 t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            return ins
        elif tag_type == 'deleted':
            dele = etree.Element(etree.QName(self.nsmap['w'], 'del'), nsmap=self.nsmap, **attrib)
            # Using fixed rsid for now, as they are typically generated by Word
            # These rsid values are from the user's example, crucial for Word's internal tracking
            r = etree.SubElement(dele, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap,
                                 **{f"{{{self.nsmap['w']}}}rsidRPr": '00197EB9', f"{{{self.nsmap['w']}}}rsidDel": '00197EB9'}) # Corrected attribute keys
            rpr = etree.SubElement(r, etree.QName(self.nsmap['w'], 'rPr'), nsmap=self.nsmap)
            etree.SubElement(rpr, etree.QName(self.nsmap['w'], 'b'), nsmap=self.nsmap)
            etree.SubElement(rpr, etree.QName(self.nsmap['w'], 'bCs'), nsmap=self.nsmap) # Bold for complex script
            del_text_elem = etree.SubElement(r, etree.QName(self.nsmap['w'], 'delText'), nsmap=self.nsmap)
            del_text_elem.text = text
            # Preserve whitespace if necessary
            # Preserve whitespace if necessary using xml:space
            if text.startswith(' ') or text.endswith(' ') or '  ' in text:
                 del_text_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            return dele
        else:
            logger.warning(f"Unsupported revision type: {tag_type}")
            return None

    def _copy_template_to_temp(self):
        """Copies the template directory to a temporary location for modification."""
        logger.info(f"Copying template from {self._template_path} to {self._temp_unzip_path}")
        try:
            if os.path.exists(self._temp_unzip_path):
                shutil.rmtree(self._temp_unzip_path)
            shutil.copytree(self._template_path, self._temp_unzip_path)
            logger.info("Template copied successfully.")
            return True
        except Exception as e:
            logger.error(f"Error copying template directory: {e}", exc_info=True)
            return False

    def _zip_temp_to_docx(self):
        """Zips the temporary directory into a .docx file."""
        logger.info(f"Zipping temporary directory {self._temp_unzip_path} to {self._output_path}")
        try:
            with zipfile.ZipFile(self._output_path, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
                for root, _, files in os.walk(self._temp_unzip_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Calculate relative path inside the zip
                        arcname = os.path.relpath(full_path, self._temp_unzip_path)
                        docx_zip.write(full_path, arcname)
            logger.info("Document zipped successfully.")
            return True
        except Exception as e:
            logger.error(f"Error zipping document: {e}", exc_info=True)
            return False
        finally:
            # Clean up temporary directory
            if os.path.exists(self._temp_unzip_path):
                shutil.rmtree(self._temp_unzip_path)
                logger.info(f"Cleaned up temporary directory: {self._temp_unzip_path}")

    def build_document(self, latex_text: str, parsed_latex_data: list):
        """
        Builds the Word document by inserting revisions and comments based on parsed LaTeX data.

        Args:
            latex_text: The original LaTeX text string.
            parsed_latex_data: A list of dictionaries, each representing a parsed LaTeX tag.
                               Example: [{'type': 'added', 'content': '...', 'line_num': ..., 'start_pos': ..., 'end_pos': ...}]
        Returns:
            bool: True if the document was built successfully, False otherwise.
        """
        if not self._copy_template_to_temp():
            return False

        document_xml_path_in_temp = os.path.join(self._temp_unzip_path, 'word', 'document.xml')
        comments_xml_path_in_temp = os.path.join(self._temp_unzip_path, 'word', 'comments.xml')

        document_tree = self._read_xml(os.path.join('word', 'document.xml'))
        comments_tree = self._read_xml(os.path.join('word', 'comments.xml'))

        if document_tree is None:
            logger.error("Failed to load document.xml from template.")
            return False

        # Get the root element of document.xml
        document_root = document_tree.getroot()

        # Ensure comments.xml exists or create a basic one if needed
        comments_root = None
        if comments_tree is None:
            logger.info("comments.xml not found in template, creating a new one.")
            comments_root = etree.Element(etree.QName(self.nsmap['w'], 'comments'), nsmap=self.nsmap)
            comments_tree = etree.ElementTree(comments_root) # Assign the new tree to comments_tree
            # Add a default commentsIds element if it doesn't exist
            comments_ids_path = os.path.join(self._temp_unzip_path, 'word', 'commentsIds.xml')
            if not os.path.exists(comments_ids_path):
                comments_ids_root = etree.Element(etree.QName(self.nsmap['w'], 'commentsIds'), nsmap=self.nsmap)
                etree.SubElement(comments_ids_root, etree.QName(self.nsmap['w'], 'unusedParagraphId'), nsmap=self.nsmap, id="0")
                self._write_xml(etree.ElementTree(comments_ids_root), os.path.join('word', 'commentsIds.xml'))
        else:
            comments_root = comments_tree.getroot() # Get root if tree already exists


        # Find the body element
        body = document_root.xpath('//w:body', namespaces=self.nsmap)[0]

        # Remove existing content from the body, keeping sectPr if it exists
        sect_pr = body.xpath('./w:sectPr', namespaces=self.nsmap)
        for child in list(body):
            if child not in sect_pr:
                body.remove(child)

        current_comment_id = 1000 # Start comment IDs from a high number to avoid conflicts

        # Group parsed data by line number and sort within lines
        parsed_data_by_line = {}
        for data in parsed_latex_data:
            line_num = data['line_num']
            if line_num not in parsed_data_by_line:
                parsed_data_by_line[line_num] = []
            parsed_data_by_line[line_num].append(data)

        # Sort tags within each line by start position
        for line_num in parsed_data_by_line:
            parsed_data_by_line[line_num].sort(key=lambda x: x['start_pos'])

        latex_lines = latex_text.splitlines()

        for line_num, line_content in enumerate(latex_lines):
            current_pos = 0
            line_tags = parsed_data_by_line.get(line_num + 1, []) # +1 because line_num in data is 1-based

            # Create a new paragraph for each line
            p = etree.SubElement(body, etree.QName(self.nsmap['w'], 'p'), nsmap=self.nsmap)

            for tag_data in line_tags:
                # Add plain text before the tag
                plain_text_before = line_content[current_pos:tag_data['start_pos']]
                if plain_text_before:
                    r = etree.SubElement(p, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
                    t = etree.SubElement(r, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap)
                    t.text = plain_text_before
                    # Preserve whitespace if necessary
                    # Preserve whitespace if necessary using xml:space
                    if plain_text_before.startswith(' ') or plain_text_before.endswith(' ') or '  ' in plain_text_before:
                         t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                    current_pos = tag_data['start_pos']


                # Add the tag element
                if tag_data['type'] == 'added':
                    ins_element = self._create_revision_element('added', tag_data['content'], author="LaTeX User", date=datetime.now().isoformat(timespec='seconds') + 'Z')
                    if ins_element is not None:
                        p.append(ins_element)
                    logger.debug(f"Added 'added' revision to document.xml: {tag_data['content'][:50]}")
                elif tag_data['type'] == 'deleted':
                    del_element = self._create_revision_element('deleted', tag_data['content'], author="LaTeX User", date=datetime.now().isoformat(timespec='seconds') + 'Z')
                    if del_element is not None:
                        p.append(del_element)
                    logger.debug(f"Added 'deleted' revision to document.xml: {tag_data['content'][:50]}")
                elif tag_data['type'] == 'replaced':
                    # Replaced is a combination of deleted and added
                    del_element = self._create_revision_element('deleted', tag_data['original_content'], author="LaTeX User", date=datetime.now().isoformat(timespec='seconds') + 'Z')
                    ins_element = self._create_revision_element('added', tag_data['new_content'], author="LaTeX User", date=datetime.now().isoformat(timespec='seconds') + 'Z')
                    if del_element is not None:
                        p.append(del_element)
                    if ins_element is not None:
                        p.append(ins_element)
                    logger.debug(f"Added 'replaced' revision to document.xml: Original='{tag_data['original_content'][:50]}', New='{tag_data['new_content'][:50]}'")
                elif tag_data['type'] == 'comment':
                    current_comment_id += 1
                    comment_text = tag_data['content']
                    author = "LaTeX User" # Placeholder
                    date = datetime.now().isoformat(timespec='seconds') + 'Z'

                    # Add comment to comments.xml
                    comment_element = self._create_comment_element(str(current_comment_id), author, date, comment_text)
                    if comments_root is not None:
                        comments_root.append(comment_element)

                    # Add comment reference in document.xml
                    # This is a simplified approach. In a real Word document, commentRangeStart/End
                    # would wrap the commented text, and w:commentReference would be within a w:r.
                    # For now, we'll add a run with the comment text and a reference.
                    # A more accurate approach would require finding the text the comment applies to
                    # and wrapping it with commentRangeStart/End, then adding commentReference.
                    # For now, adding a run with the comment text and reference after the text it was
                    # associated with in LaTeX is a reasonable approximation.

                    # Add the comment text as a run (optional, but helps visualize)
                    r_comment_text = etree.SubElement(p, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
                    t_comment_text = etree.SubElement(r_comment_text, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap)
                    t_comment_text.text = f" [Comment: {comment_text}]" # Add comment text visually
                    # Preserve whitespace if necessary
                    # Preserve whitespace if necessary using xml:space
                    if comment_text.startswith(' ') or comment_text.endswith(' ') or '  ' in comment_text:
                         t_comment_text.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


                    # Add the w:commentReference run
                    r_comment_ref = etree.SubElement(p, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
                    rpr_comment_ref = etree.SubElement(r_comment_ref, etree.QName(self.nsmap['w'], 'rPr'), nsmap=self.nsmap)
                    etree.SubElement(rpr_comment_ref, etree.QName(self.nsmap['w'], 'rStyle'), nsmap=self.nsmap, **{f"{{{self.nsmap['w']}}}val": 'af'}) # 'af' is often used for annotation reference style
                    etree.SubElement(r_comment_ref, etree.QName(self.nsmap['w'], 'commentReference'), nsmap=self.nsmap, id=str(current_comment_id))

                    logger.debug(f"Added 'comment' to document.xml and comments.xml: {comment_text[:50]}")
                elif tag_data['type'] == 'highlight':
                    # Highlights are not standard revisions. We'll just add the text with a highlight run property for now.
                    # This requires wrapping the text in a run with rPr and highlight.
                    # This is a simplified approach and might not handle complex cases.
                    highlight_text = tag_data['content']
                    r_highlight = etree.SubElement(p, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
                    rpr_highlight = etree.SubElement(r_highlight, etree.QName(self.nsmap['w'], 'rPr'), nsmap=self.nsmap)
                    etree.SubElement(rpr_highlight, etree.QName(self.nsmap['w'], 'highlight'), nsmap=self.nsmap, **{f"{{{self.nsmap['w']}}}val": 'yellow'}) # Default yellow highlight
                    t_highlight = etree.SubElement(r_highlight, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap)
                    t_highlight.text = highlight_text
                    # Preserve whitespace if necessary
                    if highlight_text.startswith(' ') or highlight_text.endswith(' ') or '  ' in highlight_text:
                         t_highlight.set(etree.QName(self.nsmap['w'], 'space'), 'preserve')
                    logger.debug(f"Added 'highlight' to document.xml: {highlight_text[:50]}")


                # Update current position to the end of the tag
                current_pos = tag_data['end_pos']

                # Check for and add space immediately after the tag
                if current_pos < len(line_content) and line_content[current_pos] == ' ':
                    r_space = etree.SubElement(p, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
                    t_space = etree.SubElement(r_space, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap)
                    t_space.text = ' '
                    t_space.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                    current_pos += 1


            # Add any remaining plain text after the last tag in the line
            remaining_text = line_content[current_pos:]
            if remaining_text:
                r = etree.SubElement(p, etree.QName(self.nsmap['w'], 'r'), nsmap=self.nsmap)
                t = etree.SubElement(r, etree.QName(self.nsmap['w'], 't'), nsmap=self.nsmap)
                t.text = remaining_text
                # Preserve whitespace if necessary
                # Preserve whitespace if necessary using xml:space
                if remaining_text.startswith(' ') or remaining_text.endswith(' ') or '  ' in remaining_text:
                     t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


        # Re-add the sectPr at the end of the body if it existed
        if sect_pr:
            body.append(sect_pr[0])


        # Write modified XML files back to the temporary directory
        self._write_xml(etree.ElementTree(document_root), os.path.join('word', 'document.xml'))
        if comments_tree is not None:
            self._write_xml(comments_tree, os.path.join('word', 'comments.xml'))

        # Zip the temporary directory into the final .docx
        return self._zip_temp_to_docx()
