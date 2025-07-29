// See Bug #329
//import Cookies from './js.cookie.mjs';

/*! js-cookie v3.0.1 | MIT */
/* eslint-disable no-var */
function assign (target) {
  for (var i = 1; i < arguments.length; i++) {
    var source = arguments[i];
    for (var key in source) {
      target[key] = source[key];
    }
  }
  return target
}
/* eslint-enable no-var */

/* eslint-disable no-var */
var defaultConverter = {
  read: function (value) {
    if (value[0] === '"') {
      value = value.slice(1, -1);
    }
    return value.replace(/(%[\dA-F]{2})+/gi, decodeURIComponent)
  },
  write: function (value) {
    return encodeURIComponent(value).replace(
      /%(2[346BF]|3[AC-F]|40|5[BDE]|60|7[BCD])/g,
      decodeURIComponent
    )
  }
};
/* eslint-enable no-var */

/* eslint-disable no-var */

function init (converter, defaultAttributes) {
  function set (key, value, attributes) {
    if (typeof document === 'undefined') {
      return
    }

    attributes = assign({}, defaultAttributes, attributes);

    if (typeof attributes.expires === 'number') {
      attributes.expires = new Date(Date.now() + attributes.expires * 864e5);
    }
    if (attributes.expires) {
      attributes.expires = attributes.expires.toUTCString();
    }

    key = encodeURIComponent(key)
      .replace(/%(2[346B]|5E|60|7C)/g, decodeURIComponent)
      .replace(/[()]/g, escape);

    var stringifiedAttributes = '';
    for (var attributeName in attributes) {
      if (!attributes[attributeName]) {
        continue
      }

      stringifiedAttributes += '; ' + attributeName;

      if (attributes[attributeName] === true) {
        continue
      }

      // Considers RFC 6265 section 5.2:
      // ...
      // 3.  If the remaining unparsed-attributes contains a %x3B (";")
      //     character:
      // Consume the characters of the unparsed-attributes up to,
      // not including, the first %x3B (";") character.
      // ...
      stringifiedAttributes += '=' + attributes[attributeName].split(';')[0];
    }

    return (document.cookie =
      key + '=' + converter.write(value, key) + stringifiedAttributes)
  }

  function get (key) {
    if (typeof document === 'undefined' || (arguments.length && !key)) {
      return
    }

    // To prevent the for loop in the first place assign an empty array
    // in case there are no cookies at all.
    var cookies = document.cookie ? document.cookie.split('; ') : [];
    var jar = {};
    for (var i = 0; i < cookies.length; i++) {
      var parts = cookies[i].split('=');
      var value = parts.slice(1).join('=');

      try {
        var foundKey = decodeURIComponent(parts[0]);
        jar[foundKey] = converter.read(value, foundKey);

        if (key === foundKey) {
          break
        }
      } catch (e) {}
    }

    return key ? jar[key] : jar
  }

  return Object.create(
    {
      set: set,
      get: get,
      remove: function (key, attributes) {
        set(
          key,
          '',
          assign({}, attributes, {
            expires: -1
          })
        );
      },
      withAttributes: function (attributes) {
        return init(this.converter, assign({}, this.attributes, attributes))
      },
      withConverter: function (converter) {
        return init(assign({}, this.converter, converter), this.attributes)
      }
    },
    {
      attributes: { value: Object.freeze(defaultAttributes) },
      converter: { value: Object.freeze(converter) }
    }
  )
}

var api = init(defaultConverter, { path: '/' });
/* eslint-enable no-var */

export default api;



////////////////////////


/*! js-cookie v3.0.1 | MIT */
;
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
  typeof define === 'function' && define.amd ? define(factory) :
  (global = global || self, (function () {
    var current = global.Cookies;
    var exports = global.Cookies = factory();
    exports.noConflict = function () { global.Cookies = current; return exports; };
  }()));
}(this, (function () { 'use strict';

  /* eslint-disable no-var */
  function assign (target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        target[key] = source[key];
      }
    }
    return target
  }
  /* eslint-enable no-var */

  /* eslint-disable no-var */
  var defaultConverter = {
    read: function (value) {
      if (value[0] === '"') {
        value = value.slice(1, -1);
      }
      return value.replace(/(%[\dA-F]{2})+/gi, decodeURIComponent)
    },
    write: function (value) {
      return encodeURIComponent(value).replace(
        /%(2[346BF]|3[AC-F]|40|5[BDE]|60|7[BCD])/g,
        decodeURIComponent
      )
    }
  };
  /* eslint-enable no-var */

  /* eslint-disable no-var */

  function init (converter, defaultAttributes) {
    function set (key, value, attributes) {
      if (typeof document === 'undefined') {
        return
      }

      attributes = assign({}, defaultAttributes, attributes);

      if (typeof attributes.expires === 'number') {
        attributes.expires = new Date(Date.now() + attributes.expires * 864e5);
      }
      if (attributes.expires) {
        attributes.expires = attributes.expires.toUTCString();
      }

      key = encodeURIComponent(key)
        .replace(/%(2[346B]|5E|60|7C)/g, decodeURIComponent)
        .replace(/[()]/g, escape);

      var stringifiedAttributes = '';
      for (var attributeName in attributes) {
        if (!attributes[attributeName]) {
          continue
        }

        stringifiedAttributes += '; ' + attributeName;

        if (attributes[attributeName] === true) {
          continue
        }

        // Considers RFC 6265 section 5.2:
        // ...
        // 3.  If the remaining unparsed-attributes contains a %x3B (";")
        //     character:
        // Consume the characters of the unparsed-attributes up to,
        // not including, the first %x3B (";") character.
        // ...
        stringifiedAttributes += '=' + attributes[attributeName].split(';')[0];
      }

      return (document.cookie =
        key + '=' + converter.write(value, key) + stringifiedAttributes)
    }

    function get (key) {
      if (typeof document === 'undefined' || (arguments.length && !key)) {
        return
      }

      // To prevent the for loop in the first place assign an empty array
      // in case there are no cookies at all.
      var cookies = document.cookie ? document.cookie.split('; ') : [];
      var jar = {};
      for (var i = 0; i < cookies.length; i++) {
        var parts = cookies[i].split('=');
        var value = parts.slice(1).join('=');

        try {
          var foundKey = decodeURIComponent(parts[0]);
          jar[foundKey] = converter.read(value, foundKey);

          if (key === foundKey) {
            break
          }
        } catch (e) {}
      }

      return key ? jar[key] : jar
    }

    return Object.create(
      {
        set: set,
        get: get,
        remove: function (key, attributes) {
          set(
            key,
            '',
            assign({}, attributes, {
              expires: -1
            })
          );
        },
        withAttributes: function (attributes) {
          return init(this.converter, assign({}, this.attributes, attributes))
        },
        withConverter: function (converter) {
          return init(assign({}, this.converter, converter), this.attributes)
        }
      },
      {
        attributes: { value: Object.freeze(defaultAttributes) },
        converter: { value: Object.freeze(converter) }
      }
    )
  }

  var api = init(defaultConverter, { path: '/' });
  /* eslint-enable no-var */

  return api;

})));


////////////////////////
/*
 * TODO: See Feature 378. Refactor this day/night mode toggle to be simpler.
 * */
$(document).ready(function() {
	if(Cookies.get("mode") == -1) {
		$(".navbar").toggleClass("navbar-dark");
		$(".navbar").toggleClass("bg-dark");
		$(".nav-item").toggleClass("text-dark");
		$(".row").toggleClass("bg-dark");
		$(".detail-images").toggleClass("bg-dark");
		$(".detail-short").toggleClass("bg-dark");
		$(".detail-long").toggleClass("bg-dark");
		$(".detail-text").toggleClass("text-dark");
		$(".back-to-listings").toggleClass("bg-dark");
		$("body").toggleClass("bg-dark");
		$("h2").toggleClass("text-dark");
		$("p").toggleClass("text-dark");
		$("span").toggleClass("text-dark");
		var dayNightIconPath = $("#toggle-day-night-icon").attr("src");
		dayNightIconPath = dayNightIconPath.replace("night", "day");
		$("#toggle-day-night-icon").attr("src", dayNightIconPath);
		$("#toggle-day-night-icon").css({"filter": "invert(100%)"});
	}
});
$("#toggle-day-night").click(function() {
	var mode;
	var dayNightIconPath = $("#toggle-day-night-icon").attr("src");
	if(Cookies.get("mode") == undefined) {
		mode = 1;
		Cookies.set("mode", mode, {sameSite: "strict"});
	} else {
		mode = Cookies.get("mode");
	}
	$(".navbar").toggleClass("navbar-dark");
	$(".navbar").toggleClass("bg-dark");
	$(".nav-item").toggleClass("text-dark");
	$(".row").toggleClass("bg-dark");
	$(".detail-images").toggleClass("bg-dark");
	$(".detail-short").toggleClass("bg-dark");
	$(".detail-long").toggleClass("bg-dark");
	$(".detail-text").toggleClass("text-dark");
	$(".back-to-listings").toggleClass("bg-dark");
	$("body").toggleClass("bg-dark");
	$("h2").toggleClass("text-dark");
	$("p").toggleClass("text-dark");
	$("span").toggleClass("text-dark");
	if(mode == 1) {
		dayNightIconPath = dayNightIconPath.replace("night", "day");
	} else {
		dayNightIconPath = dayNightIconPath.replace("day", "night");
	}
	$("#toggle-day-night-icon").attr("src", dayNightIconPath);
	if(mode == 1) {
		$("#toggle-day-night-icon").css({"filter": "invert(100%)"});
	} else {
		$("#toggle-day-night-icon").css({"filter": "none"});
	}
	mode *= -1;
	Cookies.set("mode", mode, {sameSite: "strict"});
});

$(".form-toggle-field").change(function() {
	var model_type = $(this).val();
	if(model_type == "rental") {
		$(".rental-form-fields").removeClass("hidden-form-fields");
		$(".for-sale-form-fields").addClass("hidden-form-fields");
	} else if(model_type == "for_sale") {
		$(".rental-form-fields").addClass("hidden-form-fields");
		$(".for-sale-form-fields").removeClass("hidden-form-fields");
	} else {
		$(".rental-form-fields").removeClass("hidden-form-fields");
		$(".for-sale-form-fields").addClass("hidden-form-fields");
	}

});

$(".language-flag").click(function() {
	var id = $(this).attr('id');
	var language = id.split('-')[2];
	var url = document.URL;
	url = url.replaceAll(/&language=[a-zA-Z]+/g, "");
	if (url.indexOf('?') > -1)
		url += '&';
	else
		url += '?';
	url += 'language=' + language;
	window.location.replace(url);
});
