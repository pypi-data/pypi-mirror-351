//jshint ignore:start
import {DATAGRIDS, DATAGRID_EXPORTS, DATAGRID_FILTERS} from './constants';

// Start!
if (DATAGRIDS.length) {
    import(/* webpackChunkName: 'datagrid-edit' */ './datagrid-edit');
}

if (DATAGRID_EXPORTS.length) {
    import(/* webpackChunkName: 'datagrid-export' */ './datagrid-export');
}

if (DATAGRID_FILTERS.length) {
    import(/* webpackChunkName: 'datagrid-filter' */ './datagrid-filter');
}
