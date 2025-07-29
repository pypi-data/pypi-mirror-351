from topdesk_mcp import _utils
import re
import logging

class incident:

    def __init__(self, topdesk_url, credpair):
        self._topdesk_url = topdesk_url
        self._credpair = credpair
        self.utils = _utils.utils(self._topdesk_url, self._credpair)
        self.action = self._action(self._topdesk_url, self._credpair)
        self.request = self._request(self._topdesk_url, self._credpair)
        self.timespent = self._timespent(self._topdesk_url, self._credpair)
        self.attachments = self._attachments(self._topdesk_url, self._credpair)
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Incident class initialized with URL: %s", self._topdesk_url)
        self._logger.debug("Incident class initialized with credentials: %s", self._credpair)

    def get(self, incident):
        if self.utils.is_valid_uuid(incident):
            return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}".format(incident)))
        else:
            return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}".format(incident)))

    def deescalate(self, incident, reason_id=None):
        if reason_id:
            param = {'id': reason_id}
        if self.utils.is_valid_uuid(incident):    
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/id/{}/deescalate".format(incident), param))
        else:
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/number/{}/deescalate".format(incident), param))

    def escalate(self, incident, reason_id=None):
        if reason_id:
            param = {'id': reason_id}
        if self.utils.is_valid_uuid(incident):    
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/id/{}/escalate".format(incident), param))
        else:
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/number/{}/escalate".format(incident), param))

    def get_progress_trail(self, incident, inlineimages=False, non_api_attachments_url=False, force_images_as_data=False, page_size=100):
        ext_uri= { 'inlineimages': inlineimages, 'non_api_attachments_url': non_api_attachments_url, 'force_images_as_data': force_images_as_data }
        if self.utils.is_valid_uuid(incident):
            return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/progresstrail".format(incident), page_size=page_size, extended_uri=ext_uri))
        else:
            return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}/progresstrail".format(incident), page_size=page_size, extended_uri=ext_uri))
        
    def patch(self, incident, **kwargs):
        if self.utils.is_valid_uuid(incident):
            return self.utils.handle_topdesk_response(self.utils.patch_to_topdesk("/tas/api/incidents/id/{}".format(incident), self.utils.add_id_jsonbody(**kwargs)))
        else:
            return self.utils.handle_topdesk_response(self.utils.patch_to_topdesk("/tas/api/incidents/number/{}".format(incident), self.utils.add_id_jsonbody(**kwargs)))

    class _action:
        
        def __init__(self, topdesk_url, credpair):
            self._topdesk_url = topdesk_url
            self._credpair = credpair
            self.utils = _utils.utils(self._topdesk_url, self._credpair)
            self._logger = logging.getLogger(__name__)
            self._logger.debug("TOPdesk API action object initialised.")

        def get_list(self, incident, inlineimages=False, non_api_attachments_url=False, page_size=100):
            ext_uri= { 'inlineimages': inlineimages, 'non_api_attachments_url': non_api_attachments_url }
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/actions".format(incident), page_size=page_size, extended_uri=ext_uri))
            else:
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}/actions".format(incident), page_size=page_size, extended_uri=ext_uri))

        def get(self, incident, actions_id, inlineimages=False, non_api_attachments_url=False):
            ext_uri= { 'inlineimages': inlineimages, 'non_api_attachments_url': non_api_attachments_url }
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/actions/{}".format(incident, actions_id), page_size=10, extended_uri=ext_uri))
            else:
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}/actions/{}".format(incident, actions_id), page_size=10, extended_uri=ext_uri))

        def delete(self, incident, actions_id):
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.delete_from_topdesk("/tas/api/incidents/id/{}/actions/{}".format(incident, actions_id), None))
            else:
                return self.utils.handle_topdesk_response(self.utils.delete_from_topdesk("/tas/api/incidents/number/{}/actions/{}".format(incident, actions_id), None))

    class _request:

        def __init__(self, topdesk_url, credpair):
            self._topdesk_url = topdesk_url
            self._credpair = credpair
            self.utils = _utils.utils(self._topdesk_url, self._credpair)
            self._logger = logging.getLogger(__name__)
            self._logger.debug("TOPdesk API request object initialised.")

        def get_list(self, incident, inlineimages=False, non_api_attachments_url=False, page_size=100):
            ext_uri= { 'inlineimages': inlineimages, 'non_api_attachments_url': non_api_attachments_url }
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/requests".format(incident), page_size=page_size, extended_uri=ext_uri))
            else:
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}/requests".format(incident), page_size=page_size, extended_uri=ext_uri))

        def get(self, incident, request_id, inlineimages=False, non_api_attachments_url=False):
            ext_uri= { 'inlineimages': inlineimages, 'non_api_attachments_url': non_api_attachments_url }
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/actions/{}".format(incident, request_id), page_size=10, extended_uri=ext_uri))
            else:
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}/actions/{}".format(incident, request_id), page_size=10, extended_uri=ext_uri))

        def delete(self, incident, request_id):
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.delete_from_topdesk("/tas/api/incidents/id/{}/actions/{}".format(incident, request_id), None))
            else:
                return self.utils.handle_topdesk_response(self.utils.delete_from_topdesk("/tas/api/incidents/number/{}/actions/{}".format(incident, request_id), None))

    class _timespent:

        def __init__(self, topdesk_url, credpair):
            self._topdesk_url = topdesk_url
            self._credpair = credpair
            self.utils = _utils.utils(self._topdesk_url, self._credpair)
            self._logger = logging.getLogger(__name__)
            self._logger.debug("TOPdesk API timespent object initialised.")

        def get(self, incident):
            if self.utils.is_valid_uuid(incident):    
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/timespent".format(incident)))
            else:
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}/timespent".format(incident)))

        def register(self, incident, timespent, **kwargs):
            param = {}
            if kwargs:
                param = kwargs 
            param['timespent'] =  timespent            
            if self.utils.is_valid_uuid(incident):    
                return self.utils.handle_topdesk_response(self.utils.post_to_topdesk("/tas/api/incidents/id/{}/timespent".format(incident), param))
            else:
                return self.utils.handle_topdesk_response(self.utils.post_to_topdesk("/tas/api/incidents/number/{}/timespent".format(incident), param))

    class _attachments:
        def __init__(self, topdesk_url, credpair):
            self._topdesk_url = topdesk_url
            self._credpair = credpair
            self.utils = _utils.utils(self._topdesk_url, self._credpair)
            self._logger = logging.getLogger(__name__)
            self._logger.debug("TOPdesk API attachments object initialised.")

        def get_list(self, incident, inlineimages=False, non_api_attachments_url=False, page_size=100):
            ext_uri= { 'inlineimages': inlineimages, 'non_api_attachments_url': non_api_attachments_url }
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/attachments".format(incident), page_size=page_size, extended_uri=ext_uri))
            else:
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/number/{}/attachments".format(incident), page_size=page_size, extended_uri=ext_uri))

        def download_attachments(self, incident):
            attachment_list = self.get_list(incident)
            attachment_data_list = []
            for attachment in attachment_list:
                attachment_json = self.utils.handle_topdesk_response(self.utils.request_topdesk(attachment['downloadUrl']))
                attachment_json['person']=attachment['person']
                attachment_data_list.append(attachment_json)
            return attachment_data_list

        def download_attachment(self, incident, attachment_id):
            if self.utils.is_valid_uuid(incident):
                return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/id/{}/attachments/{}/download".format(incident, attachment_id)))
            else:
                raise ValueError("Incident UUID is required to download an attachment. Incident numbers do not work.")

    def durations(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/durations"))

    def statuses(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/statuses"))

    def deescalation_reasons(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/deescalation-reasons"))
    
    def escalation_reasons(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/escalation-reasons"))
    
    def service_windows(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/slas/services"))

    def call_types(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/call_types"))

    def closure_codes(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/closure_codes"))

    def entry_types(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/entry_types"))

    def categorys(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/categories"))

    def subcategorys(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/subcategories"))

    def impacts(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/impacts"))

    def priorities(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/priorities"))

    def urgencies(self):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/urgencies"))

    def get_id_impact(self, query):
        result = self.impacts()
        canidates = list()
        for impact in result:
            if re.match(rf"(.+)?{query}(.+)?", impact['name'], re.IGNORECASE):
                canidates.append(impact['id'])

        return self.utils.resolve_lookup_candidates(canidates)

    def get_id_priority(self, query):
        result = self.priorities()
        canidates = list()
        for priority in result:
            if re.match(rf"(.+)?{query}(.+)?", priority['name'], re.IGNORECASE):
                canidates.append(priority['id'])

        return self.utils.resolve_lookup_candidates(canidates)

    def get_id_urgency(self, query):
        result = self.urgencies()
        canidates = list()
        for urgency in result:
            if re.match(rf"(.+)?{query}(.+)?", urgency['name'], re.IGNORECASE):
                canidates.append(urgency['id'])

        return self.utils.resolve_lookup_candidates(canidates)

    def get_id_entryType(self, query):
        result = self.entry_types()
        canidates = list()
        for entryType in result:
            if re.match(rf"(.+)?{query}(.+)?", entryType['name'], re.IGNORECASE):
                canidates.append(entryType['id'])

        return self.utils.resolve_lookup_candidates(canidates)

    def get_id_callType(self, query):
        result = self.call_types()
        canidates = list()
        for callType in result:
            if re.match(rf"(.+)?{query}(.+)?", callType['name'], re.IGNORECASE):
                canidates.append(callType['id'])

        return self.utils.resolve_lookup_candidates(canidates)

    def get_id_duration(self, query):
        result = self.durations()
        canidates = list()
        for callType in result:
            if re.match(rf"(.+)?{query}(.+)?", callType['name'], re.IGNORECASE):
                canidates.append(callType['id'])

        return self.utils.resolve_lookup_candidates(canidates)
    
    def create(self, caller, **kwargs):
        # Caller can be: email, uuid or unregisted user. We'll try it in that order.
        create_body = kwargs
        create_body['caller'] = caller     
        return self.utils.handle_topdesk_response(self.utils.post_to_topdesk("/tas/api/incidents/", self.utils.add_id_jsonbody(**create_body)))

    def update(self, incident, **kwargs):
        if self.utils.is_valid_uuid(incident):
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/id/{}".format(incident), self.utils.add_id_jsonbody(**kwargs)))
        else:            
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/number/{}".format(incident), self.utils.add_id_jsonbody(**kwargs)))

    def archive(self, incident, reason_id=None):
        if reason_id:
            param = {'id': reason_id}
        if self.utils.is_valid_uuid(incident):    
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/id/{}/archive".format(incident), param))
        else:
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/number/{}/archive".format(incident), param))

    def unarchive(self, incident):
        if self.utils.is_valid_uuid(incident):
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/id/{}/unarchive".format(incident), None))
        else:
            return self.utils.handle_topdesk_response(self.utils.put_to_topdesk("/tas/api/incidents/number/{}/unarchive".format(incident), None))

    def get_list(self, archived=False, page_size=100, query=None, **kwargs):
        return self.utils.handle_topdesk_response(self.utils.request_topdesk("/tas/api/incidents/", archived, page_size=page_size, query=query, extended_uri=kwargs))
