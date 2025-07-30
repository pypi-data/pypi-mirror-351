import {FORM_CONTROLS} from './constants';

/**
 * Keeps track of inputs and their values and copies those to data attributes of node.
 * @class
 */
class FormControl {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** @type {HTMLElement} */
        this.node = node;

        this.bindEvents();
        this.update();
    }

    /**
     * Returns all inputs, selects and textareas within this.node.
     * @return {HTMLElement[]}
     */
    getInputs() {
        return [...this.node.querySelectorAll('input, select, textarea')];
    }

    /**
     * Returns all inputs, selects and textareas within this.node with a name attribute set.
     * @return {HTMLElement[]}
     */
    getNamedInputs() {
        return this.getInputs()
            .filter(input => input.name);
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener('change', this.update.bind(this));
        this.node.addEventListener('input', this.update.bind(this));
        this.node.addEventListener('click', this.update.bind(this));
        this.node.addEventListener('touchend', this.update.bind(this));
        this.node.addEventListener('keyup', this.update.bind(this));
    }

    /**
     * Copies inputs select and textreas name and values to data attributes of this.node.
     */
    update() {
        setTimeout(this._update.bind(this));
    }

    /**
     * @private
     */
    _update() {
        try {
            const namedInputs = this.getNamedInputs();

            // Set names (data-input-names="foo,bar").
            const namedInputNames = [...new Set(namedInputs.map(namedInput => namedInput.name))];

            if (namedInputNames.length) {
                this.node.dataset.inputNames = namedInputNames;
            } else {
                delete this.node.dataset.inputNames;
            }


            // Set values (data-foo-value="bar").
            namedInputs.forEach(namedInput => {
                const datasetItem = `${namedInput.name}Value`;
                let value = namedInput.value;

                // Checkbox
                if (namedInput.type === 'checkbox' && !namedInput.checked) {
                    return;
                }

                // Radio
                if (namedInput.type === 'radio' && !namedInput.checked) {
                    return;
                }

                // Select multiple
                if (namedInput.multiple && namedInput.options) {
                    const values = [...namedInput.options]
                        .filter(option => option.selected)
                        .map(selectedOption => selectedOption.value || selectedOption.textContent);

                    if (values.length) {
                        value = values;
                    } else {
                        value = false;
                    }
                }

                if (value) {
                    this.node.dataset[datasetItem] = value;
                } else {
                    delete this.node.dataset[datasetItem];
                }
            });


            // Checked
            namedInputs.filter(namedInput => namedInput.checked && namedInput.value)
                .forEach(checkedInput => {
                    const datasetItem = `${checkedInput.name}Value`;
                    this.node.dataset[datasetItem] = checkedInput.value;
                });
        } catch (e) {
            const str = this.node.dataset.inputNames || this.node.id || this.node;
            console.warn(`Unable to inspect form control (${str}), got error: ${e}.`);
        }

        // IE11 Does not trigger a paint when using the generated data attributes in CSS in certain conditions.
        // We force a repaint by adding and removing an additional class.
        this.node.classList.add('PAINT');
        this.node.classList.remove('PAINT');
    }
}


// Start!
[...FORM_CONTROLS].forEach(node => new FormControl(node));
