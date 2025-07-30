import BEM from 'bem.js';

/** @const {string} The paginator block name. */
export const BLOCK_PAGINATOR = 'paginator';

/** @const {string} The input block name. */
export const BLOCK_INPUT = 'input';

/** @const {NodeList} All the paginators */
export const PAGINATORS = BEM.getBEMNodes(BLOCK_PAGINATOR);
