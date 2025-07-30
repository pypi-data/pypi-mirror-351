import BEM from 'bem.js';

/** @const {string} */
export const BLOCK_SELECT_ALL = 'select-all';

/** @const {NodeList} */
export const SELECT_ALLS = BEM.getBEMNodes(BLOCK_SELECT_ALL);

/** @const {string} */
export const BLOCK_TOGGLE = 'toggle';

/** @const {NodeList} */
export const TOGGLES = BEM.getBEMNodes(BLOCK_TOGGLE);
