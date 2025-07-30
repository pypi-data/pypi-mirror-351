# markdown_converter_1/converter_core.py
import io
import os
import subprocess
import tempfile
import asyncio
import logging
import sys # Import sys for platform check

import markdown
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError # Import PlaywrightTimeoutError


# --- Configuration / Constants ---

# Define the environment variable names for configuration
PANDOC_PATH_ENV_VAR = 'PANDOC_PATH'
REFERENCE_DOCX_PATH_ENV_VAR = 'REFERENCE_DOCX_PATH'

# We keep the variable names here so __init__.py can import them.
# Actual values are read from the environment where needed (inside functions).


# Base CSS for good PDF structure and readability
BASE_PDF_CSS = """
/* --- Base PDF Styles (Enhanced) --- */

/* General Body Styles */
body {
    font-family: 'Arial', 'Helvetica', 'Verdana', sans-serif; /* Prioritize common sans-serif fonts */
    line-height: 1.6; /* Improve readability */
    color: #2d3748; /* Slightly softer black */
    margin: 0; /* Margins controlled by @page */
    padding: 0;
    font-size: 11pt; /* Default font size */
    hyphens: auto; /* Enable hyphenation if supported */
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-weight: bold;
    margin-top: 1.8em; /* More space above headings */
    margin-bottom: 0.8em; /* Space below headings */
    line-height: 1.2; /* Tighter line spacing for headings */
    page-break-after: avoid; /* Try not to break a page immediately after a heading */
    color: #1a202c; /* Darker color for headings */
}

h1 {
    font-size: 26pt; /* Larger H1 */
    border-bottom: 2px solid #cbd5e0; /* More prominent separator */
    padding-bottom: 0.5em;
    margin-top: 2.5em; /* More space before H1 */
    /* Consider page-break-before: always; if you want each H1 to start a new page */
    margin-top: 0; /* Reset top margin if breaking page */
}

h2 { font-size: 20pt; border-bottom: 1px solid #edf2f7; padding-bottom: 0.3em;}
h3 { font-size: 16pt; }
h4 { font-size: 13pt; }
h5 { font-size: 12pt; color: #4a5568; }
h6 { font-size: 11pt; color: #718096; text-transform: uppercase; font-weight: normal;} /* Subtler H6 */

/* Paragraphs */
p {
    margin-top: 0;
    margin-bottom: 1em; /* Space between paragraphs */
    text-align: justify; /* Justify text for a cleaner look */
    orphans: 3; /* Prevent widows and orphans */
    widows: 3;
}

/* Links */
a {
    color: #3182ce; /* A standard blue */
    text-decoration: underline;
}
a:visited {
     color: #805ad5; /* A standard purple */
}

/* Lists */
ul, ol {
    margin-top: 0;
    margin-bottom: 1em;
    padding-left: 2em; /* Indent lists */
}
li {
    margin-bottom: 0.5em; /* Space between list items */
    line-height: 1.5; /* Improve spacing within list items */
    orphans: 3;
    widows: 3;
}

/* Code - Inline */
code {
    font-family: 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
    background-color: #f7fafc; /* Very light background */
    border: 1px solid #e2e8f0; /* Subtle border */
    padding: 0.2em 0.4em; /* Slight padding around code */
    border-radius: 3px; /* Rounded corners */
    font-size: 0.9em; /* Slightly smaller */
    color: #4a5568; /* Match body color or slightly darker */
}

/* Code - Blocks (pre) */
pre {
    font-family: 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
    background-color: #edf2f7; /* Light background */
    border: 1px solid #e2e8f0; /* Subtle border */
    padding: 1em;
    margin-bottom: 1.5em;
    overflow-x: auto; /* Scroll for long lines */
    border-radius: 5px;
    page-break-inside: avoid; /* Try to keep code block on one page */
    font-size: 0.9em;
    line-height: 1.4; /* Tighter line spacing for code */
}
pre code {
    background-color: transparent; /* Code inside pre doesn't need its own background */
    border: none; /* Remove border from inline code inside pre */
    padding: 0;
    border-radius: 0;
    font-size: 1em; /* Reset font size inside pre */
    color: inherit; /* Inherit color from pre or highlighting */
}

/* --- Pygments Code Highlighting CSS (Default Theme) --- */
/* Generated using: pygmentize -S default -f html -a .highlight > pygments_default.css */
/* This style block applies colors to elements *within* <pre><code>...</code></pre> */
.highlight .hll { background-color: #ffffcc }
.highlight  { background: #ffffff; } /* Background set on pre instead */
.highlight .c { color: #999988; font-style: italic } /* Comment */
.highlight .err { color: #a61717; background-color: #e3d2d2 } /* Error */
.highlight .k { color: #000000; font-weight: bold } /* Keyword */
.highlight .o { color: #000000; font-weight: bold } /* Operator */
.highlight .cm { color: #999988; font-style: italic } /* Comment.Multiline */
.highlight .cp { color: #999998; font-weight: bold } /* Comment.Preproc */
.highlight .c1 { color: #999988; font-style: italic } /* Comment.Single */
.highlight .cs { color: #999998; font-weight: bold; font-style: italic } /* Comment.Special */
.highlight .gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
.highlight .ge { color: #000000; font-style: italic } /* Generic.Emph */
.highlight .gr { color: #aa0000 } /* Generic.Error */
.highlight .gh { color: #999999 } /* Generic.Heading */
.highlight .gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
.highlight .go { color: #888888 } /* Generic.Output */
.highlight .gp { color: #555555 } /* Generic.Prompt */
.highlight .gs { font-weight: bold } /* Generic.Strong */
.highlight .gu { color: #aaaaaa } /* Generic.Subheading */
.highlight .gt { color: #aa0000 } /* Generic.Traceback */
.highlight .il { color: #009999 } /* Literal.Number.Integer.Long */
.highlight .ld { color: #009999 } /* Literal.Number.Decimal */
.highlight .m { color: #009999 } /* Literal.Number */
.highlight .mb { color: #009999 } /* Literal.Number.Binary */
.highlight .mf { color: #009999 } /* Literal.Number.Float */
.highlight .mh { color: #009999 } /* Literal.Number.Hex */
.highlight .mi { color: #009999 } /* Literal.Number.Integer */
.highlight .mo { color: #009999 } /* Literal.Number.Oct */
.highlight .sb { color: #e37a00 } /* Literal.String.Backtick */
.highlight .sc { color: #e37a00 } /* Literal.String.Char */
.highlight .sd { color: #e37a00; font-style: italic } /* Literal.String.Doc */
.highlight .s2 { color: #e37a00 } /* Literal.String.Double */
.highlight .se { color: #e37a00; font-weight: bold } /* Literal.String.Escape */
.highlight .sh { color: #e37a00 } /* Literal.String.Heredoc */
.highlight .si { color: #e37a00 } /* Literal.String.Interpol */
.highlight .sx { color: #e37a00 } /* Literal.String.Other */
.highlight .sr { color: #009900 } /* Literal.String.Regex */
.highlight .s1 { color: #e37a00 } /* Literal.String.Single */
.highlight .ss { color: #990000 } /* Literal.String.Symbol */
.highlight .bp { color: #999999 } /* Name.Builtin.Pseudo */
.highlight .vc { color: #008080 } /* Name.Variable.Class */
.highlight .vg { color: #008080 } /* Name.Variable.Global */
.highlight .vi { color: #008080 } /* Name.Variable.Instance */
.highlight .nv { color: #008080 } /* Name.Variable */
.highlight .sa { color: #e37a00 } /* Literal.String.Affix */
.highlight .fe { color: #e37a00 } /* Literal.String.Escape.Foreign */
.highlight .nb { color: #000000; font-weight: bold } /* Name.Builtin */
.highlight .nn { color: #555555 } /* Name.Namespace */
.highlight .nc { color: #000000; font-weight: bold } /* Name.Class */
.highlight .ne { color: #000000; font-weight: bold } /* Name.Exception */
.highlight .nf { color: #000000; font-weight: bold } /* Name.Function */
.highlight .nl { color: #000000; font-weight: bold } /* Name.Label */
.highlight .no { color: #008080 } /* Name.Constant */
.highlight .sr .re { color: #009900} /* Literal.String.Regex.Register */
.highlight .sr .ch { color: #009900} /* Literal.String.Regex.Char */
.highlight .sr .ke { color: #009900} /* Literal.String.Regex.Keyword */
.highlight .sr .op { color: #009900; font-weight: bold} /* Literal.String.Regex.Operator */
.highlight .sr .tt { color: #009900} /* Literal.String.Regex.Token */
.highlight .sr .dl { color: #009900} /* Literal.String.Regex.Delimiter */
.highlight .sr .cl { color: #009900} /* Literal.String.Regex.Class */
.highlight .sr .co { color: #009900} /* Literal.String.Regex.Composite */
.highlight .sr .cbracket { color: #009900} /* Literal.String.Regex.Character.Set.Bracket */
.highlight .sr .cchar { color: #009900} /* Literal.String.Regex.Character.Set.Char */
.highlight .sr .ccomment { color: #009900} /* Literal.String.Regex.Character.Set.Comment */
.highlight .sr .ccontrol { color: #009900} /* Literal.String.Regex.Character.Set.Control */
.highlight .sr .cescape { color: #009900} /* Literal.String.Regex.Character.Set.Escape */
.highlight .sr .cname { color: #009900} /* Literal.String.Regex.Character.Set.Name */
.highlight .sr .cother { color: #009900} /* Literal.String.Regex.Character.Set.Other */
.highlight .sr .crange { color: #009900} /* Literal.String.Regex.Character.Set.Range */
.highlight .crangecomma { color: #009900} /* Literal.String.Regex.Character.Set.Range.Comma */
.highlight .crangespace { color: #009900} /* Literal.String.Regex.Character.Set.Range.Space */
.highlight .crangestart { color: #009900} /* Literal.String.Regex.Character.Set.Range.Start */
.highlight .cset { color: #009900} /* Literal.String.Regex.Character.Set */
.highlight .cspecial { color: #009900} /* Literal.String.Regex.Character.Set.Special */
.highlight .kt { color: #009900} /* Literal.String.Regex.Keyword.Token */
.highlight .o { color: #009900; font-weight: bold} /* Literal.String.Regex.Operator */
.highlight .p { color: #009900} /* Literal.String.Regex.Parenthesis */
.highlight .s { color: #009900} /* Literal.String.Regex.String */
.highlight .sc { color: #009900} /* Literal.String.Regex.Char */
.highlight .sx { color: #009900} /* Literal.String.Regex.Other */
.highlight .vc { color: #009900} /* Literal.String.Regex.Variable.Class */
.highlight .vg { color: #009900} /* Literal.String.Regex.Variable.Global */
.highlight .vi { color: #009900} /* Literal.String.Regex.Variable.Instance */
.highlight .nv { color: #009900} /* Literal.String.Regex.Variable */
.highlight .nt { color: #000000; font-weight: bold } /* Name.Tag */
.highlight .vg { color: #008080 } /* Name.Variable.Global */
.highlight .vi { color: #008080 } /* Name.Variable.Instance */
.highlight .nv { color: #008080 } /* Name.Variable */
.highlight .ow { color: #000000; font-weight: bold } /* Operator.Word */
.highlight .w { color: #bbbbbb } /* Text.Whitespace */
.highlight .mf { color: #009999 } /* Literal.Number.Float */
.highlight .mh { color: #009999 } /* Literal.Number.Hex */
.highlight .mi { color: #009999 } /* Literal.Number.Integer */
.highlight .mo { color: #009999 } /* Literal.Number.Oct */
.highlight .sb { color: #e37a00 } /* Literal.String.Backtick */
.highlight .sc { color: #e37a00 } /* Literal.String.Char */
.highlight .sd { color: #e37a00; font-style: italic } /* Literal.String.Doc */
.highlight .s2 { color: #e37a00 } /* Literal.String.Double */
.highlight .se { color: #e37a00; font-weight: bold } /* Literal.String.Escape */
.highlight .sh { color: #e37a00 } /* Literal.String.Heredoc */
.highlight .si { color: #e37a00 } /* Literal.String.Interpol */
.highlight .sx { color: #e37a00 } /* Literal.String.Other */
.highlight .sr { color: #009900 } /* Literal.String.Regex */
.highlight .s1 { color: #e37a00 } /* Literal.String.Single */
.highlight .ss { color: #990000 } /* Literal.String.Symbol */
.highlight .nc { color: #000000; font-weight: bold } /* Name.Class */
.highlight .no { color: #008080 } /* Name.Constant */
.highlight .nd { color: #555555 } /* Name.Decorator */
.highlight .ni { color: #800000; font-weight: bold } /* Name.Entity */
.highlight .ne { color: #990000; font-weight: bold } /* Name.Exception */
.highlight .nf { color: #990000; font-weight: bold } /* Name.Function */
.highlight .nl { color: #990000; font-weight: bold } /* Name.Label */
.highlight .nn { color: #555555 } /* Name.Namespace */
.highlight .nt { color: #000080 } /* Name.Tag */
.highlight .vc { color: #008080 } /* Name.Variable.Class */
.highlight .ow { color: #000000; font-weight: bold } /* Operator.Word */
.highlight .st { color: #e37a00 } /* Literal.String.Interpolated */
.highlight .ss .vc { color: #990000} /* Literal.String.Symbol.Variable.Class */
.highlight .ss .vg { color: #990000} /* Literal.String.Symbol.Variable.Global */
.highlight .ss .vi { color: #990000} /* Literal.String.Symbol.Variable.Instance */
.highlight .ss .nv { color: #990000} /* Literal.String.Symbol.Variable */
.highlight .sr .vc { color: #009900} /* Literal.String.Regex.Variable.Class */
.highlight .sr .vg { color: #009900} /* Literal.String.Regex.Variable.Global */
.highlight .sr .vi { color: #009900} /* Literal.String.Regex.Variable.Instance */
.highlight .sr .nv { color: #009900} /* Literal.String.Regex.Variable */
/* --- End Pygments CSS --- */


/* Blockquotes */
blockquote {
    margin: 1em 40px; /* Indent */
    padding: 0.5em 15px;
    border-left: 4px solid #a0aec0; /* Softer grey left border */
    color: #4a5568; /* Slightly muted text */
    font-style: italic;
    background-color: #edf2f7; /* Light background for contrast */
    page-break-inside: avoid; /* Try to keep blockquote on one page */
}

/* Tables */
table {
    border-collapse: collapse; /* No space between borders */
    width: 100%; /* Full width */
    margin-bottom: 1.5em;
    border: 1px solid #e2e8f0; /* Overall table border */
    page-break-inside: avoid; /* Try to keep small tables on one page */
}
th, td {
    border: 1px solid #e2e8f0; /* Light grey borders */
    padding: 12px 10px; /* Increased padding inside cells */
    text-align: left; /* Align text left */
}
th {
    background-color: #f7fafc; /* Very light grey background for headers */
    font-weight: bold;
    color: #2d3748;
}
tbody tr:nth-child(odd) { /* Zebra striping */
    background-color: #edf2f7;
}
/* tbody tr:hover { background-color: #ebf4ff; } /* Hover not relevant for PDF */

/* Images */
img {
    max-width: 100%; /* Ensure images don't overflow containers */
    height: auto; /* Maintain aspect ratio */
    display: block; /* Images on their own line */
    margin: 1.5em auto; /* Center images and add more vertical space */
    border: 1px solid #e2e8f0; /* Optional: subtle border around images */
    padding: 5px; /* Optional: padding inside border */
    background-color: #fff; /* Optional: white background for padding */
}
figure {
     page-break-inside: avoid; /* Try to keep figures/images with captions together */
}

/* Horizontal Rule */
hr {
    border: none;
    border-top: 1px solid #cbd5e0; /* Match H1 border color */
    margin: 3em 0; /* More space above and below rule */
}

/* --- Watermark Style --- */
/* This element is added to the HTML template and positioned using CSS */
/* You can modify text, color, size, rotation here */
/* Note: This uses position: fixed which might not be perfect on all PDF renderers,
         but Playwright generally handles it well for page overlays. */
.watermark {
    position: fixed; /* Position relative to the viewport/page */
    top: 50%; /* Center vertically */
    left: 50%; /* Center horizontally */
    transform: translate(-50%, -50%) rotate(-45deg); /* Adjust for center and rotate */
    font-size: 7em; /* Large text */
    color: rgba(45, 55, 72, 0.1); /* Semi-transparent dark color matching body text base */
    /* Or use a light grey: color: rgba(160, 174, 192, 0.5); */
    pointer-events: none; /* Allow interaction with elements behind the watermark */
    z-index: 9999; /* Ensure it's above other content */
    white-space: nowrap; /* Prevent text from wrapping */
    user-select: none; /* Prevent selecting the watermark text */
    /* Optional: Hide watermark during printing if not desired in final PDF */
    /* @media print { .watermark { display: none; } } */
}


/* --- Print Specific Styles (@page) --- */
@page {
    size: A4; /* Or Letter */
    margin: 2.5cm; /* Default margins: Top, Right, Bottom, Left */

    /* Example Headers/Footers using CSS Generated Content for Paged Media */
    /* Uncomment and modify as needed. Playwright supports these. */

    /* Example Header on the top-left */
    /*
    @top-left {
        content: "Generated Document";
        font-size: 9pt;
        color: #718096;
    }
    */

    /* Example Page Number on the bottom-right footer */
    /*
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #718096;
    }
    */

    /* Example Centered Footer (e.g., Confidentiality note) */
    /*
    @bottom-center {
         content: "Confidential";
         font-size: 9pt;
         color: #a0aec0;
    }
    */

    /* Example Title in top-center */
    /*
    @top-center {
        content: element(doctitle); !* Requires a named element in HTML like <h1 id="doctitle">...</h1> *!
        font-size: 10pt;
        font-weight: bold;
        color: #2d3748;
    }
    */
}

/* Prevent block elements from breaking across pages awkwardly */
/* This is a fallback, page-break-inside is preferred, but break-inside is newer and better */
/* Use avoid-page for break-inside in paged media */
div, pre, blockquote, table, img, figure { break-inside: avoid-page; }


/* --- End Base PDF Styles (Enhanced) --- */
"""

# HTML template with placeholders for BASE_PDF_CSS, custom CSS, and content
# FIX: Ensure both style blocks are used in the template formatting
DEFAULT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        {} /* BASE_PDF_CSS goes here */
    </style>
    <style>
        {} /* Custom CSS goes here - overrides base styles */
    </style>
</head>
<body>
    <div class="watermark">MK</div> <!-- Watermark element -->
{} <!-- Markdown converted to HTML content goes here -->
</body>
</html>
"""

# Configure logging - Use a named logger for better integration
# Assume basicConfig is done in the main app (e.g., app.py)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Use the module name as the logger name


# --- Helper Functions (Internal to the core logic) ---

def convert_markdown_to_html_lib(md_text: str) -> str:
    """Converts Markdown string to HTML string using python-markdown."""
    # Ensure Pygments is installed for codehilite
    try:
        import pygments # Check if pygments can be imported
    except ImportError:
        logger.warning("Pygments not found. Code highlighting will not work. Install with 'pip install Pygments'.")
        extensions = [
            'extra',
            # 'codehilite', # Disable if Pygments is missing
            'fenced_code',
            'tables',
            'nl2br',
            'sane_lists',
            'def_list', # Definition lists
            'attr_list', # {:#id.class} syntax
        ]
    else:
         extensions = [
            'extra',
            'codehilite', # Enable if Pygments is present
            'fenced_code',
            'tables',
            'nl2br',
            'sane_lists',
            'def_list', # Definition lists
            'attr_list', # {:#id.class} syntax
        ]
    logger.debug(f"Using markdown extensions: {extensions}")
    return markdown.markdown(md_text, extensions=extensions)

async def convert_html_to_pdf_playwright(html_string: str, custom_css: str = '', timeout_ms: int = 60000) -> bytes:
    """
    Converts an HTML string to a PDF using Playwright headless browser.
    Includes base styling and optional custom CSS.

    Args:
        html_string: The HTML content string.
        custom_css: An optional string of custom CSS rules to apply.
        timeout_ms: Timeout for Playwright operations (like setting content) in milliseconds.

    Returns:
        The binary content (bytes) of the generated PDF file.

    Raises:
        RuntimeError: If the Playwright conversion fails or times out.
        PlaywrightTimeoutError: Specific timeout error from Playwright (caught by Runtime Error wrapper).
    """
    logger.info("Starting Playwright PDF conversion...")
    # Combine base CSS and custom CSS, then format the template
    full_html = DEFAULT_HTML_TEMPLATE.format(BASE_PDF_CSS, custom_css, html_string)

    browser = None # Initialize browser to None for cleanup in case of error
    try:
        # Use a context manager for playwright to ensure proper cleanup
        async with async_playwright() as p:
            # Launch browser - run headless unless debugging
            browser = await p.chromium.launch(headless=True) # Set headless=False for debugging
            page = await browser.new_page()

            # Set the HTML content and wait for the page to be ready
            # The timeout_ms here controls how long Playwright waits for network idle/DOMContentLoaded
            # Pass timeout to set_content
            await page.set_content(full_html, wait_until='networkidle', timeout=timeout_ms)
            logger.debug(f"HTML content set, waited for network idle for up to {timeout_ms}ms.")

            # Generate PDF with options
            # page.pdf() does NOT take a timeout argument directly.
            pdf_bytes = await page.pdf(
                format='A4',
                print_background=True, # Needed for background colors etc.
                # Use 0 margins and let CSS @page control them
                 margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
                 # Add other options if needed, e.g., scale, displayHeaderFooter, headerTemplate, footerTemplate
                 # The timeout for PDF generation itself is not a direct argument here.
                 # The page readiness is already waited for by set_content.
            )

            logger.info("Playwright PDF conversion successful.")
            return pdf_bytes
    except PlaywrightTimeoutError as e: # Catch Playwright's specific timeout error
        logger.error(f"Playwright operation timed out after {timeout_ms/1000} seconds: {e}", exc_info=True)
        raise RuntimeError(f"Playwright operation timed out.") from e # Chain the original exception
    except Exception as e:
        logger.error(f"Error during Playwright PDF conversion: {e}", exc_info=True)
        raise RuntimeError(f"Playwright PDF conversion failed: {e}") from e
    finally:
        # Ensure browser is closed even if conversion fails
        if browser:
            try:
                await browser.close()
                logger.debug("Playwright browser closed.")
            except Exception as close_err:
                logger.error(f"Error closing Playwright browser: {close_err}")


def convert_markdown_to_docx_pandoc(md_text: str, reference_docx: str = None, pandoc_timeout_sec: int = 60) -> bytes:
    """
    Converts Markdown string to DOCX using Pandoc subprocess.
    Optionally uses a reference DOCX for styling.
    This function is INTENTIONALLY SYNCHRONOUS. It should be called
    from an async context using asyncio.to_thread or similar.

    Args:
        md_text: The input Markdown string.
        reference_docx: Path to an optional reference DOCX file.
        pandoc_timeout_sec: Timeout for the Pandoc subprocess in seconds.

    Returns:
        The binary content (bytes) of the generated DOCX file.

    Raises:
        FileNotFoundError: If the pandoc executable is not found or reference_docx is specified but not found.
        subprocess.CalledProcessError: If pandoc returns a non-zero exit code.
        subprocess.TimeoutExpired: If pandoc times out.
        RuntimeError: For other unexpected errors or configuration issues.
    """
    # Read Pandoc path from environment variable *inside* the synchronous function
    pandoc_custom_path = os.environ.get(PANDOC_PATH_ENV_VAR)

    # Determine the Pandoc command (either PANDOC_PATH_ENV_VAR or just 'pandoc')
    pandoc_command = [pandoc_custom_path] if pandoc_custom_path else ['pandoc']

    # Check if the specified Pandoc path exists if it was explicitly set via ENV
    if pandoc_custom_path and not os.path.exists(pandoc_custom_path):
         raise RuntimeError(f"Configured Pandoc executable not found at {pandoc_custom_path} (from {PANDOC_PATH_ENV_VAR} environment variable). "
                           "Please install Pandoc or update the environment variable.")

    # Check if the reference_docx exists if provided
    if reference_docx and not os.path.exists(reference_docx):
         raise FileNotFoundError(f"Reference DOCX file not found: {reference_docx}")


    # Use tempfile for safety and cleanup
    tmp_md_path = None
    output_path = None
    try:
        # Create temporary input markdown file
        with tempfile.NamedTemporaryFile(mode='w+', suffix=".md", encoding='utf-8', delete=False) as tmp_md:
            tmp_md.write(md_text)
            tmp_md_path = tmp_md.name
            logger.debug(f"Created temporary markdown file: {tmp_md_path}")

        # Create a temporary output file explicitly
        with tempfile.NamedTemporaryFile(mode='wb', suffix=".docx", delete=False) as tmp_docx:
             output_path = tmp_docx.name
        logger.debug(f"Created temporary output docx path: {output_path}")

        # Build the Pandoc command
        command = pandoc_command + [
            '--from', 'markdown+autolink_bare_uris+pipe_tables+grid_tables+yaml_metadata_block', # Enhance Markdown parsing
            '--to', 'docx',
            '--output', output_path,
            tmp_md_path
        ]

        # Add reference-docx if provided
        if reference_docx:
             command.extend(['--reference-docx', reference_docx])
             logger.info(f"Using reference DOCX for styling: {reference_docx}")
        else:
             # Log that we're not using a reference if none was provided or found
             logger.debug("No explicit reference DOCX provided or found. Using Pandoc default styling.")


        # Log the command carefully, especially in production, to avoid exposing sensitive paths if any were included
        logger.debug(f"Running Pandoc command: {' '.join(command)}")
        logger.info("Executing Pandoc conversion...")

        # Run subprocess with timeout
        # This is the blocking call that needs to be run in a separate thread
        result = subprocess.run(
            command,
            check=True,          # Raise CalledProcessError if exit code is non-zero
            capture_output=True, # Capture stdout and stderr
            text=True,           # Decode stdout/stderr as text (utf-8)
            timeout=pandoc_timeout_sec # Set timeout
        )
        logger.info("Pandoc conversion successful.")
        logger.debug("Pandoc stdout:\n" + result.stdout)
        if result.stderr:
            # Treat stderr warnings/info from pandoc as debug/info unless check=True failed
            logger.info("Pandoc stderr:\n" + result.stderr)


        # Read the generated docx file bytes
        with open(output_path, 'rb') as f:
            docx_bytes = f.read()

        return docx_bytes

    except FileNotFoundError:
        # This specific error implies the pandoc executable wasn't found or a file path was wrong
        # Re-raise with a clearer message including the command attempted
        error_msg = (f"Pandoc executable '{pandoc_command[0]}' not found, or input/reference file path error. "
                     "Is Pandoc installed and in your system's PATH? "
                     f"Or is the {PANDOC_PATH_ENV_VAR} environment variable set correctly? "
                     f"Attempted command: {' '.join(pandoc_command)}")
        logger.error(error_msg, exc_info=True)
        raise FileNotFoundError(error_msg) from None # Raise from None to avoid chaining
    except subprocess.TimeoutExpired as e:
         error_msg = f"Pandoc conversion timed out after {pandoc_timeout_sec} seconds. Command: {' '.join(e.cmd)}"
         logger.error(error_msg, exc_info=True)
         raise RuntimeError(error_msg) from e
    except subprocess.CalledProcessError as e:
        error_output = f"Pandoc conversion failed. Command: {' '.join(e.cmd)}\n"
        error_output += f"Return Code: {e.returncode}\n"
        error_output += f"Stdout:\n{e.stdout}\n"
        error_output += f"Stderr:\n{e.stderr}\n"
        logger.error(error_output, exc_info=True)
        raise RuntimeError(f"Pandoc conversion failed: See details in logs.") from e
    except Exception as e:
        logger.error(f"An unexpected error occurred during DOCX conversion: {e}", exc_info=True)
        raise RuntimeError(f"An unexpected error occurred during DOCX conversion: {e}") from e
    finally:
        # Clean up the temporary markdown file and the output docx file
        if tmp_md_path and os.path.exists(tmp_md_path):
            try:
                os.remove(tmp_md_path)
                logger.debug(f"Cleaned up temporary markdown file: {tmp_md_path}")
            except OSError as e:
                 logger.warning(f"Could not remove temporary markdown file {tmp_md_path}: {e}")

        if output_path and os.path.exists(output_path):
             try:
                 os.remove(output_path)
                 logger.debug(f"Cleaned up temporary docx file: {output_path}")
             except OSError as e:
                 logger.warning(f"Could not remove temporary docx file {output_path}: {e}")


# --- Main Conversion Entry Point (String -> Bytes) ---

async def convert_markdown(md_text: str, output_format: str, **kwargs) -> bytes:
    """
    Converts Markdown text to the specified output format (PDF or DOCX).

    Args:
        md_text: The input Markdown string.
        output_format: The desired output format ('pdf' or 'docx').
        **kwargs: Additional arguments passed to specific converters
                  (e.g., custom_css for pdf, reference_docx for docx,
                   timeout_ms for playwright, pandoc_timeout_sec for pandoc).

    Returns:
        The binary content (bytes) of the generated file.

    Raises:
        ValueError: If the input is empty/whitespace or format is unsupported.
        RuntimeError: If a conversion tool fails.
        FileNotFoundError: If required external executable (pandoc) or file (reference_docx) is not found.
        IOError: If there's a problem with temporary file handling.
    """
    if not isinstance(md_text, str):
         raise ValueError("Input md_text must be a string.")

    # Check for empty or whitespace-only input
    if not md_text or not md_text.strip():
         logger.warning("Empty or whitespace-only markdown text provided.")
         raise ValueError("Input markdown text is empty or contains only whitespace. No content to convert.")

    output_format = output_format.lower()
    logger.info(f"Initiating conversion for format: {output_format}")

    try:
        if output_format == 'pdf':
            logger.info("Starting PDF conversion (via Playwright)...")
            # Convert Markdown to HTML first
            html_content = convert_markdown_to_html_lib(md_text)
            # Then convert HTML to PDF using Playwright
            custom_css = kwargs.get('custom_css', '') # Get custom_css from kwargs
            playwright_timeout = kwargs.get('timeout_ms', 60000)
            logger.debug(f"Passing custom CSS of length: {len(custom_css)}, Playwright timeout: {playwright_timeout}ms")
            file_bytes = await convert_html_to_pdf_playwright(
                html_content,
                custom_css=custom_css,
                timeout_ms=playwright_timeout # Pass timeout to Playwright function
            )
            logger.info("PDF conversion finished.")
            return file_bytes
        elif output_format == 'docx':
            logger.info("Starting DOCX conversion (via Pandoc)...")
            # Convert Markdown directly to DOCX using Pandoc
            # reference_docx should come from kwargs (potentially from API's server-side config)
            reference_docx = kwargs.get('reference_docx')
            pandoc_timeout = kwargs.get('pandoc_timeout_sec', 60)
            logger.debug(f"DOCX conversion, reference_docx: {reference_docx}, Pandoc timeout: {pandoc_timeout}s")

            # Call the synchronous convert_markdown_to_docx_pandoc in a separate thread
            file_bytes = await asyncio.to_thread(
                convert_markdown_to_docx_pandoc,
                md_text,
                reference_docx=reference_docx,
                pandoc_timeout_sec=pandoc_timeout # Pass timeout to Pandoc function
            )
            logger.info("DOCX conversion finished.")
            return file_bytes
        else:
            raise ValueError(f"Unsupported output format: {output_format}. Choose 'pdf' or 'docx'.")

    except (ValueError, RuntimeError, FileNotFoundError, IOError) as e:
         # Re-raise specific anticipated errors that the caller might want to catch
         raise e
    except Exception as e:
        # Catch any unexpected errors during the conversion process itself
        logger.error(f"An unexpected error occurred during conversion: {e}", exc_info=True)
        # Wrap unexpected errors in a generic RuntimeError for the public interface
        raise RuntimeError(f"An unexpected error occurred during conversion: {e}") from e


# --- Helper Functions (File -> File) ---
# These functions wrap the core convert_markdown for convenience


async def convert_file_to_pdf(
    input_path: str,
    output_path: str,
    custom_css: str = '',
    **kwargs
) -> None:
    """
    Converts a Markdown file to PDF using the package's core logic.

    Args:
        input_path: Path to the input Markdown file.
        output_path: Path where the output PDF file will be saved.
        custom_css: Optional custom CSS string for the PDF.
        **kwargs: Additional arguments passed to the core convert_markdown function.

    Raises:
        FileNotFoundError: If the input file is not found.
        IOError: If reading the input file or writing the output file fails.
        ValueError: If markdown content is empty or format is unsupported.
        RuntimeError: If the conversion tool fails.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info(f"Converting Markdown file '{input_path}' to PDF file '{output_path}'")

    # Read markdown from the input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
    except Exception as e:
        raise IOError(f"Failed to read input markdown file '{input_path}': {e}") from e

    # Use the core conversion function
    # Ensure custom_css arg is passed correctly (overrides if also in kwargs)
    kwargs['custom_css'] = custom_css
    pdf_bytes = await convert_markdown(md_text, 'pdf', **kwargs)

    # Write bytes to the output file
    try:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"Successfully saved PDF to '{output_path}'")
    except Exception as e:
        raise IOError(f"Failed to write output PDF file '{output_path}': {e}") from e


async def convert_file_to_docx(
    input_path: str,
    output_path: str,
    reference_docx: str = None,
    **kwargs
) -> None:
    """
    Converts a Markdown file to DOCX using the package's core logic (Pandoc).

    Args:
        input_path: Path to the input Markdown file.
        output_path: Path where the output DOCX file will be saved.
        reference_docx: Optional path to a reference DOCX file for styling.
                        If not provided, the REFERENCE_DOCX_PATH env var is checked
                        *by the underlying pandoc function*.
        **kwargs: Additional arguments passed to the core convert_markdown function.

    Raises:
        FileNotFoundError: If the input file is not found or reference_docx is specified but not found.
        IOError: If reading the input file or writing the output file fails.
        ValueError: If markdown content is empty or format is unsupported.
        RuntimeError: If the conversion tool (Pandoc) fails.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Check if reference_docx exists if provided explicitly to this helper
    # The underlying convert_markdown_to_docx_pandoc also checks, but checking here
    # gives a more specific error message tied to *this* helper's arguments.
    if reference_docx and not os.path.exists(reference_docx):
        raise FileNotFoundError(f"Reference DOCX file not found: {reference_docx}")


    logger.info(f"Converting Markdown file '{input_path}' to DOCX file '{output_path}'")

    # Read markdown from the input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
    except Exception as e:
        raise IOError(f"Failed to read input markdown file '{input_path}': {e}") from e

    # Use the core conversion function
    # Ensure reference_docx arg is passed correctly (overrides if also in kwargs)
    kwargs['reference_docx'] = reference_docx
    # Await convert_markdown which is now async for DOCX via asyncio.to_thread
    docx_bytes = await convert_markdown(md_text, 'docx', **kwargs)

    # Write bytes to the output file
    try:
        with open(output_path, 'wb') as f:
            f.write(docx_bytes)
        logger.info(f"Successfully saved DOCX to '{output_path}'")
    except Exception as e:
        raise IOError(f"Failed to write output DOCX file '{output_path}': {e}") from e
