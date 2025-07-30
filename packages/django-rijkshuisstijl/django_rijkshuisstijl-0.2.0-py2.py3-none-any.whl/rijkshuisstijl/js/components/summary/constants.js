import BEM from 'bem.js';

/** @const {string} The summary block name. */
export const BLOCK_SUMMARY = 'summary';

/** @const {string} The key value element name. */
export const ELEMENT_KEY_VALUE = 'key-value';

/** @const {string} The modifier making the value input visible. */
export const MODIFIER_EDIT = 'edit';

/** @const {NodeList} All the summaries. */
export const SUMMARIES = BEM.getBEMNodes(BLOCK_SUMMARY);
