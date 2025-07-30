import BEM from 'bem.js';

/** @const {string} */
export const BLOCK_SEARCH = 'search';

/** @const {string} */
export const ELEMENT_INPUT = 'input';

/** @const {string} Open modifier for BLOCK_SEARCH, indicates search widget is opened. */
export const MODIFIER_OPEN = 'open';

/** @const {NodeList} */
export const SEARCHES = BEM.getBEMNodes(BLOCK_SEARCH);
