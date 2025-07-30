import BEM from 'bem.js';

/** @const {string} */
export const BLOCK_STICKY_DETECT = 'sticky-detect';

/** @const {string} */
export const MODIFIER_STUCK = 'stuck';

/** @const {NodeList} */
export const STICKY_DETECTS = BEM.getBEMNodes(BLOCK_STICKY_DETECT);
