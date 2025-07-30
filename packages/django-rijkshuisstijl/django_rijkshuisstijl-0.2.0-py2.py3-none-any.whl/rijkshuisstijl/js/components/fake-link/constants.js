import BEM from 'bem.js';

/** @const {string} */
export const BLOCK_FAKE_LINK = 'fake-link';

/** @aconst {string} */
export const MODIFIER_DOUBLE_CLICK = 'double-click';

/** @const {NodeList} */
export const FAKE_LINKS = BEM.getBEMNodes(BLOCK_FAKE_LINK);
