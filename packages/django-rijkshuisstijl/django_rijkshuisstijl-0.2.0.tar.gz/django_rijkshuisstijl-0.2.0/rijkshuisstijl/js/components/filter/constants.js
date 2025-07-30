import BEM from 'bem.js';

/** @const {string} */
export const BLOCK_FILTER = 'filter';

/** @const {string} */
export const ELEMENT_INPUT = 'input';

/** @const {string} */
export const MODIFIER_CLASS_ONLY = 'class-only';

/** @const {string} */
export const MODIFIER_FILTER = 'filter';

/** @const {string} */
export const MODIFIER_MATCH = 'match';

/** @const {string} */
export const MODIFIER_NO_MATCH = 'nomatch';

/** @const {NodeList} */
export const FILTERS = BEM.getBEMNodes(BLOCK_FILTER, false, MODIFIER_FILTER);
