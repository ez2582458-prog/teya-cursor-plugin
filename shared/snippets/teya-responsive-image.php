<?php
/**
 * Teya responsive image helper (copy into the theme as inc/responsive-image.php
 * and require it from functions.php).
 *
 * Usage:
 *   echo teya_img( 'assets/images/hero-home.webp', 'Фасад жилого дома после ремонта', array( 'hero' => true, 'sizes' => '100vw' ) );
 *   echo teya_img( 'assets/images/block-roof.webp', 'Кровля после ремонта' ); // lazy by default
 *
 * Always outputs: src, srcset (from -480w/-800w/-1200w.webp variants written by
 * teya_image_optimize.py / package_mcp_assets.py), sizes, width, height, alt,
 * decoding="async", and loading="lazy" (or fetchpriority="high" + eager for the hero/LCP).
 * For media-library images use wp_get_attachment_image() — WordPress adds srcset itself.
 */
if ( ! function_exists( 'teya_img' ) ) {
	function teya_img( $rel_path, $alt, $args = array() ) {
		$args = wp_parse_args(
			$args,
			array(
				'hero'  => false,
				'sizes' => '(max-width: 768px) 100vw, 50vw',
				'class' => '',
			)
		);
		$rel_path = ltrim( $rel_path, '/' );
		$dir      = get_template_directory();
		$uri      = get_template_directory_uri();
		$file     = $dir . '/' . $rel_path;
		$width    = 0;
		$height   = 0;
		if ( file_exists( $file ) ) {
			$size = @getimagesize( $file );
			if ( $size ) {
				$width  = (int) $size[0];
				$height = (int) $size[1];
			}
		}
		$info   = pathinfo( $rel_path );
		$srcset = array();
		foreach ( array( 480, 800, 1200 ) as $w ) {
			$variant = $info['dirname'] . '/' . $info['filename'] . '-' . $w . 'w.' . $info['extension'];
			if ( $w < $width && file_exists( $dir . '/' . $variant ) ) {
				$srcset[] = esc_url( $uri . '/' . $variant ) . ' ' . $w . 'w';
			}
		}
		if ( $srcset && $width ) {
			$srcset[] = esc_url( $uri . '/' . $rel_path ) . ' ' . $width . 'w';
		}
		$attrs = array(
			'src'      => esc_url( $uri . '/' . $rel_path ),
			'alt'      => esc_attr( $alt ),
			'decoding' => 'async',
		);
		if ( $width && $height ) {
			$attrs['width']  = $width;
			$attrs['height'] = $height;
		}
		if ( $srcset ) {
			$attrs['srcset'] = implode( ', ', $srcset );
			$attrs['sizes']  = esc_attr( $args['sizes'] );
		}
		if ( $args['hero'] ) {
			$attrs['loading']       = 'eager';
			$attrs['fetchpriority'] = 'high';
		} else {
			$attrs['loading'] = 'lazy';
		}
		if ( $args['class'] ) {
			$attrs['class'] = esc_attr( $args['class'] );
		}
		$html = '<img';
		foreach ( $attrs as $k => $v ) {
			$html .= ' ' . $k . '="' . $v . '"';
		}
		return $html . '>';
	}
}
