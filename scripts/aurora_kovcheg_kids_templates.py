# Aurora theme templates — teya-kovcheg-kids
"""Large template strings for aurora_kovcheg_kids_full_build.py"""

THEME_JSON = """{
  "$schema": "https://schemas.wp.org/trunk/theme.json",
  "version": 3,
  "settings": {
    "color": {
      "palette": [
        { "slug": "background", "color": "#FAFAF7", "name": "Off White" },
        { "slug": "lime", "color": "#B8FF3C", "name": "Lime CTA" },
        { "slug": "pink", "color": "#FF3CAC", "name": "Pink" },
        { "slug": "yellow", "color": "#FFE066", "name": "Yellow" },
        { "slug": "sky", "color": "#5BC0FF", "name": "Sky" },
        { "slug": "foreground", "color": "#111111", "name": "Text" }
      ]
    },
    "layout": { "contentSize": "1200px", "wideSize": "1200px" }
  }
}
"""

LLMS_TXT = """# Ковчег Kids — Вайбкодинг для детей 10–16
https://mcp-kv.store/

Детская онлайн-программа: Cursor AI, нейросети, 12 недель, 4 модуля, Demo Day.

## Key pages
- https://mcp-kv.store/
- https://mcp-kv.store/programma/
- https://mcp-kv.store/probnoe/
- https://mcp-kv.store/format/
- https://mcp-kv.store/tarify/
- https://mcp-kv.store/blog/
"""

INC_SETUP = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
add_action( 'after_setup_theme', function () {
	load_theme_textdomain( 'teya-kovcheg-kids', TEYA_KIDS_DIR . '/languages' );
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );
	register_nav_menus( array(
		'primary' => __( 'Primary Menu', 'teya-kovcheg-kids' ),
		'footer'  => __( 'Footer Menu', 'teya-kovcheg-kids' ),
	) );
} );
add_action( 'init', function () {
	if ( ! has_nav_menu( 'primary' ) ) {
		// Fallback registered in bootstrap.
	}
} );
"""

INC_MEDIA = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
function teya_get_media_map() {
	static $map = null;
	if ( null === $map ) {
		$path = TEYA_KIDS_DIR . '/media-map.json';
		if ( file_exists( $path ) ) {
			$decoded = json_decode( file_get_contents( $path ), true );
			$map     = is_array( $decoded ) ? $decoded : array( 'assets' => array() );
		} else {
			$map = array( 'assets' => array() );
		}
	}
	return $map;
}
function teya_media_by_file( $file ) {
	$base = ltrim( $file, '/' );
	foreach ( teya_get_media_map()['assets'] ?? array() as $item ) {
		if ( ( $item['file'] ?? '' ) === $base ) {
			return $item;
		}
	}
	return null;
}
function teya_kids_img( $file ) {
	$item = teya_media_by_file( $file );
	if ( $item && ! empty( $item['attachment_url'] ) ) {
		return $item['attachment_url'];
	}
	return TEYA_KIDS_URI . '/assets/images/' . ltrim( $file, '/' );
}
function teya_media_img( $registry_id, $attrs = array() ) {
	foreach ( teya_get_media_map()['assets'] ?? array() as $item ) {
		if ( ( $item['registry_id'] ?? '' ) !== $registry_id ) {
			continue;
		}
		$id = (int) ( $item['attachment_id'] ?? 0 );
		if ( $id > 0 ) {
			if ( ! isset( $attrs['alt'] ) && ! empty( $item['alt_text'] ) ) {
				$attrs['alt'] = $item['alt_text'];
			}
			return wp_get_attachment_image( $id, 'full', false, $attrs );
		}
	}
	return '';
}
"""

INC_ASSETS = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
function teya_kids_asset_exists( $file ) {
	return file_exists( TEYA_KIDS_DIR . '/assets/images/' . ltrim( $file, '/' ) );
}
"""

INC_ENQUEUES = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style(
		'teya-kids-fonts',
		'https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&family=Russo+One&display=swap',
		array(),
		null
	);
	wp_enqueue_style( 'teya-kids', TEYA_KIDS_URI . '/assets/dist/style.css', array( 'teya-kids-fonts' ), TEYA_KIDS_VERSION );
	wp_enqueue_script( 'teya-kids', TEYA_KIDS_URI . '/assets/dist/main.js', array(), TEYA_KIDS_VERSION, true );
	wp_localize_script( 'teya-kids', 'teyaKids', array(
		'ajaxUrl' => admin_url( 'admin-ajax.php' ),
		'nonce'   => wp_create_nonce( 'teya_kids_lead' ),
	) );
} );
"""

INC_SECURITY = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
remove_action( 'wp_head', 'wp_generator' );
add_filter( 'xmlrpc_enabled', '__return_false' );
"""

INC_CUSTOMIZER = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
// Reserved for future Metrika/GA4 IDs.
"""

INC_HELPERS = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
function teya_kids_primary_nav() {
	wp_nav_menu( array(
		'theme_location' => 'primary',
		'container'      => false,
		'menu_class'     => 'nav-list',
		'fallback_cb'    => 'teya_kids_nav_fallback',
	) );
}
function teya_kids_nav_fallback() {
	$items = array(
		array( 'Программа', home_url( '/programma/' ) ),
		array( 'Формат', home_url( '/format/' ) ),
		array( 'Тарифы', home_url( '/tarify/' ) ),
		array( 'Блог', home_url( '/blog/' ) ),
	);
	echo '<ul class="nav-list">';
	foreach ( $items as $i ) {
		printf( '<li><a href="%s">%s</a></li>', esc_url( $i[1] ), esc_html( $i[0] ) );
	}
	echo '</ul>';
}
function teya_kids_cta( $url, $text, $class = 'btn btn-lime', $data = '' ) {
	printf(
		'<a class="%s" href="%s" %s>%s</a>',
		esc_attr( $class ),
		esc_url( $url ),
		$data,
		esc_html( $text )
	);
}
"""

INC_BREADCRUMBS = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
/** JSON-LD only — no visible breadcrumbs UI */
function teya_kids_breadcrumb_jsonld( $items ) {
	if ( empty( $items ) ) { return; }
	$list = array();
	$pos  = 1;
	foreach ( $items as $item ) {
		$list[] = array(
			'@type'    => 'ListItem',
			'position' => $pos++,
			'name'     => $item['name'],
			'item'     => $item['url'],
		);
	}
	$schema = array(
		'@context'        => 'https://schema.org',
		'@type'           => 'BreadcrumbList',
		'itemListElement' => $list,
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>';
}
"""

INC_FORMS = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
add_action( 'wp_ajax_teya_kids_lead', 'teya_kids_handle_lead' );
add_action( 'wp_ajax_nopriv_teya_kids_lead', 'teya_kids_handle_lead' );
function teya_kids_handle_lead() {
	check_ajax_referer( 'teya_kids_lead', 'nonce' );
	if ( ! empty( $_POST['website'] ) ) {
		wp_send_json_error( array( 'message' => 'Spam detected' ), 400 );
	}
	$fields = array( 'parent_name', 'child_age', 'city', 'phone', 'contact_method' );
	$data   = array();
	foreach ( $fields as $f ) {
		$data[ $f ] = sanitize_text_field( wp_unslash( $_POST[ $f ] ?? '' ) );
	}
	if ( empty( $data['parent_name'] ) || empty( $data['phone'] ) ) {
		wp_send_json_error( array( 'message' => 'Заполните имя и телефон' ), 422 );
	}
	$body = "Ковчег Kids lead\\n" . print_r( $data, true );
	wp_mail( get_option( 'admin_email' ), 'Заявка Ковчeg Kids', $body );
	do_action( 'teya_kids_lead_submitted', $data );
	wp_send_json_success( array( 'message' => 'Заявка принята. Мы свяжемся в течение одного рабочего дня.' ) );
}
"""

INC_SEO = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
add_action( 'wp_head', function () {
	if ( is_front_page() ) {
		echo '<meta name="description" content="12 недель онлайн: нейросети, Cursor, 2–4 проекта и Demo Day. Запишите ребёнка на пробное занятие." />' . "\\n";
	}
	$org = array(
		'@context' => 'https://schema.org',
		'@type'      => 'EducationalOrganization',
		'@id'        => home_url( '/#organization' ),
		'name'       => 'Ковчег Kids',
		'url'        => home_url( '/' ),
		'description'=> 'Детская программа вайбкодинга для детей 10–16 лет',
		'areaServed' => 'RU',
	);
	$site = array(
		'@context' => 'https://schema.org',
		'@type'      => 'WebSite',
		'@id'        => home_url( '/#website' ),
		'url'        => home_url( '/' ),
		'name'       => 'Ковчег Kids',
		'publisher'  => array( '@id' => home_url( '/#organization' ) ),
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $org, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>';
	echo '<script type="application/ld+json">' . wp_json_encode( $site, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>';
}, 5 );
"""

INC_INDEXING = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
add_action( 'init', function () {
	add_rewrite_rule( '^llms\\.txt$', 'index.php?teya_llms=1', 'top' );
} );
add_filter( 'query_vars', function ( $v ) {
	$v[] = 'teya_llms';
	return $v;
} );
add_action( 'template_redirect', function () {
	if ( get_query_var( 'teya_llms' ) ) {
		header( 'Content-Type: text/plain; charset=utf-8' );
		readfile( TEYA_KIDS_DIR . '/llms.txt' );
		exit;
	}
	if ( is_search() || is_404() ) {
		echo '<meta name="robots" content="noindex, follow" />' . "\\n";
	}
} );
"""

HEADER = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link screen-reader-text" href="#primary"><?php esc_html_e( 'Перейти к содержимому', 'teya-kovcheg-kids' ); ?></a>
<header class="site-header" role="banner">
<div class="container inner">
<a class="logo" href="<?php echo esc_url( home_url( '/' ) ); ?>" data-nav="logo">Ковчег Kids</a>
<nav class="nav" aria-label="<?php esc_attr_e( 'Основное меню', 'teya-kovcheg-kids' ); ?>">
<?php teya_kids_primary_nav(); ?>
</nav>
<?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться', 'btn btn-lime menu-item-cta', 'data-nav="cta-header" data-cta="primary"' ); ?>
<button type="button" class="nav-toggle" aria-expanded="false" aria-controls="mobile-nav" aria-label="Меню"><span></span></button>
</div>
<div id="mobile-nav" class="mobile-nav" hidden>
<?php teya_kids_primary_nav(); ?>
<?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime btn-block', 'data-cta="primary-mobile"' ); ?>
</div>
</header>
"""

FOOTER = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
?>
<footer class="site-footer" role="contentinfo">
<div class="footer-cta-strip">
<div class="container">
<p class="footer-cta-text">Готовы познакомить ребёнка с вайбкодингом?</p>
<?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime', 'data-cta="primary-footer"' ); ?>
</div>
</div>
<div class="container footer-grid">
<div class="footer-col">
<h3>Курс</h3>
<ul>
<li><a href="<?php echo esc_url( home_url( '/programma/' ) ); ?>">Программа 12 недель</a></li>
<li><a href="<?php echo esc_url( home_url( '/format/' ) ); ?>">Формат и расписание</a></li>
<li><a href="<?php echo esc_url( home_url( '/tarify/' ) ); ?>">Тарифы</a></li>
<li><a href="<?php echo esc_url( home_url( '/probnoe/' ) ); ?>">Пробное занятие</a></li>
</ul>
</div>
<div class="footer-col">
<h3>Родителям</h3>
<ul>
<li><a href="<?php echo esc_url( home_url( '/blog/' ) ); ?>">Блог</a></li>
<li><a href="<?php echo esc_url( home_url( '/blog/vajbkoding-dlya-detey/' ) ); ?>">Что такое вайбкодинг</a></li>
<li><a href="<?php echo esc_url( home_url( '/blog/bezopasnost-chatgpt-cursor/' ) ); ?>">Безопасность AI</a></li>
<li><a href="<?php echo esc_url( home_url( '/blog/5-proektov-s-ai/' ) ); ?>">5 проектов с AI</a></li>
</ul>
</div>
<div class="footer-col">
<h3>Ковчег</h3>
<ul>
<li><a href="https://kv-ai.ru/obuchenie-po-make" rel="noopener noreferrer">Клуб Ковчег для взрослых</a></li>
<li><a href="https://mayai.ru/obo-mne" rel="noopener noreferrer">Maya AI — Артур Хорошев</a></li>
</ul>
</div>
</div>
<div class="container footer-legal">
<a href="<?php echo esc_url( home_url( '/politika-konfidencialnosti/' ) ); ?>">Политика конфиденциальности</a>
<span aria-hidden="true"> · </span>
<a href="<?php echo esc_url( home_url( '/politika-cookies/' ) ); ?>">Политика cookies</a>
<p class="copyright">&copy; <?php echo esc_html( gmdate( 'Y' ) ); ?> Ковчег Kids · mcp-kv.store</p>
</div>
</footer>
<div id="cookie-banner" class="cookie-banner" role="dialog" aria-label="Cookies" hidden>
<p>Мы используем cookies для работы сайта и аналитики. <a href="<?php echo esc_url( home_url( '/politika-cookies/' ) ); ?>">Подробнее</a> · <a href="<?php echo esc_url( home_url( '/politika-konfidencialnosti/' ) ); ?>">ПДн</a></p>
<button type="button" class="btn btn-lime" id="cookie-accept">Принять cookies</button>
</div>
<?php wp_footer(); ?>
</body>
</html>
"""

TPL_LEAD_FORM = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
$context = $args['context'] ?? 'home';
$title   = $args['title'] ?? 'Запишите ребёнка на пробное';
?>
<section class="section form-section lead-form-section" id="lead-form">
<div class="container">
<div class="form-panel">
<form class="teya-lead-form" data-context="<?php echo esc_attr( $context ); ?>" novalidate>
<h2><?php echo esc_html( $title ); ?></h2>
<p class="form-sub">Перезвоним или напишем в выбранный мессенджер, чтобы согласовать дату.</p>
<label class="field"><span>Имя родителя</span><input type="text" name="parent_name" required placeholder="Как к вам обращаться"></label>
<label class="field"><span>Возраст ребёнка</span><input type="text" name="child_age" placeholder="Например: 12"></label>
<label class="field"><span>Город</span><input type="text" name="city" placeholder="Для часового пояса когорты"></label>
<label class="field"><span>Телефон</span><input type="tel" name="phone" required placeholder="+7 …"></label>
<div class="toggle" role="radiogroup" aria-label="Как связаться">
<button type="button" class="toggle-btn active" data-value="telegram">Telegram</button>
<button type="button" class="toggle-btn" data-value="whatsapp">WhatsApp</button>
<button type="button" class="toggle-btn" data-value="phone">Звонок</button>
</div>
<input type="hidden" name="contact_method" value="telegram">
<input type="text" name="website" class="hp-field" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="consent"><input type="checkbox" name="consent" required> Я соглашаюсь на <a href="<?php echo esc_url( home_url( '/politika-konfidencialnosti/' ) ); ?>">обработку персональных данных</a> и ознакомлен(а) с <a href="<?php echo esc_url( home_url( '/politika-cookies/' ) ); ?>">политикой cookies</a>.</label>
<button type="submit" class="btn btn-lime btn-block">Отправить заявку</button>
<p class="form-msg" role="status" aria-live="polite"></p>
</form>
<div class="form-visual">
<div class="blob blob-sky form-blob"></div>
<div class="blob blob-lime form-blob2"></div>
<img src="<?php echo esc_url( teya_kids_img( 'form-robot-wave.png' ) ); ?>" alt="Робот Ковчег приглашает на пробное занятие" width="320" height="420" loading="lazy">
</div>
</div>
</div>
</section>
"""

TPL_FAQ = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
$items = $args['items'] ?? array();
if ( ! $items ) { return; }
?>
<section class="section faq-section">
<div class="container">
<h2><?php echo esc_html( $args['title'] ?? 'Частые вопросы' ); ?></h2>
<div class="faq-list">
<?php foreach ( $items as $i => $item ) : ?>
<details class="faq-item" <?php echo 0 === $i ? 'open' : ''; ?>>
<summary><?php echo esc_html( $item['q'] ); ?></summary>
<div class="faq-a"><?php echo wp_kses_post( $item['a'] ); ?></div>
</details>
<?php endforeach; ?>
</div>
</div>
</section>
<?php
if ( ! empty( $args['schema'] ) ) {
	$entities = array();
	foreach ( $items as $item ) {
		$entities[] = array(
			'@type'          => 'Question',
			'name'           => $item['q'],
			'acceptedAnswer' => array(
				'@type' => 'Answer',
				'text'  => wp_strip_all_tags( $item['a'] ),
			),
		);
	}
	$faq = array(
		'@context'   => 'https://schema.org',
		'@type'      => 'FAQPage',
		'mainEntity' => $entities,
	);
	echo '<script type="application/ld+json">' . wp_json_encode( $faq, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>';
}
?>
"""

FRONT_PAGE = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
$faq = array(
	array( 'q' => 'Что такое вайбкодинг для детей?', 'a' => 'Вайбкодинг — способ создавать сайты, игры и ботов, описывая задачу словами: ребёнок формулирует идею, AI в Cursor помогает с кодом, наставник учит проверять результат. Курс 12 недель, 4 модуля, Demo Day.' ),
	array( 'q' => 'С какого возраста подходит курс?', 'a' => '10–16 лет, онлайн по России. Запись — <a href="/probnoe/">пробное занятие</a>.' ),
	array( 'q' => 'Нужен ли опыт программирования?', 'a' => 'Нет. Нужны базовые навыки ПК и русский язык. Формат — <a href="/format/">онлайн, 1 занятие в неделю</a>.' ),
	array( 'q' => 'Безопасны ли нейросети и Cursor?', 'a' => 'Мы учим не вводить личные данные и редактировать ответы. Подробнее — <a href="/blog/bezopasnost-chatgpt-cursor/">правила для родителей</a>.' ),
	array( 'q' => 'Сколько стоит курс?', 'a' => 'Публичных цен нет — условия на <a href="/probnoe/">пробном</a>. Тарифы — <a href="/tarify/">без цифр</a>.' ),
	array( 'q' => 'Как записаться?', 'a' => 'Оставьте заявку на <a href="/probnoe/">пробном</a>: имя родителя, возраст, город, телефон и способ связи.' ),
);
?>
<main id="primary">
<section class="hero">
<div class="container hero-grid">
<div class="hero-copy">
<p class="eyebrow">Ковчег Kids · онлайн для всей России</p>
<h1>Вайбкодинг для детей 10–16: <span class="highlight">игры и приложения</span> с AI</h1>
<p class="hero-sub">12 недель, 4 модуля и финальный Demo Day. Ребёнок учится формулировать идеи, работать с нейросетями безопасно и собирать проекты в Cursor — с поддержкой наставника.</p>
<div class="hero-ctas">
<?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime', 'data-cta="primary"' ); ?>
<?php teya_kids_cta( home_url( '/programma/' ), 'Смотреть программу', 'btn btn-ghost', 'data-cta="secondary-programma"' ); ?>
</div>
</div>
<div class="hero-visual">
<div class="blob blob-pink"></div><div class="blob blob-lime"></div><div class="blob blob-sky"></div>
<img src="<?php echo esc_url( teya_kids_img( 'hero-mascot-kovcheg.png' ) ); ?>" alt="Робот Ковчег — маскот школы вайбкодинга" width="380" height="507" fetchpriority="high">
</div>
</div>
</section>
<section class="stats stats-overlap">
<div class="container stats-grid">
<div><strong>12</strong><span>недель программы</span></div>
<div><strong>4</strong><span>модуля</span></div>
<div><strong>Demo</strong><span>Day в финале</span></div>
</div>
</section>
<section class="section pain-solution">
<div class="container prose">
<h2>Ребёнок живёт в экране — а вы хотите, чтобы там был смысл</h2>
<p>Многие родители видят TikTok, игры и бесконечные чаты — и тревогу, что «всё это не про будущее». Классические курсы часто начинаются со Scratch или долгого Python, а тема нейросетей остаётся без структуры.</p>
<h2>Ковчег Kids переводит интерес в проекты</h2>
<p>Мы не обещаем профессию за три месяца. Мы даём маршрут: от безопасных промптов — к игре в браузере, вайбкодингу в Cursor и Demo Day. Методология адаптирована из клуба <a href="https://kv-ai.ru/obuchenie-po-make" rel="noopener noreferrer">Ковчег</a> — с детской подачей.</p>
</div>
</section>
<section class="section benefits-section">
<div class="blob blob-pink benefits-blob"></div>
<div class="container">
<h2>Почему детям заходит</h2>
<div class="benefits">
<article class="card yellow">
<img src="<?php echo esc_url( teya_kids_img( 'benefit-yellow-ai-safe.png' ) ); ?>" alt="Ребёнок за ноутбуком с иконками безопасного AI" width="400" height="200" loading="lazy">
<div class="card-body"><h3>Нейросети с правилами</h3><p>Чек-лист приватности с первой недели. <a href="<?php echo esc_url( home_url( '/blog/bezopasnost-chatgpt-cursor/' ) ); ?>">Подробнее о безопасности</a>.</p></div>
</article>
<article class="card green">
<img src="<?php echo esc_url( teya_kids_img( 'benefit-green-projects.png' ) ); ?>" alt="Скриншоты детских мини-игр и приложений" width="400" height="200" loading="lazy">
<div class="card-body"><h3>2–4 проекта в портфолио</h3><p>Идеи — в <a href="<?php echo esc_url( home_url( '/blog/5-proektov-s-ai/' ) ); ?>">5 проектах с AI</a>.</p></div>
</article>
<article class="card pink">
<img src="<?php echo esc_url( teya_kids_img( 'benefit-pink-demo-day.png' ) ); ?>" alt="Demo Day — презентация проекта" width="400" height="200" loading="lazy">
<div class="card-body"><h3>Demo Day</h3><p>Финальный showcase — праздник прогресса без давления «единственного победителя».</p></div>
</article>
</div>
</div>
</section>
<div class="wave-divider" aria-hidden="true"></div>
<section class="section how accordion-section">
<div class="container how-wrap">
<div><h2>Как это работает</h2></div>
<div class="accordion" data-accordion>
<div class="accordion-item active" data-step="1"><span class="num">01</span><h3>Заявка на пробное</h3><p>Контакты на <a href="<?php echo esc_url( home_url( '/probnoe/' ) ); ?>">странице пробного</a>.</p></div>
<div class="accordion-item" data-step="2"><span class="num">02</span><h3>Пробное занятие</h3><p>Мини промпт-квест, вы видите темп группы.</p></div>
<div class="accordion-item" data-step="3"><span class="num">03</span><h3>Старт когорты</h3><p>1 живое занятие в неделю + домашний проект.</p></div>
<div class="accordion-item" data-step="4"><span class="num">04</span><h3>Четыре модуля</h3><p>Подробности на <a href="<?php echo esc_url( home_url( '/programma/' ) ); ?>">программе</a>.</p></div>
<div class="accordion-item" data-step="5"><span class="num">05</span><h3>Demo Day</h3><p>Презентация проектов и Q&A для родителей.</p></div>
</div>
</div>
</section>
<section class="section program-teaser program-wash">
<div class="container">
<h2>Четыре модуля за 12 недель</h2>
<p>Cursor подключается с модуля 3 — до этого промпты, творчество и безопасность.</p>
<ul class="module-chips">
<li><strong>М1</strong> AI-разведчик</li>
<li><strong>М2</strong> Творческая фабрика</li>
<li><strong>М3</strong> Вайбкодинг в Cursor</li>
<li><strong>М4</strong> Demo Day</li>
</ul>
<?php teya_kids_cta( home_url( '/programma/' ), 'Полная программа по неделям', 'btn btn-lime' ); ?>
</div>
</section>
<section class="section eeat">
<div class="container prose">
<h2>Методология клуба «Ковчег»</h2>
<p>Детская программа опирается на опыт взрослого клуба на kv-ai.ru. Основатель — <strong>Артур Хорошев</strong> (CEO Maya AI). Цифры mayai.ru относятся к взрослому треку — не переносим как статистику Kids.</p>
</div>
</section>
<?php get_template_part( 'template-parts/sections/faq', null, array( 'title' => 'FAQ', 'items' => $faq, 'schema' => true ) ); ?>
<section class="section blog-teaser blog-diagonal">
<div class="container">
<h2>Материалы для родителей</h2>
<p class="intro">Три статьи, с которых удобно начать.</p>
<div class="blog-grid">
<article class="card blog-card">
<a href="<?php echo esc_url( home_url( '/blog/vajbkoding-dlya-detey/' ) ); ?>">
<img src="<?php echo esc_url( teya_kids_img( 'blog-thumb-b01.png' ) ); ?>" alt="Иллюстрация ребёнка и AI-редактора" width="400" height="225" loading="lazy">
<div class="card-body"><h3>Что такое вайбкодинг для детей</h3><p>Чем подход отличается от Scratch и Python.</p></div>
</a>
</article>
<article class="card blog-card">
<a href="<?php echo esc_url( home_url( '/blog/bezopasnost-chatgpt-cursor/' ) ); ?>">
<img src="<?php echo esc_url( teya_kids_img( 'blog-thumb-ai-safety.png' ) ); ?>" alt="Щит и детский ноутбук" width="400" height="225" loading="lazy">
<div class="card-body"><h3>ChatGPT и Cursor: правила безопасности</h3><p>Чек-лист для родителей.</p></div>
</a>
</article>
<article class="card blog-card">
<a href="<?php echo esc_url( home_url( '/blog/5-proektov-s-ai/' ) ); ?>">
<img src="<?php echo esc_url( teya_kids_img( 'blog-thumb-b03.png' ) ); ?>" alt="Коллаж детских проектов" width="400" height="225" loading="lazy">
<div class="card-body"><h3>5 проектов с AI</h3><p>От промпт-квеста до Demo Day.</p></div>
</a>
</article>
</div>
<?php teya_kids_cta( home_url( '/blog/' ), 'Все материалы', 'btn btn-ghost' ); ?>
</div>
</section>
<?php get_template_part( 'template-parts/sections/lead-form', null, array( 'context' => 'home' ) ); ?>
</main>
<?php get_footer(); ?>
"""

# Inner page templates - compact but rich
PAGE_PROGRAMMA = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary">
<section class="page-hero program-hero program-wash">
<div class="container">
<h1>Программа 12 недель: 4 модуля вайбкодинга</h1>
<p class="lead">От первых промптов — к игре в браузере, Cursor, умным сценариям и Demo Day. Онлайн, 1 групповое занятие в неделю.</p>
<img class="roadmap-img" src="<?php echo esc_url( teya_kids_img( 'program-roadmap-12w.png' ) ); ?>" alt="Инфографика 12 недель и 4 модулей" width="1200" height="675" loading="eager">
<div class="hero-ctas"><?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime' ); ?><?php teya_kids_cta( home_url( '/format/' ), 'Формат и расписание', 'btn btn-ghost' ); ?></div>
</div>
</section>
<section class="section"><div class="container prose"><h2>Что будет у ребёнка к концу когорты</h2><ol class="outcomes"><li>Понимает ИИ, промпты и ограничения нейросетей.</li><li>2–4 законченных проекта: игра, приложение, AI-проект, бот.</li><li>Описывает идею для Cursor.</li><li>Цифровая безопасность и авторское право.</li><li>Demo Day — питч и обратная связь.</li></ol></div></section>
<section class="section modules-grid">
<div class="container">
<div class="module-panel pink" id="modul-1"><h2>Модуль 1 · AI-разведчик</h2><p>Недели 1–3: промпты, безопасность, промпт-квест, AI-помощник.</p></div>
<div class="module-panel yellow" id="modul-2"><h2>Модуль 2 · Творческая фабрика</h2><p>Недели 4–6: арт, сюжет, лендинг игры.</p></div>
<div class="module-panel green" id="modul-3"><h2>Модуль 3 · Вайбкодинг в Cursor</h2><p>Недели 7–9: викторина, игра в браузере, деплой.</p></div>
<div class="module-panel sky" id="modul-4"><h2>Модуль 4 · Demo Day</h2><p id="demo-day">Недели 10–12: сценарии, портфолио, финал.</p></div>
</div>
</section>
<section class="section demo-strip pink-strip"><div class="container"><h2>Demo Day</h2><p>3 минуты питча, демонстрация, Q&A для родителей.</p></div></section>
<section class="section"><div class="container prose"><h2>12 недель одним взглядом</h2><table class="data-table"><thead><tr><th>Недели</th><th>Фокус</th><th>Артефакт</th></tr></thead><tbody><tr><td>1–3</td><td>Промпты, безопасность</td><td>Промпт-квест</td></tr><tr><td>4–6</td><td>Арт, сюжет</td><td>Лендинг игры</td></tr><tr><td>7–9</td><td>Cursor</td><td>Игра по ссылке</td></tr><tr><td>10–12</td><td>Сценарии, финал</td><td>Demo Day</td></tr></tbody></table></div></section>
<section class="section cta-section"><div class="container"><?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime' ); ?></div></section>
</main>
<?php get_footer(); ?>
"""

PAGE_PROBNOE = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary">
<section class="page-hero sky-wash"><div class="container"><h1>Пробное занятие: познакомим ребёнка с вайбкодингом</h1><p class="lead">Онлайн для 10–16 лет и короткий разговор с вами о формате и безопасности.</p><ul class="trust-list"><li>12 нед / 4 модуля / Demo Day</li><li>Правила AI с первых минут</li><li>Стоимость когорты — на пробном</li></ul></div></section>
<section class="section"><div class="container prose"><h2>Кому подойдёт</h2><p>Ребёнку 10–16, интересующемуся играми и ботами. Родителю, который хочет безопасный вход в нейросети.</p><h2>Как проходит 60–75 минут</h2><table class="data-table"><tr><th>Этап</th><th>Содержание</th></tr><tr><td>~15 мин</td><td>Знакомство, правила</td></tr><tr><td>~30 мин</td><td>Мини промпт-квест</td></tr><tr><td>~15 мин</td><td>Q&A для родителя</td></tr></table></div></section>
<?php get_template_part( 'template-parts/sections/lead-form', null, array( 'context' => 'probnoe', 'title' => 'Пробное занятие Ковчег Kids' ) ); ?>
</main>
<?php get_footer(); ?>
"""

PAGE_FORMAT = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary">
<section class="page-hero"><div class="container format-hero-grid"><div><h1>Формат: онлайн, группа, одно занятие в неделю</h1><p class="lead">Живые созвоны по России. Домашний мини-проект 30–60 мин с чек-листом для родителя.</p></div><div class="format-mascot"><img src="<?php echo esc_url( teya_kids_img( 'hero-mascot-kovcheg.png' ) ); ?>" alt="Маскот Ковчег у календаря" width="228" height="304" loading="lazy"></div></div></section>
<section class="section"><div class="container bento-grid">
<article class="bento yellow"><h2>Онлайн · Россия</h2><p>Живые созвоны из любого города.</p></article>
<article class="bento green"><h2>Ритм</h2><p><strong>1 занятие в неделю</strong> + мини-проект дома. Не «2×/нед».</p></article>
<article class="bento sky"><h2>Родитель</h2><p>Бриф после каждого модуля: что сделал ребёнок.</p></article>
</div></section>
<section class="section parent-callout"><div class="container"><h2>Ваша роль — поддержка, не вайбкодинг за ребёнка</h2><p>Пять минут в неделю по карточке наставника. Не пишите промпты вместо ребёнка.</p></div></section>
<section class="section"><div class="container prose"><h2>Расписание когорт</h2><p>Даты старта публикуются после согласования. На <a href="<?php echo esc_url( home_url( '/probnoe/' ) ); ?>">пробном</a> узнаете актуальную когорту.</p><h2>Требования к ПК</h2><p>Windows 10+ или macOS, Chrome/Edge, наушники с микрофоном, Telegram. Cursor — с <a href="<?php echo esc_url( home_url( '/programma/#modul-3' ) ); ?>">модуля 3</a>.</p></div></section>
<section class="section cta-section"><div class="container"><?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime' ); ?></div></section>
</main>
<?php get_footer(); ?>
"""

PAGE_TARIFY = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary">
<section class="page-hero tarify-hero"><div class="container tarify-grid"><div><h1>Тарифы: выберите формат, цену уточним на пробном</h1><p class="lead">Публичных цен нет — условия согласуются на пробном. 5 800 ₽/мес kv-ai — другой продукт.</p></div><img src="<?php echo esc_url( teya_kids_img( 'form-robot-wave.png' ) ); ?>" alt="Маскот Ковчег" width="180" height="240" loading="lazy"></div></section>
<section class="section"><div class="container pricing-grid">
<article class="price-card"><h2>Kids Group</h2><p>12 недель, группа, Demo Day, blueprints, брифы для родителей.</p><?php teya_kids_cta( home_url( '/probnoe/' ), 'Уточнить на пробном', 'btn btn-lime' ); ?></article>
<article class="price-card pink-top"><h2>Kids Pro</h2><p>Group + доп. разборы проектов между занятиями.</p><?php teya_kids_cta( home_url( '/probnoe/' ), 'Уточнить на пробном', 'btn btn-lime' ); ?></article>
<article class="price-card sky-top"><h2>Индивидуальный</h2><p>1-на-1, гибкий график — по запросу.</p><?php teya_kids_cta( home_url( '/probnoe/' ), 'Уточнить на пробном', 'btn btn-lime' ); ?></article>
</div></section>
<section class="section"><div class="container prose"><h2>Почему цен нет на сайте</h2><p>Стоимость зависит от формата и когорты. Озвучиваем на <a href="<?php echo esc_url( home_url( '/probnoe/' ) ); ?>">пробном</a>.</p></div></section>
</main>
<?php get_footer(); ?>
"""

PAGE_PRIVACY = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary" class="section legal-page"><div class="container prose">
<h1>Политика обработки персональных данных</h1>
<p>Оператор: проект <strong>Ковчег Kids</strong> (mcp-kv.store). Сведения об ИП взрослого трека kv-ai не автоматически равны оператору Kids.</p>
<h2>Какие данные</h2><p>Имя родителя, возраст ребёнка, город, телефон, способ связи, cookies.</p>
<h2>Цели</h2><p>Запись на пробное, связь по курсу, аналитика при включённых счётчиках.</p>
<h2>Права</h2><p>Доступ, уточнение, удаление — запрос через контакт из footer (при появлении).</p>
<h2>Дети</h2><p>Данные ребёнка вводит родитель; избыточные данные не собираем.</p>
<p><a href="<?php echo esc_url( home_url( '/politika-cookies/' ) ); ?>">Политика cookies</a></p>
</div></main>
<?php get_footer(); ?>
"""

PAGE_COOKIES = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary" class="section legal-page"><div class="container prose">
<h1>Политика использования cookies</h1>
<p>Сайт mcp-kv.store использует cookies для форм, согласия и аналитики (Яндекс.Метрика, GA4 — при подключении).</p>
<h2>Типы</h2><p>Необходимые, функциональные (выбор cookies), аналитические.</p>
<h2>Управление</h2><p>Кнопка «Принять cookies» в баннере; отключение в браузере может ограничить форму.</p>
<p><a href="<?php echo esc_url( home_url( '/politika-konfidencialnosti/' ) ); ?>">Политика конфиденциальности</a></p>
</div></main>
<?php get_footer(); ?>
"""

HOME_BLOG = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary" class="section">
<div class="container">
<h1>Блог Ковчег Kids</h1>
<p class="intro">Статьи для родителей: вайбкодинг, безопасность AI, идеи проектов.</p>
<div class="blog-grid">
<?php if ( have_posts() ) : while ( have_posts() ) : the_post(); ?>
<article class="card blog-card">
<a href="<?php the_permalink(); ?>">
<?php if ( has_post_thumbnail() ) { the_post_thumbnail( 'medium_large', array( 'loading' => 'lazy' ) ); } else { ?>
<img src="<?php echo esc_url( teya_kids_img( 'blog-thumb-ai-safety.png' ) ); ?>" alt="" width="400" height="225" loading="lazy">
<?php } ?>
<div class="card-body"><h2><?php the_title(); ?></h2><p><?php echo esc_html( get_the_excerpt() ); ?></p></div>
</a>
</article>
<?php endwhile; else : ?>
<p>Материалы появятся после публикации статей.</p>
<?php endif; ?>
</div>
<?php the_posts_pagination(); ?>
<?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime' ); ?>
</div>
</main>
<?php get_footer(); ?>
"""

SINGLE = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
if ( is_singular( 'post' ) ) {
	teya_kids_breadcrumb_jsonld( array(
		array( 'name' => 'Главная', 'url' => home_url( '/' ) ),
		array( 'name' => 'Блог', 'url' => home_url( '/blog/' ) ),
		array( 'name' => get_the_title(), 'url' => get_permalink() ),
	) );
}
?>
<main id="primary" class="section">
<article <?php post_class( 'container prose article-page' ); ?>>
<header><h1><?php the_title(); ?></h1></header>
<div class="entry-content"><?php the_content(); ?></div>
<p class="article-cta"><?php teya_kids_cta( home_url( '/probnoe/' ), 'Записаться на пробное', 'btn btn-lime' ); ?></p>
</article>
</main>
<?php get_footer(); ?>
"""

PAGE_GENERIC = """<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="primary" class="section"><div class="container prose">
<?php while ( have_posts() ) { the_post(); the_content(); } ?>
</div></main>
<?php get_footer(); ?>
"""

ARCHIVE = """<?php get_header(); ?><main id="primary" class="section"><div class="container"><?php if(have_posts()){while(have_posts()){the_post();get_template_part('template-parts/content/content');}}?></div></main><?php get_footer(); ?>"""
SEARCH = """<?php get_header(); ?><main id="primary" class="section"><div class="container"><?php get_search_form(); if(have_posts()){while(have_posts()){the_post();get_template_part('template-parts/content/content');}}?></div></main><?php get_footer(); ?>"""
SEARCHFORM = """<?php ?><form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>"><label><span class="screen-reader-text">Поиск</span><input type="search" name="s" value="<?php echo get_search_query(); ?>"></label><button type="submit" class="btn btn-lime">Искать</button></form>"""
PAGE_404 = """<?php get_header(); ?><main id="primary" class="section"><div class="container"><h1>Страница не найдена</h1><p><a href="<?php echo esc_url(home_url('/')); ?>">На главную</a></p></div></main><?php get_footer(); ?>"""
COMMENTS = """<?php if ( ! defined( 'ABSPATH' ) ) { exit; } if ( comments_open() || get_comments_number() ) { comments_template(); } ?>"""
TPL_CONTENT = """<?php the_title('<h2>','</h2>'); the_content(); ?>"""
TPL_NONE = """<?php ?><p>Ничего не найдено.</p>"""

DIST_JS = """(function(){
var banner=document.getElementById('cookie-banner');
var accept=document.getElementById('cookie-accept');
if(banner&&!localStorage.getItem('teya_cookies_ok')){banner.hidden=false;}
if(accept){accept.addEventListener('click',function(){localStorage.setItem('teya_cookies_ok','1');banner.hidden=true;});}
document.querySelectorAll('[data-accordion]').forEach(function(acc){
  acc.querySelectorAll('.accordion-item').forEach(function(item){
    item.addEventListener('click',function(){
      acc.querySelectorAll('.accordion-item').forEach(function(i){i.classList.remove('active');});
      item.classList.add('active');
    });
  });
});
document.querySelectorAll('.toggle').forEach(function(t){
  var hidden=t.parentElement.querySelector('input[name=contact_method]');
  t.querySelectorAll('.toggle-btn').forEach(function(btn){
    btn.addEventListener('click',function(){
      t.querySelectorAll('.toggle-btn').forEach(function(b){b.classList.remove('active');});
      btn.classList.add('active');
      if(hidden)hidden.value=btn.dataset.value;
    });
  });
});
document.querySelectorAll('.teya-lead-form').forEach(function(form){
  form.addEventListener('submit',function(e){
    e.preventDefault();
    var msg=form.querySelector('.form-msg');
    var fd=new FormData(form);
    fd.append('action','teya_kids_lead');
    fd.append('nonce',(window.teyaKids&&teyaKids.nonce)||'');
    fetch((window.teyaKids&&teyaKids.ajaxUrl)||'/wp-admin/admin-ajax.php',{method:'POST',body:fd,credentials:'same-origin'})
    .then(function(r){return r.json();})
    .then(function(j){
      if(j.success){msg.textContent=j.data.message;msg.className='form-msg ok';form.reset();}
      else{msg.textContent=(j.data&&j.data.message)||'Ошибка';msg.className='form-msg err';}
    }).catch(function(){msg.textContent='Не удалось отправить';msg.className='form-msg err';});
  });
});
var toggle=document.querySelector('.nav-toggle');
var mobile=document.getElementById('mobile-nav');
if(toggle&&mobile){toggle.addEventListener('click',function(){var o=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!o));mobile.hidden=o;});}
if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){document.querySelectorAll('.hero-visual img').forEach(function(i){i.style.animation='none';});}
})();
"""

DIST_CSS = r""":root{--bg:#FAFAF7;--lime:#B8FF3C;--pink:#FF3CAC;--yellow:#FFE066;--sky:#5BC0FF;--text:#111;--muted:#555;--white:#FFF;--font-d:"Russo One",sans-serif;--font-b:Nunito,sans-serif;--radius:24px;--shadow:0 12px 40px rgba(17,17,17,.08)}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;font-family:var(--font-b);background:var(--bg);color:var(--text);line-height:1.55}
.container{max-width:1200px;margin:0 auto;padding:0 40px}
@media(max-width:768px){.container{padding:0 16px}}
h1,h2,h3{font-family:var(--font-d);letter-spacing:-.03em;line-height:1.1}
.highlight{background:var(--lime);padding:4px 14px;border-radius:9999px;display:inline-block}
.btn{display:inline-block;font-weight:700;font-size:16px;padding:16px 32px;border-radius:9999px;text-decoration:none;border:none;cursor:pointer;font-family:var(--font-b);transition:transform .2s}
.btn-lime{background:var(--lime);color:var(--text)}
.btn-lime:hover{transform:translateY(-1px);filter:brightness(.95)}
.btn-ghost{background:transparent;border:2px solid var(--text);color:var(--text);margin-left:12px}
.btn-block{display:block;width:100%;text-align:center;margin-left:0}
.site-header{position:sticky;top:0;z-index:100;background:var(--bg);padding:16px 0;border-bottom:1px solid rgba(17,17,17,.06)}
.site-header .inner{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.logo{font-family:var(--font-d);font-size:22px;text-decoration:none;color:var(--text)}
.nav-list{list-style:none;display:flex;gap:20px;margin:0;padding:0;flex-wrap:wrap}
.nav-list a{text-decoration:none;color:var(--text);font-weight:600;font-size:15px}
.menu-item-cta{margin-left:8px}
.nav-toggle{display:none;background:none;border:0;width:40px;height:40px}
.mobile-nav{padding:16px;background:var(--white);border-top:1px solid rgba(17,17,17,.08)}
.mobile-nav .nav-list{flex-direction:column}
@media(max-width:900px){.nav{display:none}.nav-toggle{display:block}.menu-item-cta{display:none}}
.hero{position:relative;padding:60px 0 100px;overflow:hidden}
.hero-grid{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:end}
.hero h1{font-size:clamp(32px,5vw,56px);margin-bottom:20px}
.hero-sub,.lead{font-size:18px;color:var(--muted);max-width:560px}
.hero-ctas{margin-top:24px}
.hero-visual{position:relative;min-height:420px}
.hero-visual img{position:relative;z-index:3;width:100%;max-width:380px;margin:0 auto;display:block;animation:float 4s ease-in-out infinite alternate}
.blob{position:absolute;z-index:1;border-radius:50%}
.blob-pink{width:320px;height:300px;background:var(--pink);opacity:.4;top:10%;right:0;border-radius:60% 40% 55% 45%;animation:blobDrift 12s ease-in-out infinite}
.blob-lime{width:200px;height:200px;background:var(--lime);opacity:.45;bottom:5%;left:0;border-radius:45% 55% 40% 60%}
.blob-sky{width:140px;height:140px;background:var(--sky);opacity:.4;top:40%;left:30%}
.benefits-blob{top:-60px;right:10%;width:180px;height:180px;opacity:.35}
@keyframes float{from{transform:translateY(0)}to{transform:translateY(-8px)}}
@keyframes blobDrift{0%,100%{transform:translate(0,0)}50%{transform:translate(8px,-6px)}}
.stats{background:#FFF9E6;padding:48px 0;position:relative;z-index:2}
.stats-overlap{margin-top:-48px}
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;text-align:center}
.stats-grid strong{font-family:var(--font-d);font-size:48px;display:block}
.section{padding:80px 0;position:relative}
.section h2{font-size:clamp(28px,4vw,40px);margin-bottom:24px}
.benefits{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.card{background:var(--white);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}
.card img{width:100%;height:200px;object-fit:cover;object-position:top center}
.card-body{padding:24px}
.card.yellow{border-top:6px solid var(--yellow)}
.card.green{border-top:6px solid var(--lime)}
.card.pink{border-top:6px solid var(--pink)}
.card a{text-decoration:none;color:inherit}
.wave-divider{height:48px;background:var(--white);clip-path:ellipse(80% 100% at 50% 100%)}
.accordion-item{border-radius:20px;padding:20px 24px;margin-bottom:12px;border:2px solid rgba(17,17,17,.12);cursor:pointer;transition:background .3s}
.accordion-item.active{background:var(--lime);border-color:var(--lime)}
.accordion-item .num{font-family:var(--font-d);font-size:14px;opacity:.7}
.how-wrap{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
.program-wash{background:linear-gradient(180deg,#fff 0%,#E8F7FF 100%)}
.module-chips{display:flex;flex-wrap:wrap;gap:12px;list-style:none;padding:0;margin:24px 0}
.module-chips li{background:var(--white);padding:12px 18px;border-radius:16px;box-shadow:var(--shadow)}
.form-section{padding:80px 0}
.form-panel{display:grid;grid-template-columns:1.2fr .8fr;gap:40px;background:var(--white);border-radius:32px;box-shadow:0 20px 60px rgba(17,17,17,.1);padding:48px;position:relative;overflow:hidden}
.form-panel input,.form-panel select{width:100%;padding:14px 18px;border-radius:16px;border:2px solid #E8E8E3;margin-bottom:16px;font-family:var(--font-b);font-size:16px}
.field span{display:block;font-weight:600;margin-bottom:6px;font-size:14px}
.toggle{display:flex;gap:8px;background:#F0F0EB;padding:6px;border-radius:16px;margin-bottom:20px}
.toggle-btn{flex:1;padding:10px;border:none;border-radius:12px;font-weight:600;cursor:pointer;background:transparent;font-family:var(--font-b)}
.toggle-btn.active{background:var(--lime)}
.hp-field{position:absolute;left:-9999px;height:0;width:0;opacity:0}
.consent{font-size:14px;display:flex;gap:8px;align-items:flex-start;margin-bottom:16px}
.form-visual{position:relative;min-height:360px;display:flex;align-items:center;justify-content:center}
.form-visual img{position:relative;z-index:2;max-height:360px;width:auto}
.form-blob{right:10%;top:20%;width:120px;height:120px}
.form-blob2{left:5%;bottom:10%;width:100px;height:100px}
.blog-diagonal{clip-path:polygon(0 8%,100% 0,100% 100%,0 100%)}
.blog-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.blog-card img{width:100%;aspect-ratio:16/9;object-fit:cover}
.site-footer{background:#111;color:#fff}
.footer-cta-strip{padding:40px 0;text-align:center;background:#1a1a1a}
.footer-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:32px;padding:48px 0}
.footer-col h3{font-size:18px;margin-bottom:12px}
.footer-col ul{list-style:none;padding:0;margin:0}
.footer-col a{color:#ddd;text-decoration:none}
.footer-legal{padding:24px 0 48px;border-top:1px solid rgba(255,255,255,.1);font-size:14px}
.footer-legal a{color:#ccc}
.cookie-banner{position:fixed;bottom:0;left:0;right:0;background:#111;color:#fff;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;z-index:999;flex-wrap:wrap}
.cookie-banner a{color:var(--lime)}
.prose{max-width:760px}
.prose p,.prose li{color:var(--muted);font-size:18px}
.page-hero{padding:60px 0 40px}
.sky-wash{background:linear-gradient(180deg,var(--bg),rgba(91,192,255,.15))}
.roadmap-img{width:100%;height:auto;border-radius:var(--radius);margin:24px 0;box-shadow:var(--shadow)}
.modules-grid .container{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.module-panel{padding:28px;border-radius:var(--radius);color:var(--text)}
.module-panel.pink{background:rgba(255,60,172,.15)}
.module-panel.yellow{background:rgba(255,224,102,.35)}
.module-panel.green{background:rgba(184,255,60,.25)}
.module-panel.sky{background:rgba(91,192,255,.2)}
.pink-strip{background:rgba(255,60,172,.12)}
.bento-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.bento{padding:28px;border-radius:var(--radius);box-shadow:var(--shadow)}
.bento.yellow{background:rgba(255,224,102,.35)}
.bento.green{background:rgba(184,255,60,.25)}
.bento.sky{background:rgba(91,192,255,.2)}
.format-hero-grid{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:center}
.format-mascot img{max-width:228px;opacity:.95}
.parent-callout{background:rgba(91,192,255,.13);padding:48px 0}
.pricing-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.price-card{background:var(--white);padding:32px;border-radius:var(--radius);box-shadow:var(--shadow);border-top:6px solid var(--lime)}
.price-card.pink-top{border-top-color:var(--pink)}
.price-card.sky-top{border-top-color:var(--sky)}
.tarify-grid{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:center}
.data-table{width:100%;border-collapse:collapse;margin:16px 0}
.data-table th,.data-table td{border:1px solid rgba(17,17,17,.12);padding:12px;text-align:left}
.faq-item{border:1px solid rgba(17,17,17,.12);border-radius:16px;padding:16px 20px;margin-bottom:12px;background:var(--white)}
.faq-item summary{cursor:pointer;font-weight:700}
.form-msg.ok{color:green}.form-msg.err{color:#c00}
.screen-reader-text{position:absolute;left:-9999px}
.cta-section{text-align:center}
.trust-list{list-style:none;padding:0}
.trust-list li{padding:8px 0;font-weight:600}
.legal-page h1{font-size:36px}
@media(max-width:900px){
.hero-grid,.how-wrap,.form-panel,.benefits,.blog-grid,.stats-grid,.footer-grid,.bento-grid,.pricing-grid,.modules-grid .container{grid-template-columns:1fr}
.btn-ghost{margin-left:0;margin-top:12px;display:inline-block}
.stats-overlap{margin-top:0}
.hero-visual{min-height:280px}
.format-hero-grid,.tarify-grid{grid-template-columns:1fr}
}
@media(prefers-reduced-motion:reduce){.hero-visual img,.blob-pink{animation:none}}
"""
