import BEM from 'bem.js';

/** @const {string} Form block name. */
export const BLOCK_FORM = 'form';

/** @const {NodeList} All the forms */
export const FORMS = BEM.getBEMNodes(BLOCK_FORM);

/** @const {string} Form control block name. */
export const BLOCK_FORM_CONTROL = 'form-control';

/** @const {NodeList} All the form controls. */
export const FORM_CONTROLS = BEM.getBEMNodes(BLOCK_FORM_CONTROL);

/** @const {string} Input block name. */
export const BLOCK_INPUT = 'input';

/** @const {string} Date range modifier name. */
export const MODIFIER_DATE = 'date';

/** @const {string} Date range modifier name. */
export const MODIFIER_DATE_RANGE = 'daterange';

/** @const {NodeList} All the date inputs. */
export const DATE_INPUTS = document.querySelectorAll(BEM.getBEMSelector(BLOCK_INPUT) + '[type="date"]');

/** @const {NodeList} All the date range inputs.. */
export const DATE_RANGE_INPUTS = BEM.getBEMNodes(BLOCK_INPUT, false, MODIFIER_DATE_RANGE);

/** @const {NodeList} All the time inputs. */
export const TIME_INPUTS = document.querySelectorAll(BEM.getBEMSelector(BLOCK_INPUT) + '[type="time"]');

/** @const {string} Filepicker element name. */
export const ELEMENT_FILEPICKER = 'filepicker';

/** @const {NodeList} All the file pickers. */
export const INPUT_FILEPICKERS = BEM.getBEMNodes(BLOCK_INPUT, ELEMENT_FILEPICKER);

/** @const {string} Select block name. */
export const BLOCK_SELECT = 'select';

/** @const {NodeList} All the selects. */
export const SELECTS = BEM.getBEMNodes(BLOCK_SELECT);

/** @const {string} Modifier indicating that a select has a value set. */
export const MODIFIER_HAS_VALUE = 'has-value';

/** @const {string} Modifier indicating a select should trigger a navigation. */
export const MODIFIER_LINK = 'link';

/** @const {NodeList} Link selects. */
export const LINK_SELECTS = BEM.getBEMNodes(BLOCK_SELECT, false, MODIFIER_LINK);

/** @const {string} Textarea block name. */
export const BLOCK_TEXTAREA = 'textarea';

/** @const {NodeList} All the textareas. */
export const TEXTAREAS = BEM.getBEMNodes(BLOCK_TEXTAREA);

/** @const {number} Keycode for enter key. */
export const KEYCODE_ENTER = 13;
