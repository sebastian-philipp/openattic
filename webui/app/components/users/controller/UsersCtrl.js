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

var app = angular.module("openattic.users");
app.controller("UsersCtrl", function ($scope, $state, usersService, $uibModal) {
  $scope.data = {};

  $scope.filterConfig = {
    page: 0,
    entries: null,
    search: "",
    sortfield: null,
    sortorder: null
  };

  $scope.selection = {};

  $scope.$watch("filterConfig", function (newVal) {
    if (newVal.entries === null) {
      return;
    }
    usersService.filter({
      page: $scope.filterConfig.page + 1,
      pageSize: $scope.filterConfig.entries,
      search: $scope.filterConfig.search,
      ordering: ($scope.filterConfig.sortorder === "ASC" ? "" : "-") + $scope.filterConfig.sortfield
    })
      .$promise
      .then(function (res) {
        $scope.data = res;
      });
  }, true);

  $scope.$watchCollection("selection.item", function (item) {
    $scope.hasSelection = Boolean(item);
  });

  $scope.addAction = function () {
    $state.go("users-add");
  };

  $scope.editAction = function () {
    $state.go("users-edit", {user: $scope.selection.item.id});
  };

  $scope.deleteAction = function () {
    var modalInstance = $uibModal.open({
      windowTemplate: require("../../../templates/messagebox.html"),
      template: require("../templates/delete-user.html"),
      controller: "UsersDeleteCtrl",
      resolve: {
        user: function () {
          return $scope.selection.item;
        }
      }
    });
    modalInstance.result.then(function () {
      $scope.filterConfig.refresh = new Date();
    });
  };
});