import BEM from 'bem.js';

/** @const {string} */
export const BLOCK_DATAGRID = 'datagrid';

/** @const {NodeList} */
export const DATAGRIDS = BEM.getBEMNodes(BLOCK_DATAGRID);

/** @const {string} */
export const ELEMENT_CELL = 'cell';

export const MODIFIER_CHECKBOX = 'checkbox';

/** @const {string} */
export const ELEMENT_EXPORT = 'export';

/** @const {NodeList} */
export const DATAGRID_EXPORTS = BEM.getBEMNodes(BLOCK_DATAGRID, ELEMENT_EXPORT);

/** @const {string} */
export const ELEMENT_FILTER = 'filter';

/** @const {NodeList} */
export const DATAGRID_FILTERS = BEM.getBEMNodes(BLOCK_DATAGRID, ELEMENT_FILTER);

/** @const {NodeList} */
export const ELEMENT_FORM = 'form';

/** @const {NodeList} */
export const MODIFIER_ACTION = 'action';

/** @const {string} */
export const ELEMENT_ROW = 'row';

/** @const {string} */
export const MODIFIER_EDIT = 'edit';
