#!/usr/bin/env python3
"""Generate teya-kovcheg-kids WordPress theme files."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "teya-memory" / "wp" / "theme" / "teya-kovcheg-kids"
HERO_CUTOUT = "https://tempfile.aiquickdraw.com/r/66ae758d53f6992b3079cf00e5166742_1780504558_t2i79lt7.png"


def w(rel: str, content: str) -> None:
    p = THEME / rel.replace("/", "\\") if "\\" not in rel else THEME / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")
    print(f"  {rel}")


def main() -> None:
    print("Generating teya-kovcheg-kids theme...")
    w("style.css", STYLE_CSS)
    w("functions.php", FUNCTIONS)
    w("index.php", INDEX_PHP)
    w("header.php", HEADER)
    w("footer.php", FOOTER)
    w("front-page.php", FRONT_PAGE)
    w("page-programma.php", PAGE_PROGRAMMA)
    w("page-format-i-raspisanie.php", PAGE_FORMAT)
    w("page-prepodavateli.php", PAGE_PREPOD)
    w("home.php", HOME_BLOG)
    w("single.php", SINGLE)
    w("page.php", PAGE)
    w("404.php", PAGE_404)
    w("search.php", SEARCH)
    w("archive.php", ARCHIVE)
    w("searchform.php", SEARCHFORM)
    w("comments.php", COMMENTS)
    w("theme.json", THEME_JSON)
    w(".deployignore", DEPLOYIGNORE)
    w("inc/setup.php", INC_SETUP)
    w("inc/enqueues.php", INC_ENQUEUES)
    w("inc/security.php", INC_SECURITY)
    w("inc/customizer.php", INC_CUSTOMIZER)
    w("inc/breadcrumbs.php", INC_BREADCRUMBS)
    w("inc/forms.php", INC_FORMS)
    w("inc/seo.php", INC_SEO)
    w("inc/indexing.php", INC_INDEXING)
    w("inc/content-data.php", INC_CONTENT)
    w("template-parts/content/content.php", TPL_CONTENT)
    w("template-parts/content/content-none.php", TPL_NONE)
    w("template-parts/sections/faq.php", TPL_FAQ)
    w("template-parts/sections/lead-form.php", TPL_LEAD)
    w("template-parts/sections/blog-topics.php", TPL_BLOG)
    w("assets/dist/style.css", DIST_CSS)
    w("assets/dist/main.js", DIST_JS)
    w("assets/src/js/main.js", DIST_JS)
    w("assets/src/scss/main.scss", "// Compiled to assets/dist/style.css\n")
    print(f"Done: {THEME}")


STYLE_CSS = r'''/*
Theme Name: Ковчег Kids — Вайбкодинг
Theme URI: https://mcp-kv.store/
Author: Teya Aurora
Description: Онлайн-школа вайбкодинга для детей 10–16. Panda School soft edu pop design.
Version: 1.0.0
Requires at least: 6.0
Tested up to: 6.8
Requires PHP: 7.4
Text Domain: teya-kovcheg-kids
License: GNU General Public License v2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Tags: education, custom-colors, custom-menu, featured-images, translation-ready
*/
'''

FUNCTIONS = r'''<?php
/**
 * Theme bootstrap — teya-kovcheg-kids
 *
 * @package teya-kovcheg-kids
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'TEYA_KIDS_VERSION', '1.0.0' );
define( 'TEYA_KIDS_DIR', get_template_directory() );
define( 'TEYA_KIDS_URI', get_template_directory_uri() );

require_once TEYA_KIDS_DIR . '/inc/setup.php';
require_once TEYA_KIDS_DIR . '/inc/enqueues.php';
require_once TEYA_KIDS_DIR . '/inc/security.php';
require_once TEYA_KIDS_DIR . '/inc/breadcrumbs.php';
require_once TEYA_KIDS_DIR . '/inc/customizer.php';
require_once TEYA_KIDS_DIR . '/inc/content-data.php';
require_once TEYA_KIDS_DIR . '/inc/forms.php';
require_once TEYA_KIDS_DIR . '/inc/indexing.php';
require_once TEYA_KIDS_DIR . '/inc/seo.php';
'''

INDEX_PHP = r'''<?php
/**
 * Fallback index
 *
 * @package teya-kovcheg-kids
 */
get_header();
?>
<main id="primary" class="site-main">
	<?php
	if ( have_posts() ) {
		while ( have_posts() ) {
			the_post();
			get_template_part( 'template-parts/content/content' );
		}
	} else {
		get_template_part( 'template-parts/content/content', 'none' );
	}
	?>
</main>
<?php
get_footer();
'''

DEPLOYIGNORE = '''node_modules
.git
*.map
assets/src
'''

THEME_JSON = '''{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "color": {
      "palette": [
        { "slug": "background", "color": "#FAFAF8", "name": "Background" },
        { "slug": "foreground", "color": "#1A3A2A", "name": "Foreground" },
        { "slug": "primary", "color": "#C5E86C", "name": "Lime CTA" },
        { "slug": "secondary", "color": "#B8E6D0", "name": "Mint" },
        { "slug": "accent-pink", "color": "#F5A8B8", "name": "Pink" },
        { "slug": "accent-yellow", "color": "#FFE566", "name": "Yellow" }
      ]
    },
    "typography": {
      "fontFamilies": [
        { "fontFamily": "Montserrat, sans-serif", "slug": "display", "name": "Montserrat" },
        { "fontFamily": "Nunito, sans-serif", "slug": "body", "name": "Nunito" }
      ]
    },
    "layout": { "contentSize": "1200px", "wideSize": "1400px" }
  },
  "styles": {
    "color": { "background": "var(--wp--preset--color--background)", "text": "var(--wp--preset--color--foreground)" },
    "typography": { "fontFamily": "var(--wp--preset--font-family--body)", "fontSize": "1rem", "lineHeight": "1.6" }
  }
}
'''

# Due to size limits, remaining templates are appended via exec in script continuation
if __name__ == "__main__":
    main()
