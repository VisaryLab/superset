from flask_appbuilder.api import expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access

from superset.constants import MODEL_VIEW_RW_METHOD_PERMISSION_MAP, RouteMethod
from superset.superset_typing import FlaskResponse
from superset.views.base import DeleteMixin, SupersetModelView

from superset.report_templates.models import ReportTemplate

class ReportTemplateModelView(  # pylint: disable=too-many-ancestors
    SupersetModelView,
    DeleteMixin,
):
    """
    Страница /report_template/list/
    """
	
    datamodel = SQLAInterface(ReportTemplate)

    route_base = "/report_template"                # даст /report_template/...
    include_route_methods = RouteMethod.LIST       # только list-роут

    # Имена для системы прав
    class_permission_name = "ReportTemplate"
    method_permission_name = MODEL_VIEW_RW_METHOD_PERMISSION_MAP

    @expose("/list/")
    @has_access
    def list(self) -> FlaskResponse:
        # Вернёт общий шаблон приложения
        return super().render_app_template()
