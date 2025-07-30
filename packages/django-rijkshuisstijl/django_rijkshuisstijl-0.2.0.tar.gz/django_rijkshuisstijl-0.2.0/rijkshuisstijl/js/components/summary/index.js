//jshint ignore:start
import {SUMMARIES} from './constants';

// Start!
if (SUMMARIES.length) {
    import(/* webpackChunkName: 'summary' */ './summary');
}
