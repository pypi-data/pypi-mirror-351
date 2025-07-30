//jshint ignore:start
import {TABS} from './constants';

// Start!
if (TABS.length) {
    import(/* webpackChunkName: 'tabs' */ './tabs');
}
