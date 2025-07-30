//jshint ignore:start
import {SELECT_ALLS, TOGGLES} from './constants';

// Start!
if (SELECT_ALLS.length) {
    import(/* webpackChunkName: 'select-all' */ './select-all');
}

if (TOGGLES.length) {
    import(/* webpackChunkName: 'toggle' */ './toggle');
}
