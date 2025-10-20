import * as code from './code.js';
import * as page from './page.js';
import * as search from './search.js';

/* Added so the DOMContentLoaded events work without any changes. */
document.addEventListener("turbo:load", function() {
  document.dispatchEvent(new CustomEvent("DOMContentLoaded"));
});

document.addEventListener('DOMContentLoaded', () => {
  code.ready();
  page.ready();
  search.ready();
});
