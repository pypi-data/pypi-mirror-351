//jshint ignore:start
import {STICKY_DETECTS} from './constants';

// Start!
if (STICKY_DETECTS.length) {
    import(/* webpackChunkName: 'sticky-navigation-bar' */ './sticky-navigation-bar');
}
