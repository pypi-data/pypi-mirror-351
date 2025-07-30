//jshint ignore:start
import {FAKE_LINKS} from './constants';

// Start!
if (FAKE_LINKS.length) {
    import(/* webpackChunkName: 'fake-link' */ './fake-link');
}
