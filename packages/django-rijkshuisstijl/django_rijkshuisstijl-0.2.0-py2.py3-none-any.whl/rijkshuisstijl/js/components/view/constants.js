import BEM from 'bem.js';

/** @const {string} */
export const BLOCK_VIEW = 'view';

/** @const {string} */
export const MODIFIER_MENU_OPEN = 'menu-open';

/** @const {HTMLHtmlElement} */
export const VIEW = BEM.getBEMNode(BLOCK_VIEW);

/** @const {string} */
export const BLOCK_NAVIGATION_BAR = 'navigation-bar';

/** @const {HTMLElement} */
export const NAVIGATION_BAR = BEM.getBEMNode(BLOCK_NAVIGATION_BAR);
