/**
 * Copyright 2021 Charly Delay <charly@codesink.dev> (@0xcharly)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include QMK_KEYBOARD_H

enum charybdis_keymap_layers {
    LAYER_BASE = 0,
    LAYER_FUNCTION,
    LAYER_NAVIGATION,
    LAYER_POINTER,
    LAYER_NUMERAL,
    LAYER_SYMBOLS,
    LAYER_GAMING,
    LAYER_GAMING_AUX,
};

#define SPC_NAV LT(LAYER_NAVIGATION, KC_SPC)
#define FUN_BSPC LT(LAYER_FUNCTION, KC_ENT)
#define PTR_TG TG(LAYER_POINTER)
#define ESC_SYM LT(LAYER_SYMBOLS, KC_ESC)
#define TAB_NUM LT(LAYER_NUMERAL, KC_TAB)
#define ESC_AUX LT(LAYER_GAMING_AUX, KC_ESC)

#ifndef POINTING_DEVICE_ENABLE
#    define DRGSCRL KC_NO
#    define DPI_MOD KC_NO
#    define DPI_RMOD KC_NO
#    define S_D_MOD KC_NO
#    define S_D_RMOD KC_NO
#    define SNIPING KC_NO
#    define SNP_TOG KC_NO
#    define DRG_TOG KC_NO
#endif // !POINTING_DEVICE_ENABLE

// clang-format off
/** \brief Colemak layout (3 rows, 10 columns). */
#define LAYOUT_LAYER_BASE                                                                     \
       KC_Q,    KC_W,    KC_F,    KC_P,    KC_G,    KC_J,    KC_L,    KC_U,    KC_Y, KC_QUOT, \
       KC_A,    KC_R,    KC_S,    KC_T,    KC_D,    KC_H,    KC_N,    KC_E,    KC_I, KC_O,    \
       KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_K,    KC_M, KC_COMM,  KC_DOT, KC_SLSH, \
                      KC_BSPC, SPC_NAV, FUN_BSPC, ESC_SYM, TAB_NUM

/** Convenience row shorthands. */
#define _______________DEAD_HALF_ROW_______________ XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX
#define ______________HOME_ROW_GACS_L______________ KC_LGUI, KC_LALT, KC_LCTL, KC_LSFT, XXXXXXX
#define ______________HOME_ROW_GACS_R______________ XXXXXXX, KC_LSFT, KC_LCTL, KC_LALT, KC_LGUI

/*
 * Layers used on the Charybdis Nano.
 *
 * These layers started off heavily inspired by the Miryoku layout, but trimmed
 * down and tailored for a stock experience that is meant to be fundation for
 * further personalization.
 *
 * See https://github.com/manna-harbour/miryoku for the original layout.
 */

/**
 * \brief Function + Media layer (merged).
 *
 * Right-hand: F-keys in a row-major block (F1-F9) with F10-F12 on the
 * outer column.  Left-hand: media controls (prev/vol/mute/vol/next on
 * home row, EE_CLR + QK_BOOT on bottom row).  Thumb: play/pause.
 */
#define LAYOUT_LAYER_FUNCTION                                                                 \
    _______________DEAD_HALF_ROW_______________, XXXXXXX,   KC_F7,   KC_F8,   KC_F9,  KC_F12, \
    KC_MPRV, KC_VOLD, KC_MUTE, KC_VOLU, KC_MNXT, XXXXXXX,   KC_F4,   KC_F5,   KC_F6,  KC_F11, \
    XXXXXXX, QK_BOOT, EE_CLR,   PTR_TG, XXXXXXX, XXXXXXX,   KC_F1,   KC_F2,   KC_F3,  KC_F10, \
                      KC_BSPC, _______, _______, KC_MPLY, PTR_TG

/**
 * \brief Mouse emulation and pointer functions.
 *
 * Physical thumb layout: 3 keys on the left half, 2 on the right half,
 * with the trackball at the rightmost right-half position (replacing a
 * key).  The right thumb operates the trackball, so all mouse buttons
 * live on the free left thumb.  Thumb order on the right half is
 * inner→outer→trackball, so PTR_TG sits on the outer key (closest to
 * the ball) for both entry (function layer) and exit (this layer).
 *
 * Left hand: mouse buttons (home row), DPI/scroll/snipe (bottom row).
 * Right hand: GACS modifiers (home row), scroll/DPI (bottom row),
 *             browser nav (top row).
 */
#define LAYOUT_LAYER_POINTER                                                                  \
    XXXXXXX, XXXXXXX, KC_WWW_FORWARD, KC_WWW_BACK, XXXXXXX, XXXXXXX, KC_WWW_BACK, KC_WWW_FORWARD, XXXXXXX, XXXXXXX, \
    XXXXXXX, MS_BTN3, MS_BTN2, MS_BTN1, XXXXXXX, ______________HOME_ROW_GACS_R______________, \
    DPI_MOD, DPI_RMOD, DRGSCRL, S_D_MOD, S_D_RMOD, XXXXXXX, MS_BTN1, MS_BTN2, MS_BTN3, XXXXXXX, \
                      SNIPING,  PTR_TG, DRGSCRL,  PTR_TG, DRGSCRL

/**
 * \brief Navigation layer.
 *
 * Primary right-hand layer (left home thumb) is navigation and editing. Cursor
 * keys are on the home position, line and page movement below, clipboard above,
 * caps lock and insert on the inner column. Thumb keys are duplicated from the
 * base layer to avoid having to layer change mid edit and to enable auto-repeat.
 */
#define LAYOUT_LAYER_NAVIGATION                                                               \
    LCTL(KC_Z), LCTL(KC_X), LCTL(KC_C), LCTL(KC_V), LCTL(KC_A), _______________DEAD_HALF_ROW_______________, \
    ______________HOME_ROW_GACS_L______________, KC_CAPS, KC_LEFT, KC_DOWN,   KC_UP, KC_RGHT, \
    XXXXXXX, XXXXXXX, TO(LAYER_GAMING),  PTR_TG, XXXXXXX,  KC_INS, KC_HOME, KC_PGUP, KC_PGDN,  KC_END, \
                      XXXXXXX, _______, XXXXXXX,  KC_ENT, KC_BSPC

/**
 * \brief Numeral layout.
 *
 * Primary left-hand layer (right home thumb) is numerals and symbols. Numerals
 * are in the standard numpad locations with symbols in the remaining positions.
 * Also provides entry to the gaming layer.
 */
#define LAYOUT_LAYER_NUMERAL                                                                  \
    KC_RBRC,  KC_EQL, KC_SCLN, KC_BSLS, KC_LBRC, _______________DEAD_HALF_ROW_______________, \
    KC_5,       KC_4,    KC_3,    KC_2,    KC_1, ______________HOME_ROW_GACS_R______________, \
    KC_0,       KC_9,    KC_8,    KC_7,    KC_6, _______________DEAD_HALF_ROW_______________, \
             TO(LAYER_GAMING),  KC_GRV, KC_MINS, XXXXXXX, _______

/**
 * \brief Symbols layer.
 *
 * Secondary left-hand layer is the shift-equivalent of the numeral layer.
 * Each left-hand key on this layer maps to the shifted version of the
 * same position on the numeral layer, making symbol locations predictable.
 * Thumbs mirror: grave becomes tilde, minus becomes underscore.
 */
#define LAYOUT_LAYER_SYMBOLS                                                                  \
    KC_RCBR,  KC_LCBR, KC_COLN, KC_PLUS,  KC_PIPE, _______________DEAD_HALF_ROW_______________, \
    KC_PERC,   KC_DLR, KC_HASH,   KC_AT,  KC_EXLM, ______________HOME_ROW_GACS_R______________, \
    KC_RPRN,  KC_LPRN, KC_ASTR, KC_AMPR,  KC_CIRC, _______________DEAD_HALF_ROW_______________, \
                      TO(LAYER_GAMING), KC_TILD, KC_UNDS, _______, XXXXXXX

/**
 * \brief Gaming layer.
 *
 * Last left-hand layer that largely mimics the QWERTY layout (right shifted one col), for gaming.
 *
 */
#define LAYOUT_LAYER_GAMING                                                                   \
    KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    KC_Y,    KC_U,    KC_I,    KC_O,    \
    KC_LSFT, KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    KC_H,    KC_J,    KC_K,    KC_L,    \
    KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_N,    KC_M, KC_COMM,  KC_DOT,    KC_ENT,  \
                   KC_LCTL,  KC_SPC, MO(LAYER_GAMING_AUX), ESC_AUX, TO(LAYER_BASE)

/**
 * \brief Gaming-aux layer.
 *
 * Aux gaming layer.
 *
 */
#define LAYOUT_LAYER_GAMING_AUX                                                               \
    KC_M,    KC_I,    KC_O,    KC_P,  KC_ESC, XXXXXXX,   KC_F7,   KC_F8,   KC_F9,  KC_F12, \
    KC_5,    KC_4,    KC_3,    KC_2,    KC_1, XXXXXXX,   KC_F4,   KC_F5,   KC_F6,  KC_F11, \
    KC_0,    KC_9,    KC_8,    KC_7,    KC_6, XXXXXXX,   KC_F1,   KC_F2,   KC_F3,  KC_F10, \
                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX

/**
 * \brief Add Home Row mod to a layout.
 *
 * Expects a 10-key per row layout.  Adds support for GACS (Gui, Alt, Ctl, Shift)
 * home row.  The layout passed in parameter must contain at least 20 keycodes.
 *
 * This is meant to be used with `LAYER_ALPHAS_QWERTY` defined above, eg.:
 *
 *     HOME_ROW_MOD_GACS(LAYER_ALPHAS_QWERTY)
 */
#define _HOME_ROW_MOD_GACS(                                            \
    L00, L01, L02, L03, L04, R05, R06, R07, R08, R09,                  \
    L10, L11, L12, L13, L14, R15, R16, R17, R18, R19,                  \
    ...)                                                               \
             L00,         L01,         L02,         L03,         L04,  \
             R05,         R06,         R07,         R08,         R09,  \
      LGUI_T(L10), LALT_T(L11), LCTL_T(L12), LSFT_T(L13),        L14,  \
             R15,  RSFT_T(R16), RCTL_T(R17), RALT_T(R18), RGUI_T(R19), \
      __VA_ARGS__
#define HOME_ROW_MOD_GACS(...) _HOME_ROW_MOD_GACS(__VA_ARGS__)

#define LAYOUT_wrapper(...) LAYOUT(__VA_ARGS__)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [LAYER_BASE] = LAYOUT_wrapper(
    HOME_ROW_MOD_GACS(LAYOUT_LAYER_BASE)
  ),
  [LAYER_FUNCTION] = LAYOUT_wrapper(LAYOUT_LAYER_FUNCTION),
  [LAYER_NAVIGATION] = LAYOUT_wrapper(LAYOUT_LAYER_NAVIGATION),
  [LAYER_POINTER] = LAYOUT_wrapper(LAYOUT_LAYER_POINTER),
  [LAYER_NUMERAL] = LAYOUT_wrapper(LAYOUT_LAYER_NUMERAL),
  [LAYER_SYMBOLS] = LAYOUT_wrapper(LAYOUT_LAYER_SYMBOLS),
  [LAYER_GAMING] = LAYOUT_wrapper(LAYOUT_LAYER_GAMING),
  [LAYER_GAMING_AUX] = LAYOUT_wrapper(LAYOUT_LAYER_GAMING_AUX),
};
// clang-format on
