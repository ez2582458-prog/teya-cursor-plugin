#!/usr/bin/env python3
"""Build teya-kovcheg-kids WordPress theme (AURA hot pink gaming kids)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "teya-memory" / "wp" / "theme" / "teya-kovcheg-kids"

MASCOT = "https://tempfile.aiquickdraw.com/r/ef632523504e0fdd3bf67802efe89102_1780518077_4oahez24.png"
SERVICES_STRIP = "https://tempfile.aiquickdraw.com/images/chatgpt/34296ba30c5aad511cfb03147e11008f_2440e0dedf7c420ebffee61b394f2677.png"


def w(rel: str, content: str) -> None:
    p = THEME / rel.replace("\\", "/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    print(f"Building theme at {THEME}")
    w("style.css", STYLE_CSS)
    w("functions.php", FUNCTIONS)
    w("index.php", INDEX_PHP)
    w("header.php", HEADER)
    w("footer.php", FOOTER)
    w("front-page.php", FRONT_PAGE)
    w("page-programma.php", PAGE_PROGRAMMA)
    w("page-format-i-raspisanie.php", PAGE_FORMAT)
    w("page-prepodavateli.php", PAGE_PREPOD)
    w("page-politika-konfidentsialnosti.php", PAGE_PRIVACY)
    w("page-cookies.php", PAGE_COOKIES)
    w("home.php", HOME_BLOG)
    w("single.php", SINGLE)
    w("page.php", PAGE_GENERIC)
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
    w("inc/helpers.php", INC_HELPERS)
    w("template-parts/content/content.php", TPL_CONTENT)
    w("template-parts/content/content-none.php", TPL_NONE)
    w("template-parts/sections/compact-hero.php", TPL_COMPACT_HERO)
    w("template-parts/sections/cta-strip.php", TPL_CTA_STRIP)
    w("template-parts/sections/faq.php", TPL_FAQ)
    w("template-parts/sections/lead-form.php", TPL_LEAD)
    w("template-parts/sections/blog-topics.php", TPL_BLOG_TOPICS)
    w("assets/dist/style.css", DIST_CSS)
    w("assets/dist/main.js", DIST_JS)
    w("sitemap-static.xml", SITEMAP_STATIC)
    w("llms.txt", LLMS_TXT)
    print("Done.")


STYLE_CSS = """/*
Theme Name: Ковчег Kids — Вайбкодинг
Theme URI: https://mcp-kv.store/
Author: Teya Aurora
Description: Онлайн-школа вайбкодинга для детей 10–16. Hot pink gaming kids landing.
Version: 1.0.0
Requires at least: 6.0
Tested up to: 6.8
Requires PHP: 7.4
Text Domain: teya-kovcheg-kids
License: GNU General Public License v2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Tags: education, custom-colors, custom-menu
*/
"""

FUNCTIONS = """<?php
/**
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
require_once TEYA_KIDS_DIR . '/inc/helpers.php';
require_once TEYA_KIDS_DIR . '/inc/breadcrumbs.php';
require_once TEYA_KIDS_DIR . '/inc/customizer.php';
require_once TEYA_KIDS_DIR . '/inc/forms.php';
require_once TEYA_KIDS_DIR . '/inc/indexing.php';
require_once TEYA_KIDS_DIR . '/inc/seo.php';
"""

INDEX_PHP = """<?php
get_header();
?>
<main id="primary" class="site-main section">
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
"""

DEPLOYIGNORE = """node_modules
.git
*.map
assets/src
"""

THEME_JSON = """{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "color": {
      "palette": [
        { "slug": "primary", "color": "#FF1F8F", "name": "Hot Pink" },
        { "slug": "primary-deep", "color": "#E8176F", "name": "Pink Deep" },
        { "slug": "cta", "color": "#FFD400", "name": "Yellow CTA" },
        { "slug": "background", "color": "#FFFFFF", "name": "White" },
        { "slug": "foreground", "color": "#1A1A1A", "name": "Ink" }
      ]
    },
    "typography": {
      "fontFamilies": [
        { "fontFamily": "\\"Russo One\\", sans-serif", "slug": "display", "name": "Russo One" },
        { "fontFamily": "Nunito, sans-serif", "slug": "body", "name": "Nunito" }
      ]
    },
    "layout": { "contentSize": "1200px", "wideSize": "1200px" }
  }
}
"""

# Continue in next write - file too large, split INC and templates

if __name__ == "__main__":
    main()
