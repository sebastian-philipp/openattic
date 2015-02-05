angular.module('openattic')
  .controller('VolumeNfsSharesCtrl', function ($scope, $stateParams, NfsSharesService) {
    $scope.nfsData = {};

    $scope.nfsFilter = {
      page: 0,
      entries: 10,
      search: '',
      sortfield: 'name',
      sortorder: 'ASC',
      volume: null
    };

    $scope.nfsSelection = {
    };

    $scope.$watch("selection.item", function(selitem){
      $scope.nfsFilter.volume = selitem;
    });

    $scope.$watch("nfsFilter", function(){
      if(!$scope.nfsFilter.volume) return;
      NfsSharesService.filter({
        page:      $scope.nfsFilter.page + 1,
        page_size: $scope.nfsFilter.entries,
        search:    $scope.nfsFilter.search,
        ordering:  $scope.nfsFilter.ordering,
        volume:    $scope.nfsFilter.volume.id
      })
      .$promise
      .then(function (res) {
        $scope.nfsData = res;
      })
      .catch(function (error) {
        console.log('An error occurred', error);
      });
    });
  });

// kate: space-indent on; indent-width 2; replace-tabs on;