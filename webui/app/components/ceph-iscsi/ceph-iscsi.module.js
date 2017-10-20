/**
 *
 * @source: http://bitbucket.org/openattic/openattic
 *
 * @licstart  The following is the entire license notice for the
 *  JavaScript code in this page.
 *
 * Copyright (c) 2017 SUSE LLC
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

import cephIscsiDeleteModal from "./ceph-iscsi-delete-modal/ceph-iscsi-delete-modal.component";
import cephIscsiDetail from "./ceph-iscsi-detail/ceph-iscsi-detail.component";
import cephIscsiForm from "./ceph-iscsi-form/ceph-iscsi-form.component";
import cephIscsiFormImageSettingsModal from "./ceph-iscsi-form/ceph-iscsi-form-image-settings-modal.component";
import cephIscsiFormTargetSettingsModal from "./ceph-iscsi-form/ceph-iscsi-form-target-settings-modal.component";
import cephIscsiList from "./ceph-iscsi-list/ceph-iscsi-list.component";

angular.module("openattic.cephIscsi", [])
  .component("cephIscsiDeleteModal", cephIscsiDeleteModal)
  .component("cephIscsiDetail", cephIscsiDetail)
  .component("cephIscsiForm", cephIscsiForm)
  .component("cephIscsiFormImageSettingsModal", cephIscsiFormImageSettingsModal)
  .component("cephIscsiFormTargetSettingsModal", cephIscsiFormTargetSettingsModal)
  .component("cephIscsiList", cephIscsiList);

require("./ceph-iscsi.routes");
require("./shared/ceph-iscsi-image-advanged-settings.value");
require("./shared/ceph-iscsi-image-optional-settings.value");
require("./shared/ceph-iscsi-target-advanged-settings.value");
require("./shared/ceph-iscsi.service");
