# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Remote user security manager."""

from flask_appbuilder.security.manager import AUTH_REMOTE_USER

from superset.security.manager import SupersetSecurityManager


class CustomSecurityManager(SupersetSecurityManager):
    """Security manager that uses :class:`AuthRemoteUserView`."""

    def register_views(self) -> None:  # type: ignore[override]
        """Register the appropriate authentication views."""
        if self.auth_type == AUTH_REMOTE_USER:
            from superset.views.auth import AuthRemoteUserView, SupersetRegisterUserView

            self.auth_view = self.appbuilder.add_view_no_menu(AuthRemoteUserView)
            self.registeruser_view = self.appbuilder.add_view_no_menu(
                SupersetRegisterUserView
            )
            super().register_views()
        else:
            super().register_views()
