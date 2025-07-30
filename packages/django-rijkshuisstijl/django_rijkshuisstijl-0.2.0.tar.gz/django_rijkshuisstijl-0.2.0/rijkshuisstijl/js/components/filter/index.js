//jshint ignore:start
import {FILTERS} from './constants';

// Start!
if (FILTERS.length) {
    import(/* webpackChunkName: 'filter' */ './filter');
}
