import ckan.lib.datapreview as datapreview
import ckan.plugins as p

from dcor_shared import DC_MIME_TYPES, get_dc_instance


class DCLogViewPlugin(p.SingletonPlugin):
    """This plugin makes log views of DC data"""
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourceView, inherit=True)

    # IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('assets', 'dc_log_view')

    # IResourceView
    def info(self):
        return {'name': 'dc_log_view',
                'title': p.toolkit._('DC Logs'),
                'icon': 'microscope',
                'iframed': False,
                'always_available': True,
                'default_title': p.toolkit._('DC Logs'),
                }

    def can_view(self, data_dict):
        resource = data_dict['resource']
        mtype = resource.get('mimetype', '')
        same_domain = datapreview.on_same_domain(data_dict)
        if mtype in DC_MIME_TYPES and same_domain:
            return True
        else:
            return False

    def setup_template_variables(self, context, data_dict):
        # get the local resource location
        res_dict = data_dict['resource']
        # extract the logs
        logs = {}
        with get_dc_instance(res_dict["id"]) as ds:
            for key in ds.logs:
                logs[key] = ds.logs[key]
        return {"logs": logs}

    def view_template(self, context, data_dict):
        return 'dc_view_log.html'
