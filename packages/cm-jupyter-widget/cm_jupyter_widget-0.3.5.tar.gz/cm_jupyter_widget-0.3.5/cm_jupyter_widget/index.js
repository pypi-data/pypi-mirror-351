import clevermapsJsSdk from 'https://cdn.jsdelivr.net/npm/clevermaps-js-sdk@2.5.0/+esm';

function render({ model, el }) {
    let base_url = model.get('base_url');
    let view_url = model.get('view_url');
    let width = model.get('width');
    let height = model.get('height');
    let options_string = model.get('options');
    let options = JSON.parse(options_string);
    console.log('sdk options:', options);

    let div = document.createElement('div');
    div.setAttribute("id", "frameDiv");
    if (width) {
        div.style.width = width;
    }
    if (height) {
        div.style.height = height;
    }
    el.appendChild(div);

    const sdk = clevermapsJsSdk(base_url);
    console.log('sdk created:', sdk);

    const iframe = sdk.createIframe(view_url, options);
    console.log('iframe created:', iframe);

    sdk.renderIframe(div, iframe);
    console.log('iframe rendered in div:', div);

    // Add filter change listener
    iframe.message.addAddFilterListener(() => {
        model.set('filter_added', { timestamp: Date.now() });
    });

    model.on("change:command", () => {
        const command = model.get('command');
        if (!command || !command.type) return;

        switch (command.type) {
            case 'toggleFitAll':
                iframe.message.toggleFitAll();
                break;
            case 'addFilter':
                iframe.message.addFilter(command.definitionId, command.values, command.instanceId);
                break;
            case 'setFilter':
                iframe.message.setFilter(command.instanceId, command.value);
                break;
            case 'removeFilter':
                iframe.message.removeFilter(command.instanceId);
                break;
            case 'resetFilter':
                iframe.message.resetFilter(command.instanceId);
                break;
            case 'setState':
                iframe.setState(command.viewUrl);
                break;
            case 'openBookmarkModal':
                iframe.message.openBookmarkModal();
                break;
            case 'openExportModal':
                iframe.message.openExportModal();
                break;
            default:
                console.warn('Unknown command type:', command.type);
        }
    });
}

export default { render };