/**
 * Class containging utility functions for tests.
 * @class
 */
export class Utils {
    /**
     * Returns a modified version of class target.
     * Modified version's constructor is not called by default.
     *
     * @example:
     *
     * let this.Foo = Utils.createTestableClass(Foo);
     * this.foo = new this.Foo();
     * this.foo.constructor()
     *
     * @param {Function} target
     * @returns {Function}
     */
    static createTestableClass(target) {
        let proto = target.prototype;
        let fake = function () {};
        fake.prototype = proto;
        return fake;
    }

    /**
     * Returns a promise which resolves after ms milliseconds.
     * Even if ms=0 this will result in asynchronous code
     * and is pushed to the end of the event loop.
     *
     * This is useful when assertions should be made after another
     * asynchronous event.
     *
     * If asynchronous code is used, always pass the "done"
     * parameter to a Jasmine it() callback and call it manually
     * when done.
     *
     * @example:
     *
     * it('should run async', (done) => {
     *         let bool = false;
     *         setTimeout(() => bool = true, 100);
     *
     *         Utils.delay(100)
     *             .then(() => {
     *                 expect(bool).toBeTruthy();
     *                 done();
     *             });
     * });
     *
     * @param [ms=0]
     * @returns {Promise}
     */
    static delay(ms=0) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
