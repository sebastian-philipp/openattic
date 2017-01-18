/**
 *
 * @source: http://bitbucket.org/openattic/openattic
 *
 * @licstart  The following is the entire license notice for the
 *  JavaScript code in this page.
 *
 * Copyright (C) 2011-2016, it-novum GmbH <community@openattic.org>
 *
 *
 * The JavaScript code in this page is free software: you can
 * redistribute it and/or modify it under the terms of the GNU
 * General Public License as published by the Free Software
 * Foundation; version 2.
 *
 * This package is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * As additional permission under GNU GPL version 2 section 3, you
 * may distribute non-source (e.g., minimized or compacted) forms of
 * that code without the copy of the GNU GPL normally required by
 * section 1, provided you include this license notice and a URL
 * through which recipients can access the Corresponding Source.
 *
 * @licend  The above is the entire license notice
 * for the JavaScript code in this page.
 *
 */
"use strict";

var app = angular.module("openattic.datatable");
app.directive("actions", function () {
  return {
    restrict: "E",
    templateUrl: "components/datatable/templates/actionmenu.html",
    transclude: true,
    link: function (scope, element, attr, controller, transclude) {
      var dropdown = element.find(".oa-dropdown-actions");
      var actionsscope = scope.$parent.$new();

      $(dropdown.parent()).on({
        "show.bs.dropdown": function () {
          this.closeable = true;
        },
        "click": function (e) {
          var parentTarget = $(e.target).parent();
          this.closeable= parentTarget.is(":not(ul.dropdown-menu,li.disabled)");
        },
        "hide.bs.dropdown": function () {
          return this.closeable;
        }
      });

      transclude(actionsscope, function (clone) {
        var i;
        var liElems = clone.filter("li");
        for (i = 0; i < liElems.length; i++) {
          element.find(".oa-dropdown-actions").append(liElems[i]);
        }
        var aElems = clone.filter(".btn-primary");
        for (i = aElems.length - 1; i >= 0; --i) {
          element.find(".btn-group").prepend(aElems[i]);
        }
      });
    }
  };
});
