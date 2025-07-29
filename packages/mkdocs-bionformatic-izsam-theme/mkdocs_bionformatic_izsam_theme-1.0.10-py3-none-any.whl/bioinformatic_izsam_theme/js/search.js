wiki.search = {};

/* Get indexed docs
 * 
 * s_index is declared in search_docs.js built with mkdocs-izsam-search
 * 
 */
wiki.search.documents = s_index;
wiki.search.idx;

/* Get indexed configurations parameters
 * 
 * s_config is declared in search_docs.js built with mkdocs-izsam-search
 * 
 */
wiki.search.separator = s_config[0].separator;
wiki.search.minSearchLength = s_config[0].min_search_length;

wiki.search.getSearchTermFromLocation = function() {
  let sPageURL = window.location.search.substring(1);
  let sParameterName = sPageURL.split('=');
  if (sParameterName[0] == 'q') {
    return decodeURIComponent(sParameterName[1].replace(/\+/g, '%20'));
  }
}

wiki.search.joinUrl = function(base, path) {
  if (path.substring(0, 1) === "/") {
    // path starts with `/`. Thus it is absolute.
    return path;
  }
  if (base.substring(base.length-1) === "/") {
    // base ends with `/`
    return base + path;
  }
  return base + "/" + path;
}

wiki.search.formatResult = function(location, title, summary) {
  return '<article><h3><a href="' + wiki.search.joinUrl(base_url, location) + '">'+ title + '</a></h3><p class="location">' + location + '</p><p>' + summary +'</p></article>';
}

wiki.search.displayResults = function(results) {
  let searchResults = document.getElementById("mkdocs-search-results");
  if (searchResults) {
    searchResults.innerHTML = '';
  }
  if (results.length > 0){
    // compare object and return an object of matched elements
    let filteredResults = wiki.search.documents.filter(function (o1) {
      return results.some(function (o2) {
        return o1.location === o2.ref; // return the ones with equal location and ref
      });
    });
    // now we need to reorder the keys with the scores given in results object
    // first I will make the same order of the two matching objects
    let orderedResults = results.sort(function(a, b) {
       return a.ref.toLowerCase().localeCompare(b.ref);
    });
    let orderedFilteredResults = filteredResults.sort(function(a, b) {
       return a.location.toLowerCase().localeCompare(b.location);
    });
    // now I will assign the score to the filtered results
    function isEqual(object1, object2) {
      return object1.location === object2.ref;
    }
    orderedFilteredResults.forEach((result, index) => {
      if (isEqual( orderedFilteredResults, orderedResults)) {
        result.score = orderedResults[index].score;
      }
    });
    let sortedResults = orderedFilteredResults.sort(function(a, b) {
      return b.score - a.score;
    });
    sortedResults.forEach(result => {
      let summary = (result.text.substring(0, 200) + " [...]");
      let html = wiki.search.formatResult(result.location, result.title, summary);
      searchResults.insertAdjacentHTML('beforeend', html);
    });
  } else {
    let languages = wiki.locales.languages;
    let language = languages.find(element => element.active);
    let code = language ? language.code : 'en';
    let noResultsText = wiki.languages[code].search_page_no_results;
    searchResults.innerHTML = '<p>' + noResultsText + '</p>';
  }
}

wiki.search.doSearch = function() {
  let query = document.getElementById('mkdocs-search-query').value;
  if (query.length > wiki.search.minSearchLength) {
    wiki.search.displayResults(wiki.search.idx.search(query));
  } else {
    // Clear results for short queries
    wiki.search.displayResults([]);
  }
}

wiki.search.initSearch = function() {
  let searchInput = document.getElementById('mkdocs-search-query');
  if (searchInput) {
    searchInput.addEventListener("keyup", wiki.search.doSearch);
  }
  let term = wiki.search.getSearchTermFromLocation();
  if (term) {
    searchInput.value = term;
    wiki.search.doSearch();
  }
}

wiki.search.buildModalSearch = function() {
  let languages = wiki.locales.languages;
  let language = languages.find(element => element.active);
  let code = language ? language.code : 'en';
  let title = wiki.languages[code].search_within_the_wiki;
  let contents = [];
  let form = document.createElement('form');
  form.setAttribute('action', wiki.search.joinUrl(base_url, 'search.html'));
  form.setAttribute('method', 'get');
  let box = document.createElement('div');
  box.setAttribute('class', 'search-box');
  let input = document.createElement('input');
  input.setAttribute('id', 'modal-search');
  input.setAttribute('type', 'search');
  input.setAttribute('name', 'q');
  let placeholder = wiki.languages[code].use_keywords;
  input.setAttribute('placeholder', placeholder);
  box.append(input);
  form.append(box);
  let button = document.createElement('button');
  button.setAttribute('type', 'submit');
  button.setAttribute('disabled', '');
  button.innerHTML = wiki.languages[code].search;
  form.append(button);

  input.addEventListener('keyup', function(event) {
    let value = input.value;
    if (value.length > wiki.search.minSearchLength) {
      if (event.key === 'Enter') {
        form.submit();
      } else {
        button.removeAttribute('disabled');
      }
    } else {
      button.setAttribute('disabled', '');
    }
  });

  contents.push(form);
  let cfg = {
    title: title,
    contents: contents
  };
  
  wiki.modal.buildModal(cfg);
  
  setTimeout(function() {
    input.focus();
  }, 600);
}

/* Start the magic */
if (wiki.search.documents) {
  let lang = document.documentElement.lang;
  wiki.search.idx = lunr(function () {
    if (lang != 'en') {
      this.use(lunr.multiLanguage('en', lang))
    }
    this.ref('location')
    this.field('text')
    this.field('title')
    // we need to add to what lunr considers a token separator
    // this.tokenizer.separator = /[\s\-\_]+/
    this.tokenizer.separator = wiki.search.separator
    // if using the lunr.Index#search method to query then the
    // term separator also needs to be updated
    lunr.QueryLexer.termSeparator = lunr.tokenizer.separator
    wiki.search.documents.forEach(function (doc) {
      this.add(doc)
    }, this)
  });
  wiki.search.initSearch();
}
