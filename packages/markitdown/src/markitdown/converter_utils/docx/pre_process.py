import struct
import zipfile
import zlib
from io import BytesIO
from typing import BinaryIO, List, Tuple
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup, Tag

from .math.omml import OMML_NS, oMath2Latex

MATH_ROOT_TEMPLATE = "".join(
    (
        "<w:document ",
        'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" ',
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" ',
        'xmlns:o="urn:schemas-microsoft-com:office:office" ',
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ',
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" ',
        'xmlns:v="urn:schemas-microsoft-com:vml" ',
        'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" ',
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" ',
        'xmlns:w10="urn:schemas-microsoft-com:office:word" ',
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" ',
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" ',
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" ',
        'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" ',
        'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" ',
        'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 wp14">',
        "{0}</w:document>",
    )
)


def _convert_omath_to_latex(tag: Tag) -> str:
    """
    Converts an OMML (Office Math Markup Language) tag to LaTeX format.

    Args:
        tag (Tag): A BeautifulSoup Tag object representing the OMML element.

    Returns:
        str: The LaTeX representation of the OMML element.
    """
    # Format the tag into a complete XML document string
    math_root = ET.fromstring(MATH_ROOT_TEMPLATE.format(str(tag)))
    # Find the 'oMath' element within the XML document
    math_element = math_root.find(OMML_NS + "oMath")
    # Convert the 'oMath' element to LaTeX using the oMath2Latex function
    latex = oMath2Latex(math_element).latex
    return latex


def _get_omath_tag_replacement(tag: Tag, block: bool = False) -> Tag:
    """
    Creates a replacement tag for an OMML (Office Math Markup Language) element.

    Args:
        tag (Tag): A BeautifulSoup Tag object representing the "oMath" element.
        block (bool, optional): If True, the LaTeX will be wrapped in double dollar signs for block mode. Defaults to False.

    Returns:
        Tag: A BeautifulSoup Tag object representing the replacement element.
    """
    t_tag = Tag(name="w:t")
    t_tag.string = (
        f"$${_convert_omath_to_latex(tag)}$$"
        if block
        else f"${_convert_omath_to_latex(tag)}$"
    )
    r_tag = Tag(name="w:r")
    r_tag.append(t_tag)
    return r_tag


def _replace_equations(tag: Tag):
    """
    Replaces OMML (Office Math Markup Language) elements with their LaTeX equivalents.

    Args:
        tag (Tag): A BeautifulSoup Tag object representing the OMML element. Could be either "oMathPara" or "oMath".

    Raises:
        ValueError: If the tag is not supported.
    """
    if tag.name == "oMathPara":
        # Create a new paragraph tag
        p_tag = Tag(name="w:p")
        # Replace each 'oMath' child tag with its LaTeX equivalent as block equations
        for child_tag in tag.find_all("oMath"):
            p_tag.append(_get_omath_tag_replacement(child_tag, block=True))
        # Replace the original 'oMathPara' tag with the new paragraph tag
        tag.replace_with(p_tag)
    elif tag.name == "oMath":
        # Replace the 'oMath' tag with its LaTeX equivalent as inline equation
        tag.replace_with(_get_omath_tag_replacement(tag, block=False))
    else:
        raise ValueError(f"Not supported tag: {tag.name}")


def _pre_process_math(content: bytes) -> bytes:
    """
    Pre-processes the math content in a DOCX -> XML file by converting OMML (Office Math Markup Language) elements to LaTeX.
    This preprocessed content can be directly replaced in the DOCX file -> XMLs.

    Args:
        content (bytes): The XML content of the DOCX file as bytes.

    Returns:
        bytes: The processed content with OMML elements replaced by their LaTeX equivalents, encoded as bytes.
    """
    soup = BeautifulSoup(content.decode(), features="xml")
    for tag in soup.find_all("oMathPara"):
        _replace_equations(tag)
    for tag in soup.find_all("oMath"):
        _replace_equations(tag)
    return str(soup).encode()


def _extract_member_raw(raw: bytes, info: zipfile.ZipInfo) -> bytes:
    """
    Extracts a single zip member's bytes directly from its local file header,
    bypassing zipfile's strict local-vs-central filename check.

    Some tools (e.g. certain Word/Microsoft Graph exports) emit .docx files whose
    local file header stores a filename with different letter-casing than the
    central directory entry (e.g. local ``customXML/item5.xml`` vs central
    ``customXml/item5.xml``). Python's ``zipfile`` rejects these with
    ``BadZipFile``. This helper reads the compressed data using the offsets from
    the central directory (``info``) and decompresses it manually.

    Args:
        raw (bytes): The full bytes of the zip/docx file.
        info (zipfile.ZipInfo): The central-directory info for the member.

    Returns:
        bytes: The decompressed member content.
    """
    off = info.header_offset
    if raw[off : off + 4] != b"PK\x03\x04":
        raise zipfile.BadZipFile(
            f"Bad local file header for {info.filename!r} at offset {off}"
        )
    fname_len = struct.unpack("<H", raw[off + 26 : off + 28])[0]
    extra_len = struct.unpack("<H", raw[off + 28 : off + 30])[0]
    data_start = off + 30 + fname_len + extra_len
    compressed = raw[data_start : data_start + info.compress_size]

    if info.compress_type == zipfile.ZIP_STORED:
        return compressed
    if info.compress_type == zipfile.ZIP_DEFLATED:
        return zlib.decompress(compressed, -15)
    raise zipfile.BadZipFile(
        f"Unsupported compression type {info.compress_type} for {info.filename!r}"
    )


def _read_docx_members(input_docx: BinaryIO) -> Tuple[bytes, List[Tuple[str, bytes]]]:
    """
    Reads every member of a (possibly slightly malformed) .docx zip.

    Falls back to :func:`_extract_member_raw` for any member that ``zipfile``
    refuses to read because of a local-vs-central filename mismatch, so that
    documents with inconsistent internal filename casing can still be converted.

    Args:
        input_docx (BinaryIO): The binary input stream of the .docx file.

    Returns:
        Tuple[bytes, List[Tuple[str, bytes]]]: The zip archive comment and an
        ordered list of ``(member_name, content)`` pairs.
    """
    input_docx.seek(0)
    raw = input_docx.read()

    with zipfile.ZipFile(BytesIO(raw), mode="r") as zip_input:
        comment = zip_input.comment
        members: List[Tuple[str, bytes]] = []
        for info in zip_input.infolist():
            try:
                content = zip_input.read(info.filename)
            except zipfile.BadZipFile:
                content = _extract_member_raw(raw, info)
            members.append((info.filename, content))
    return comment, members


def pre_process_docx(input_docx: BinaryIO) -> BinaryIO:
    """
    Pre-processes a DOCX file with provided steps.

    The process works by unzipping the DOCX file in memory, transforming specific XML files
    (such as converting OMML elements to LaTeX), and then zipping everything back into a
    DOCX file without writing to disk.

    Args:
        input_docx (BinaryIO): A binary input stream representing the DOCX file.

    Returns:
        BinaryIO: A binary output stream representing the processed DOCX file.
    """
    output_docx = BytesIO()
    # The files that need to be pre-processed from .docx
    pre_process_enable_files = [
        "word/document.xml",
        "word/footnotes.xml",
        "word/endnotes.xml",
    ]
    # Read members tolerantly so that documents with mismatched internal
    # filename casing (BadZipFile) can still be re-zipped and converted.
    comment, members = _read_docx_members(input_docx)
    with zipfile.ZipFile(output_docx, mode="w") as zip_output:
        zip_output.comment = comment
        for name, content in members:
            if name in pre_process_enable_files:
                try:
                    # Pre-process the content
                    updated_content = _pre_process_math(content)
                    # In the future, if there are more pre-processing steps, they can be added here
                    zip_output.writestr(name, updated_content)
                except Exception:
                    # If there is an error in processing the content, write the original content
                    zip_output.writestr(name, content)
            else:
                zip_output.writestr(name, content)
    output_docx.seek(0)
    return output_docx
