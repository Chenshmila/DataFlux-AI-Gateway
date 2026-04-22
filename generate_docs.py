"""
generate_docs.py — Generates the Hebrew technical documentation PDF for the
ScreenStop MCP project.

Usage:
    python generate_docs.py
Outputs:
    ScreenStop_Technical_Documentation.pdf
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

# DejaVu Sans covers both Hebrew and Latin glyphs (verified).
# DejaVu Sans Mono is ASCII-only — used only for code blocks (all-English).
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO    = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

OUTPUT_FILE  = "ScreenStop_Technical_Documentation.pdf"

# ---------------------------------------------------------------------------
# RTL helper — reverses paragraphs so fpdf renders Hebrew correctly
# ---------------------------------------------------------------------------

def rtl(text: str) -> str:
    """Return a visually correct RTL string for fpdf (which renders LTR)."""
    lines = text.split("\n")
    return "\n".join(line[::-1] for line in lines)


# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------

class DocPDF(FPDF):
    def header(self):
        self.set_font("Main", "B", 10)
        self.set_text_color(80, 80, 80)
        header = rtl("תיעוד טכני — ScreenStop MCP Gateway")
        self.cell(0, 8, header, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Main", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"{self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    # ------------------------------------------------------------------ #
    # Convenience writers                                                  #
    # ------------------------------------------------------------------ #

    def h1(self, text: str):
        self.ln(6)
        self.set_font("Main", "B", 18)
        self.set_fill_color(30, 60, 114)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, rtl(text), fill=True, align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def h2(self, text: str):
        self.ln(5)
        self.set_font("Main", "B", 14)
        self.set_text_color(30, 60, 114)
        self.cell(0, 9, rtl(text), align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(30, 60, 114)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def h3(self, text: str):
        self.ln(4)
        self.set_font("Main", "B", 12)
        self.set_text_color(50, 90, 160)
        self.cell(0, 8, rtl(text), align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)

    def body(self, text: str, size: int = 11):
        self.set_font("Main", "", size)
        for line in text.strip().split("\n"):
            self.multi_cell(0, 7, rtl(line), align="R",
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def bullet(self, text: str):
        self.set_font("Main", "", 11)
        for line in text.strip().split("\n"):
            if not line.strip():
                self.ln(2)
                continue
            self.multi_cell(0, 7, rtl(f"• {line.strip()}"), align="R",
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def code_block(self, text: str):
        """Render a code block with a light grey background.
        Uses Mono font for pure-ASCII content, Main font for text containing Hebrew."""
        has_hebrew = any("\u0590" <= ch <= "\u05FF" for ch in text)
        font = "Main" if has_hebrew else "Mono"
        self.set_font(font, "", 9)
        self.set_fill_color(240, 240, 245)
        self.set_draw_color(200, 200, 210)
        y = self.get_y()
        self.rect(self.l_margin, y, self.w - self.l_margin - self.r_margin,
                  len(text.strip().split("\n")) * 5 + 6, style="FD")
        self.set_y(y + 3)
        for line in text.strip().split("\n"):
            self.set_x(self.l_margin + 3)
            self.cell(0, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_draw_color(0, 0, 0)

    def table_row(self, cols: list[str], bold: bool = False, fill: bool = False):
        style = "B" if bold else ""
        self.set_font("Main", style, 10)
        if fill:
            self.set_fill_color(220, 230, 245)
        col_w = (self.w - self.l_margin - self.r_margin) / len(cols)
        for i, col in enumerate(cols):
            align = "R" if i == len(cols) - 1 else "L"
            self.cell(col_w, 8, rtl(col) if align == "R" else col,
                      border=1, align=align, fill=fill,
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(8)


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

def build(pdf: DocPDF):

    # ═══════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Main", "B", 28)
    pdf.set_text_color(30, 60, 114)
    pdf.cell(0, 14, rtl("תיעוד טכני מקצועי"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_font("Main", "B", 20)
    pdf.cell(0, 12, "ScreenStop MCP Gateway", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    pdf.set_font("Main", "", 13)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, rtl("ארכיטקטורת סוכן–שער–קטלוג מבוססת פרוטוקול MCP"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(20)
    pdf.set_draw_color(30, 60, 114)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin + 30, pdf.get_y(), pdf.w - pdf.r_margin - 30, pdf.get_y())
    pdf.ln(20)
    pdf.set_font("Main", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, rtl("גרסה 1.0  |  אפריל 2026"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.set_line_width(0.2)

    # ═══════════════════════════════════════════════════════════════════════
    # 1. PROJECT OVERVIEW
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("1. סקירת הפרויקט")

    pdf.h2("1.1 מטרת הפרויקט")
    pdf.body(
        "פרויקט ScreenStop MCP Gateway הוא מימוש עיון מינימלי ומוכן לייצור של שער AI\n"
        "מבוסס על פרוטוקול Model Context Protocol (MCP). המטרה היא לאפשר לסוכן\n"
        "שיחותי (Claude) לגשת לקטלוג מוצרים של חברת ScreenStop ולנהל שיחות מכירה\n"
        "עם לקוחות — הכל תוך שמירה על הפרדה ברורה בין שכבת הבינה המלאכותית\n"
        "לבין שכבת הנתונים."
    )

    pdf.h2("1.2 ארכיטקטורת הליבה: סוכן–שער–קטלוג")
    pdf.body(
        "המערכת בנויה משלוש שכבות לוגיות המתקשרות בזו אחר זו:"
    )
    pdf.bullet(
        "שכבת הסוכן (agent.py) — ממשק המשתמש וה-loop האגנטי. מנהלת את\n"
        "   השיחה עם המשתמש, שולחת בקשות ל-Claude, ומתרגמת תוצאות כלים\n"
        "   לתשובות טקסטואליות.\n"
        "שכבת השער (agent_store.py) — שרת MCP המשמש כ-gateway לקטלוג.\n"
        "   חושף כלים מוגדרים בצורה מובנית ומאמת כל בקשה מול מפתח פנימי.\n"
        "שכבת הקטלוג (CATALOG dict) — מקור האמת היחיד לנתוני המוצרים.\n"
        "   מוגדר בתוך agent_store.py ומוגש אך ורק דרך הכלים הרשמיים."
    )

    pdf.h2("1.3 דיאגרמת זרימה")
    pdf.code_block(
        "  המשתמש\n"
        "     |\n"
        "     v\n"
        " agent.py  <-->  Claude API (claude-sonnet-4-6)\n"
        "     |\n"
        "     | stdio (MCP protocol)\n"
        "     v\n"
        " agent_store.py  (FastMCP server)\n"
        "     |\n"
        "     v\n"
        " CATALOG dict  (single source of truth)"
    )

    pdf.h2("1.4 עקרונות עיצוב")
    pdf.bullet(
        "הפרדת אחריות — כל שכבה אחראית על תחום אחד בלבד.\n"
        "גילוי דינמי — הסוכן מגלה כלים בזמן ריצה, ללא hardcoding.\n"
        "אבטחה מובנית — אימות מפתח משותף בכל קריאת כלי.\n"
        "ניפוי שגיאות מבוקר — DEBUG mode מאפשר לוג מלא ללא שינוי קוד.\n"
        "חוויה נקייה — המשתמש רואה רק את תשובת הסוכן, לא תהליכים פנימיים."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 2. FILE HIERARCHY
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("2. היררכיית הקבצים")

    pdf.h2("2.1 מפת הפרויקט")
    pdf.code_block(
        "screenstop-assignment/\n"
        "  agent.py            # סוכן הלקוח — לולאה אגנטית + ממשק CLI\n"
        "  agent_store.py      # שרת MCP — שער הקטלוג\n"
        "  system_prompt.md    # פרסונת האלכס + חוקי שיחה\n"
        "  README.md           # תיעוד + הוראות הפעלה\n"
        "  requirements.txt    # תלויות Python\n"
        "  generate_docs.py    # סקריפט יצירת ה-PDF הזה"
    )

    pdf.h2("2.2 agent.py — סוכן הלקוח")
    pdf.body(
        "agent.py הוא נקודת הכניסה למערכת מבחינת המשתמש. הוא:\n"
        "מאתחל חיבור MCP לשרת agent_store.py דרך stdio.\n"
        "מגלה את הכלים הזמינים ומתרגם אותם לפורמט Anthropic.\n"
        "מריץ לולאה אגנטית — שולח הודעות ל-Claude, מעבד קריאות כלים,\n"
        "ומחזיר את התשובה הסופית למשתמש."
    )

    pdf.h2("2.3 agent_store.py — שרת MCP")
    pdf.body(
        "agent_store.py הוא לב המערכת מבחינת הנתונים. הוא:\n"
        "מגדיר את קטלוג המוצרים כ-dict Python — מקור האמת היחיד.\n"
        "חושף שני כלים רשמיים: get_catalog ו-search_products.\n"
        "מאמת מפתח פנימי (SCREENSTOP_INTERNAL_KEY) בתחילת כל קריאת כלי.\n"
        "רץ כתת-תהליך stdio — מתקשר עם agent.py דרך פרוטוקול MCP."
    )

    pdf.h2("2.4 system_prompt.md — פרסונת הסוכן")
    pdf.body(
        "system_prompt.md מגדיר את אלכס — המומחה המקצועי של ScreenStop.\n"
        "הקובץ כולל:\n"
        "הוראות שפה: זיהוי שפת המשתמש ותגובה בשפתו (עברית/אנגלית).\n"
        "זרימת שיחה: 6 שלבים מהברכה ועד לסגירת המכירה.\n"
        "טיפול בקצה: הנחיות מפורשות לתרחישים כמו 'אין תוצאות'.\n"
        "כללי ברזל: מה שאלכס לעולם לא יעשה (לא יספר מחיר ללא כלי וכו')."
    )

    pdf.h2("2.5 README.md — תיעוד ופעולה")
    pdf.body(
        "README.md מיועד לגורם שמרים את הפרויקט לראשונה. הוא כולל:\n"
        "ארכיטקטורה ויזואלית בתבנית ASCII.\n"
        "הסבר מעמיק על MCP לעומת REST API.\n"
        "הוראות Setup מלאות כולל משתני הסביבה הנדרשים.\n"
        "פרק Bonuses המתאר את מנגנון האימות וה-Smart Search."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 3. LINE-BY-LINE: agent.py
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("3. פירוט שורה-אחר-שורה: agent.py")

    # --- imports ---
    pdf.h2("3.1 ייבוא ספריות")
    pdf.code_block(
        "import asyncio\n"
        "import json\n"
        "import logging\n"
        "import os\n"
        "import sys\n"
        "from pathlib import Path"
    )
    pdf.bullet(
        "asyncio — מאפשר תכנות אסינכרוני; נדרש כי MCP client הוא coroutine-based.\n"
        "json — דרוש להמרת ארגומנטים של כלים לפורמט טקסט לצורך לוג.\n"
        "logging — ניהול רמות לוג; משמש לדחיקת הודעות INFO של ספריית mcp.\n"
        "os — גישה למשתני סביבה (API key, internal key, DEBUG flag).\n"
        "sys — גישה ל-sys.executable (נתיב Python הנוכחי) ול-sys.stderr.\n"
        "pathlib.Path — ניתוב קובץ system_prompt.md בצורה רובוסטית ובלתי\n"
        "   תלויה במערכת הפעלה."
    )

    pdf.code_block(
        "import anthropic\n"
        "from mcp import ClientSession, StdioServerParameters\n"
        "from mcp.client.stdio import stdio_client"
    )
    pdf.bullet(
        "anthropic — SDK רשמי של Anthropic; מספק גישה ל-Claude API.\n"
        "ClientSession — מנהל את החיבור ל-MCP server לאחר האתחול.\n"
        "StdioServerParameters — הגדרות הפעלת שרת MCP דרך stdio.\n"
        "stdio_client — Context manager שפותח תהליך-בן ומנהל pipes."
    )

    # --- debug mode ---
    pdf.h2("3.2 הגדרת DEBUG Mode")
    pdf.code_block(
        "DEBUG = os.environ.get(\"DEBUG\", \"\").lower() == \"true\"\n"
        "\n"
        "def _debug(*args, **kwargs) -> None:\n"
        "    if DEBUG:\n"
        "        print(*args, **kwargs)\n"
        "\n"
        "logging.getLogger(\"mcp\").setLevel(logging.DEBUG if DEBUG else logging.WARNING)"
    )
    pdf.bullet(
        "DEBUG — boolean הנקרא ממשתנה הסביבה DEBUG. ברירת מחדל: False.\n"
        "_debug() — wrapper לפונקציית print. פלט מוצג רק אם DEBUG=true.\n"
        "   עוטף את כל הלוג הפנימי: קריאות כלים ותוצאות.\n"
        "logging.getLogger('mcp') — ספריית mcp משתמשת ב-Python logging.\n"
        "   ללא הגדרה זו היא מדפיסה הודעות INFO כגון\n"
        "   'Processing request of type ListToolsRequest' — רעש לא רצוי."
    )

    # --- system prompt ---
    pdf.h2("3.3 טעינת System Prompt")
    pdf.code_block(
        "_PROMPT_FILE = Path(__file__).parent / \"system_prompt.md\"\n"
        "SYSTEM_PROMPT = _PROMPT_FILE.read_text(encoding=\"utf-8\")"
    )
    pdf.bullet(
        "Path(__file__).parent — תיקיית הקובץ הנוכחי; עמיד לשינויי working dir.\n"
        "/ 'system_prompt.md' — operator / של pathlib מחבר נתיבים בצורה בטוחה.\n"
        "read_text(encoding='utf-8') — קריאת הקובץ כמחרוזת Unicode.\n"
        "SYSTEM_PROMPT קבוע גלובלי — נטען פעם אחת בהפעלה, לא בכל פנייה."
    )

    # --- _mcp_tool_to_anthropic ---
    pdf.h2("3.4 פונקציה: _mcp_tool_to_anthropic()")
    pdf.code_block(
        "def _mcp_tool_to_anthropic(tool) -> dict:\n"
        "    return {\n"
        "        \"name\": tool.name,\n"
        "        \"description\": tool.description or \"\",\n"
        "        \"input_schema\": tool.inputSchema,\n"
        "    }"
    )
    pdf.bullet(
        "מקבלת אובייקט Tool של ספריית mcp ומחזירה dict תואם ל-Anthropic API.\n"
        "name — שם הכלי שבו Claude ישתמש בקריאות tool_use.\n"
        "description — תיאור טקסטואלי שבו Claude מחליט מתי לקרוא לכלי.\n"
        "input_schema — JSON Schema המגדיר את הפרמטרים המקובלים.\n"
        "   Claude משתמש בסכמה זו כדי לבנות ארגומנטים תקינים בצורה אוטומטית."
    )

    # --- _call_mcp_tool ---
    pdf.h2("3.5 פונקציה: _call_mcp_tool()")
    pdf.code_block(
        "async def _call_mcp_tool(session, name, arguments) -> str:\n"
        "    result = await session.call_tool(name, arguments=arguments)\n"
        "    parts = []\n"
        "    for block in result.content:\n"
        "        if hasattr(block, \"text\"):\n"
        "            parts.append(block.text)\n"
        "        else:\n"
        "            parts.append(str(block))\n"
        "    return \"\\n\".join(parts) if parts else \"(empty result)\""
    )
    pdf.bullet(
        "async — הפונקציה ממתינה לתשובת השרת ללא חסימת ה-event loop.\n"
        "session.call_tool() — שולחת בקשה לשרת MCP ומחכה לתוצאה.\n"
        "result.content — רשימת content blocks; MCP תומך בסוגים מרובים.\n"
        "hasattr(block, 'text') — בדיקה בטוחה: לא כל block הוא TextContent.\n"
        "str(block) — fallback לבלוקים לא-טקסטואליים (תמונות, קבצים וכו').\n"
        "join(parts) — איחוד כל הבלוקים לטקסט אחד רציף.\n"
        "'(empty result)' — ערך ברירת מחדל בטוח כאשר השרת לא מחזיר תוכן."
    )

    # --- run_agent ---
    pdf.add_page()
    pdf.h2("3.6 פונקציה: run_agent() — הלולאה האגנטית")
    pdf.code_block(
        "async def run_agent(user_message, session, client) -> str:\n"
        "    mcp_tools = (await session.list_tools()).tools\n"
        "    anthropic_tools = [_mcp_tool_to_anthropic(t) for t in mcp_tools]\n"
        "    messages = [{\"role\": \"user\", \"content\": user_message}]\n"
        "\n"
        "    while True:\n"
        "        response = client.messages.create(\n"
        "            model=\"claude-sonnet-4-6\",\n"
        "            max_tokens=1024,\n"
        "            system=SYSTEM_PROMPT,\n"
        "            tools=anthropic_tools,\n"
        "            messages=messages,\n"
        "        )\n"
        "        messages.append({\"role\": \"assistant\", \"content\": response.content})\n"
        "\n"
        "        if response.stop_reason == \"end_turn\":\n"
        "            for block in response.content:\n"
        "                if hasattr(block, \"text\"):\n"
        "                    return block.text\n"
        "            return \"(no text response)\"\n"
        "\n"
        "        if response.stop_reason != \"tool_use\":\n"
        "            return f\"(unexpected stop reason: {response.stop_reason})\"\n"
        "\n"
        "        tool_results = []\n"
        "        for block in response.content:\n"
        "            if block.type != \"tool_use\":\n"
        "                continue\n"
        "            _debug(f\"  [tool call] {block.name}(...)\")\n"
        "            result_text = await _call_mcp_tool(session, block.name, block.input)\n"
        "            _debug(f\"  [tool result] {result_text[:120]}\")\n"
        "            tool_results.append({\n"
        "                \"type\": \"tool_result\",\n"
        "                \"tool_use_id\": block.id,\n"
        "                \"content\": result_text,\n"
        "            })\n"
        "        messages.append({\"role\": \"user\", \"content\": tool_results})"
    )

    pdf.h3("פירוט שורה-אחר-שורה:")
    pdf.bullet(
        "session.list_tools() — בקשה חד-פעמית לשרת לקבל רשימת כלים.\n"
        "   list comprehension הופכת כל כלי MCP לפורמט Anthropic.\n"
        "messages list — היסטוריית השיחה; מתחילה עם הודעת המשתמש.\n"
        "while True — הלולאה רצה עד ש-Claude מחזיר end_turn.\n"
        "client.messages.create() — קריאה ל-Claude API עם:\n"
        "   model: claude-sonnet-4-6 — המודל העדכני והחזק ביותר.\n"
        "   max_tokens: 1024 — מגביל אורך תשובה למניעת בזבוז.\n"
        "   system: SYSTEM_PROMPT — הפרסונה ואלכס והחוקים.\n"
        "   tools: anthropic_tools — רשימת הכלים שClaude יכול לקרוא.\n"
        "   messages: היסטוריית השיחה המלאה עד לנקודה זו.\n"
        "messages.append(assistant) — שמירת תגובת Claude לצורך context.\n"
        "stop_reason == 'end_turn' — Claude סיים לחשוב; מחזירים תשובה.\n"
        "stop_reason != 'tool_use' — מצב בלתי צפוי; מחזירים שגיאה מוגנת.\n"
        "for block in response.content — עיבוד כל קריאות הכלים בתור.\n"
        "block.type != 'tool_use' — דילוג על בלוקי טקסט (חשיבה פנימית).\n"
        "_debug() — הדפסה מותנית; נסתרת מהמשתמש ב-production.\n"
        "tool_result dict — מבנה נדרש על-ידי Anthropic API לתשובות כלים.\n"
        "tool_use_id — מזהה ייחודי שמקשר כל תוצאה לקריאת הכלי שלה.\n"
        "messages.append(user+results) — הזנת תוצאות הכלים חזרה ל-Claude."
    )

    # --- main ---
    pdf.h2("3.7 פונקציה: main() — ממשק ה-CLI")
    pdf.code_block(
        "async def main() -> None:\n"
        "    if not os.environ.get(\"ANTHROPIC_API_KEY\"):\n"
        "        print(\"Error: ANTHROPIC_API_KEY is not set.\", file=sys.stderr)\n"
        "        sys.exit(1)\n"
        "\n"
        "    internal_key = os.environ.get(\"SCREENSTOP_INTERNAL_KEY\", \"\")\n"
        "    if not internal_key:\n"
        "        print(\"Error: SCREENSTOP_INTERNAL_KEY is not set.\", file=sys.stderr)\n"
        "        sys.exit(1)\n"
        "\n"
        "    server_params = StdioServerParameters(\n"
        "        command=sys.executable,\n"
        "        args=[str(Path(__file__).parent / \"agent_store.py\")],\n"
        "        env={**os.environ, \"SCREENSTOP_INTERNAL_KEY\": internal_key},\n"
        "    )\n"
        "    client = anthropic.Anthropic()\n"
        "\n"
        "    async with stdio_client(server_params) as (read, write):\n"
        "        async with ClientSession(read, write) as session:\n"
        "            await session.initialize()\n"
        "            tools = (await session.list_tools()).tools\n"
        "            _debug(f\"Tools: {[t.name for t in tools]}\")\n"
        "            print(\"Welcome to ScreenStop. Type your question (or 'quit').\\n\")\n"
        "\n"
        "            while True:\n"
        "                user_input = input(\"You: \").strip()\n"
        "                if not user_input: continue\n"
        "                if user_input.lower() in {\"quit\",\"exit\",\"q\"}: break\n"
        "                answer = await run_agent(user_input, session, client)\n"
        "                print(f\"\\nAlex: {answer}\\n\")"
    )
    pdf.bullet(
        "בדיקות משתני סביבה בתחילת ריצה — fail-fast ברורה לפני כל פעולה.\n"
        "sys.exit(1) — קוד יציאה שגיאה; מאפשר לסביבות CI לזהות כישלון.\n"
        "sys.executable — מבטיח שתת-התהליך ירוץ עם אותו Python interpreter.\n"
        "env={**os.environ, ...} — העתקת כל סביבת ההורה + הוספת המפתח.\n"
        "   חיוני: stdio_client אינו מעביר את סביבת ההורה אוטומטית.\n"
        "anthropic.Anthropic() — לקוח API; קורא ANTHROPIC_API_KEY מהסביבה.\n"
        "async with stdio_client — פותח ומנהל pipes לתת-התהליך.\n"
        "async with ClientSession — מנהל פרוטוקול MCP (handshake, cleanup).\n"
        "session.initialize() — ביצוע MCP handshake; חובה לפני list_tools.\n"
        "_debug(tools) — מציג כלים זמינים רק ב-DEBUG mode.\n"
        "לולאת input — ממתינה לקלט המשתמש; EOFError / KeyboardInterrupt נתפסים."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 4. DESIGN DECISIONS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("4. החלטות עיצוב")

    pdf.h2("4.1 MCP לעומת REST API — למה MCP?")

    pdf.body("השוואה מפורטת:")
    pdf.ln(2)
    pdf.table_row(["REST API מסורתי", "MCP", "היבט"], bold=True, fill=True)
    pdf.table_row(["hardcoded בסוכן", "דינמי — שרת מפרסם כלים", "גילוי כלים"])
    pdf.table_row(["תיעוד אנושי", "JSON Schema מובנה", "סכמת קלט"])
    pdf.table_row(["HTTP בלבד", "stdio, SSE, WebSocket", "transport"])
    pdf.table_row(["תיאום ידני", "פרוטוקול אחיד", "ריבוי שרתים"])
    pdf.table_row(["ידני", "MCP מאמת קלט", "validation"])

    pdf.ln(3)
    pdf.body(
        "הסיבה העיקרית לבחירה ב-MCP היא גילוי דינמי:\n"
        "כאשר agent.py מתחבר ל-agent_store.py, הפעולה הראשונה היא list_tools().\n"
        "השרת מחזיר שם, תיאור וסכמה מלאה של כל כלי — Claude מקבל את כל\n"
        "המידע הדרוש לו כדי להחליט מתי ואיך לקרוא לכל כלי, ללא שורת קוד\n"
        "נוספת בצד הסוכן. ב-REST, מידע זה היה חייב להיות מוטבע ב-system prompt\n"
        "או ב-hardcoded logic — פתרון שבור ברגע שה-API משתנה."
    )

    pdf.h2("4.2 אבטחה: מפתח פנימי (SCREENSTOP_INTERNAL_KEY)")
    pdf.body(
        "מדוע נדרש מפתח פנימי בתקשורת stdio?"
    )
    pdf.bullet(
        "ב-transport מסוג stdio אין שכבת HTTP ולכן אין middleware אימות רגיל.\n"
        "המפתח מוגדר כמשתנה סביבה — לא מוטבע בקוד (no hardcoding).\n"
        "agent.py מעביר את המפתח לתת-התהליך דרך env={} ב-StdioServerParameters.\n"
        "agent_store.py קורא את המפתח פעם אחת ב-module level — בזמן טעינה.\n"
        "_check_auth() נקראת בתחילת כל כלי; כשל מחזיר {'error': ...} מיידית.\n"
        "הגישה מקבילה ל-middleware ב-API gateway HTTP — אך מותאמת ל-stdio."
    )

    pdf.h2("4.3 שפה דינמית — זיהוי שפת המשתמש")
    pdf.body(
        "system_prompt.md מנחה את אלכס לזהות את שפת המשתמש ולהשיב בה.\n"
        "לקוח עברי — תשובה בעברית. לקוח אנגלי — תשובה באנגלית.\n"
        "החלטה זו שמורה ל-Claude (שכבת הסוכן) ולא לכלים (שכבת הנתונים).\n"
        "הכלים מחזירים נתונים באנגלית — שפה ניטרלית שכל consumer יכול לצרוך.\n"
        "הפרדה זו מאפשרת שימוש חוזר בשרת MCP לסוכנים בכל שפה."
    )

    pdf.h2("4.4 DEBUG Mode — שקיפות ללא דליפה")
    pdf.body(
        "כל הלוג הפנימי (קריאות כלים, תוצאות, רשימת כלים) עובר דרך _debug().\n"
        "ב-production: DEBUG לא מוגדר; המשתמש רואה רק את תשובת אלכס.\n"
        "ב-development: DEBUG=true — כל הזרימה הפנימית גלויה.\n"
        "גם רמת הלוג של ספריית mcp מוגדרת דינמית בהתאם ל-DEBUG flag.\n"
        "עיצוב זה מונע דליפת מידע פנימי בחוויית הלקוח ללא הקרבת יכולת debug."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 5. EDGE CASE HANDLING
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("5. טיפול בקצוות ושגיאות")

    pdf.h2("5.1 אין תוצאות חיפוש")
    pdf.body(
        "כאשר search_products לא מוצאת מוצרים תואמים:"
    )
    pdf.bullet(
        "הכלי מחזיר total_matches: 0 ו-message מפורש באנגלית.\n"
        "system_prompt.md מנחה את אלכס לא לעצור ולא להתנצל בלבד.\n"
        "אלכס נדרש: להודות שאין תוצאות, לספק עצה כללית להגנת מסכים,\n"
        "   להציע ניסוח חדש, ואופציונלית לקרוא get_catalog לסקירה מלאה.\n"
        "השכבה הנכונה: הכלי מדווח עובדות; הסוכן אחראי לחוויית המשתמש."
    )

    pdf.h2("5.2 כישלון אימות — מפתח חסר")
    pdf.body(
        "כאשר SCREENSTOP_INTERNAL_KEY לא מוגדר:"
    )
    pdf.bullet(
        "agent.py — sys.exit(1) עם הודעת שגיאה ל-stderr לפני כל פעולה.\n"
        "agent_store.py — _check_auth() מחזירה {'error': 'Unauthorized...'}\n"
        "   הכלי לא מבצע שום לוגיקה עסקית לפני האימות.\n"
        "Claude יקבל את הודעת השגיאה כ-tool_result ויסביר למשתמש\n"
        "   שיש בעיה טכנית — ללא חשיפת פרטים פנימיים."
    )

    pdf.h2("5.3 שאילתה ריקה")
    pdf.body(
        "כאשר search_products מקבלת מחרוזת ריקה:"
    )
    pdf.bullet(
        "הכלי מזהה query.strip() == '' ומחזיר את הקטלוג המלא.\n"
        "זהה להתנהגות get_catalog — אין fail, אין שגיאה.\n"
        "message מסביר: 'No query provided — returning full catalog'."
    )

    pdf.h2("5.4 בקשה לרמה לא-קיימת")
    pdf.body(
        "כאשר לקוח שואל על מוצר שלא קיים (למשל 'ScreenStop Ultra'):"
    )
    pdf.bullet(
        "search_products תחזיר total_matches: 0.\n"
        "system_prompt.md מנחה אלכס לבהיר שהמוצר לא קיים.\n"
        "אלכס מציג את שלוש הרמות האמיתיות: Light, Pro, Enterprise."
    )

    pdf.h2("5.5 stop_reason לא צפוי")
    pdf.body(
        "ב-run_agent, אם Claude מחזיר stop_reason שאינו 'end_turn' או 'tool_use':"
    )
    pdf.bullet(
        "הפונקציה מחזירה מחרוזת '(unexpected stop reason: X)' — לא זורקת exception.\n"
        "הלולאה הראשית מציגה את המחרוזת הזו כ-fallback — לא קורסת.\n"
        "עיצוב זה מאפשר graceful degradation גם במצבי API לא צפויים."
    )

    pdf.h2("5.6 קלט EOF / KeyboardInterrupt")
    pdf.body(
        "בלולאת ה-CLI הראשית:"
    )
    pdf.bullet(
        "try/except תופס EOFError (pipe סגור, piped input נגמר) וגם\n"
        "   KeyboardInterrupt (Ctrl+C מהמשתמש).\n"
        "שניהם מטופלים בנחת: הדפסת 'Goodbye!' ויציאה נקייה מהלולאה.\n"
        "ה-context managers (stdio_client, ClientSession) מבטיחים\n"
        "   שגם תת-התהליך agent_store.py ייסגר בצורה מסודרת."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # 6. ENVIRONMENT VARIABLES SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("6. סיכום משתני הסביבה")

    pdf.ln(2)
    pdf.table_row(["ברירת מחדל", "מטרה", "משתנה"], bold=True, fill=True)
    pdf.table_row(["חובה", "מפתח Anthropic API לגישה ל-Claude", "ANTHROPIC_API_KEY"])
    pdf.table_row(
        ["screenstop-internal-auth-2026",
         "מפתח משותף בין agent ל-MCP server",
         "SCREENSTOP_INTERNAL_KEY"]
    )
    pdf.table_row(["false", "הפעלת לוג פנימי מלא", "DEBUG"])

    pdf.ln(5)
    pdf.h2("הפעלת הדמו — פקודות מוכנות")
    pdf.code_block(
        "# התקנת תלויות\n"
        "pip install -r requirements.txt\n"
        "\n"
        "# הגדרת משתני סביבה\n"
        "export ANTHROPIC_API_KEY=sk-ant-...\n"
        "export SCREENSTOP_INTERNAL_KEY=screenstop-internal-auth-2026\n"
        "\n"
        "# הרצה רגילה\n"
        "python agent.py\n"
        "\n"
        "# הרצה עם לוג מלא\n"
        "DEBUG=true python agent.py"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pdf = DocPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=15, top=15, right=15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("Main", "",  FONT_REGULAR)
    pdf.add_font("Main", "B", FONT_BOLD)
    pdf.add_font("Mono",   "",  FONT_MONO)

    build(pdf)

    pdf.output(OUTPUT_FILE)
    print(f"PDF generated: {OUTPUT_FILE}")
